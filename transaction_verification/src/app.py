import sys
import os
from datetime import datetime
from google.protobuf.json_format import MessageToDict

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "transaction_verification"})))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://observability:4318/v1/traces"))
trace.get_tracer_provider().add_span_processor(span_processor)

metrics.set_meter_provider(MeterProvider(resource=Resource.create({"service.name": "transaction_verification"})))
meter = metrics.get_meter(__name__)
metric_exporter = OTLPMetricExporter(endpoint="http://observability:4318/v1/metrics")

verification_counter = meter.create_counter("verification_count", description="Counts verification attempts")
verification_status = meter.create_up_down_counter("verification_status", description="Counts active verifications")
verification_latency = meter.create_histogram("verification_latency", description="Verification latency")

active_verifications_count = 0

def get_active_verifications():
    global active_verifications_count
    return active_verifications_count

active_verifications = meter.create_observable_gauge("active_verifications", callbacks=[get_active_verifications])

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, utils_path)
from fraud_detection import fraud_detection_pb2 as fraud_detection
from fraud_detection import fraud_detection_pb2_grpc as fraud_detection_grpc
from transaction_verification import transaction_verification_pb2 as transaction_verification
from transaction_verification import transaction_verification_pb2_grpc as transaction_verification_grpc

from concurrent import futures
import grpc

# Set the server index for the vector clock.
# Frontend: 0, Orchestrator: 1, TransactionVerification: 2, FraudDetection: 3, BookSuggestion: 4
SERVER_INDEX = 2
NUM_SERVERS = 5
LOCAL_VC_CORRECT_AFTER_ORCHESTRATOR = [0, 0, 0, 0, 0]
VC_CORRECT_AFTER_ORCHESTRATOR = [0, 1, 0, 0, 0]
LOCAL_VC_CORRECT_AFTER_ITEM_VERIFICATION = [0, 0, 1, 0, 0]
VC_CORRECT_AFTER_ITEM_VERIFICATION = [0, 1, 1, 0, 0]
LOCAL_VC_CORRECT_AFTER_USERDATA_FRAUD_DETECTION = [0, 0, 2, 0, 0]
VC_CORRECT_AFTER_USERDATA_FRAUD_DETECTION = [0, 1, 2, 1, 0]

# Create the global local vector clock.
local_vector_clock = {}

# Transaction flow check by order id.
order_id_from_orchestrator = ""

def userdata_fraud_detection_service(data, vector_clock):
     with tracer.start_as_current_span("userdata_fraud_detection_service") as span:
        span.set_attribute("service", "fraud_detection")
        with grpc.insecure_channel('fraud_detection:50051') as channel:
            stub = fraud_detection_grpc.UserdataFraudDetectionServiceStub(channel)
            attr = MessageToDict(data)
            attr["vectorClock"] = vector_clock
            response = stub.DetectUserdataFraud(fraud_detection.UserdataFraudDetectionRequest(**attr))
            return response

def cardinfo_fraud_detection_service(data, vector_clock):
    with tracer.start_as_current_span("cardinfo_fraud_detection_service") as span:
        span.set_attribute("service", "fraud_detection")
        with grpc.insecure_channel('fraud_detection:50051') as channel:
            stub = fraud_detection_grpc.CardinfoFraudDetectionServiceStub(channel)
            attr = MessageToDict(data)
            attr["vectorClock"] = vector_clock
            response = stub.DetectCardinfoFraud(fraud_detection.CardinfoFraudDetectionRequest(**attr))
            return response
    
# Increment the value in the server index, and update the timestamp.
# If the index isn't in the vc_array, append 0 until the index.
def increment_vector_clock(vector_clock):
    vc_array = [0 for _ in range(NUM_SERVERS)] if not "vcArray" in vector_clock else vector_clock["vcArray"]
    timestamp = datetime.now().timestamp()

    vc_array[SERVER_INDEX] += 1

    return {"vcArray": vc_array, "timestamp": timestamp}

class OrderIdStorageService(transaction_verification_grpc.OrderIdStorageServiceServicer):
    
    def StorageOrderId(self, request, context):
        global order_id_from_orchestrator
        verification_counter.add(1, {"operation": "store_order_id"})
        order_id_from_orchestrator = request.orderId
        return transaction_verification.OrderIdStorageResponse(isValid=True)

class ItemAndUserdataVerificationService(transaction_verification_grpc.ItemAndUserdataVerificationServiceServicer):

    def check_order_id(self, order_id):
        is_valid = (order_id_from_orchestrator == order_id)
        return is_valid

    def check_vc_after_orchestrator(self, vector_clock, local_vector_clock):
        request_vc_check = bool(vector_clock['vcArray'] == VC_CORRECT_AFTER_ORCHESTRATOR)
        local_vc_check = bool(local_vector_clock['vcArray'] == LOCAL_VC_CORRECT_AFTER_ORCHESTRATOR)
        timestamp_check = bool(vector_clock['timestamp'] < datetime.now().timestamp())
        return request_vc_check and local_vc_check and timestamp_check
    
    def check_vc_after_item_verification(self, vector_clock, local_vector_clock):
        request_vc_check = bool(vector_clock['vcArray'] == VC_CORRECT_AFTER_ITEM_VERIFICATION)
        local_vc_check = bool(local_vector_clock['vcArray'] == LOCAL_VC_CORRECT_AFTER_ITEM_VERIFICATION)
        timestamp_check = bool(vector_clock['timestamp'] < datetime.now().timestamp())
        return request_vc_check and local_vc_check and timestamp_check
    
    def VerifyItemAndUserdata(self, request, context):
        global local_vector_clock
        global active_verifications_count
        start_time = datetime.now()
        with tracer.start_as_current_span("verify_item_and_userdata") as span:
            span.set_attribute("order_id", request.orderId)
            verification_counter.add(1, {"operation": "verify_item_and_userdata"})
            verification_status.add(1)
            active_verifications_count += 1 
            local_vector_clock = {"vcArray": [0 for _ in range(NUM_SERVERS)], "timestamp": datetime.now().timestamp()}
            print("Transaction verification request received")
            print(f"[Transaction verification] Server index: {SERVER_INDEX}")
            
            error_response = lambda error_message: {
                "isValid": False,
                "errorMessage": error_message,
                "books": None
            }
            
            vector_clock = MessageToDict(request.vectorClock)
            user = request.user
            item = request.item
            order_id = request.orderId

            ### Order Id Confirm ------------------------------------
            if not self.check_order_id(order_id):
                error_message = "Server Error. Please retry later."
                verification_status.add(-1)
                active_verifications_count -= 1
                return transaction_verification.ItemAndUserdataVerificationResponse(**error_response(error_message))

            print('[Transaction verification] Order Id is confirmed.')
                
            ### Vector Clock Confirm ------------------------------------
            print(local_vector_clock)
            if not self.check_vc_after_orchestrator(vector_clock, local_vector_clock):
                error_message = "Server Error. Please retry later."
                verification_status.add(-1)
                active_verifications_count -= 1
                return transaction_verification.ItemAndUserdataVerificationResponse(**error_response(error_message))
            
            print('[Transaction verification] VC is correct after orchestrator.')

            ### a: order items empty? -----------------------------------
            item_exist = bool(item.name) and (item.quantity > 0)
            if not item_exist:
                error_message = "Transaction Invalid. Couldn't verify your order information."
                verification_status.add(-1)
                active_verifications_count -= 1 
                return transaction_verification.ItemAndUserdataVerificationResponse(**error_response(error_message))
            
            local_vector_clock = increment_vector_clock(local_vector_clock)
            vector_clock = increment_vector_clock(vector_clock)
            print(f"[Transaction verification] VCArray updated (item exists) in Transaction verification: {vector_clock['vcArray']}")
            # print(f"[Transaction verification] Timestamp updated (item exists) in Transaction verification: {vector_clock['timestamp']}")

            ### Vector Clock Confirm ------------------------------------
            if not self.check_vc_after_item_verification(vector_clock, local_vector_clock):
                error_message = "Server Error. Please retry later."
                verification_status.add(-1)
                active_verifications_count -= 1
                return transaction_verification.ItemAndUserdataVerificationResponse(**error_response(error_message))

            print('[Transaction verification] VC is correct after item verification.')

            ### b: user data filled? -----------------------------------
            user_data_filled = bool(user.name and user.contact)
            if not user_data_filled:
                error_message = "Transaction Invalid. Couldn't verify your user information."
                verification_status.add(-1)
                active_verifications_count -= 1
                return transaction_verification.ItemAndUserdataVerificationResponse(**error_response(error_message))
            
            local_vector_clock = increment_vector_clock(local_vector_clock)
            vector_clock = increment_vector_clock(vector_clock)
            print(f"[Transaction verification] VCArray updated (userdata exists) in Transaction verification: {vector_clock['vcArray']}")
            # print(f"[Transaction verification] Timestamp updated (userdata exists) in Transaction verification: {vector_clock['timestamp']}")
                    
            print(f"[Transaction verification] Item and Userdata verification response: Valid")
            with futures.ThreadPoolExecutor() as executor:
                userdata_fraud_future = executor.submit(userdata_fraud_detection_service, request, vector_clock)
            message = userdata_fraud_future.result()
            response = MessageToDict(message)
            end_time = datetime.now()
            verification_latency.record((end_time - start_time).total_seconds(), {"operation": "verify_item_and_userdata"})
            verification_status.add(-1)
            active_verifications_count -= 1 
            return transaction_verification.ItemAndUserdataVerificationResponse(**response)
        
    
class CardinfoVerificationService(transaction_verification_grpc.CardinfoVerificationServiceServicer):

    def check_order_id(self, order_id):
        is_valid = (order_id_from_orchestrator == order_id)
        return is_valid

    def check_vc_after_usredata_fraud_detection(self, vector_clock, local_vector_clock):
        request_vc_check = bool(vector_clock['vcArray'] == VC_CORRECT_AFTER_USERDATA_FRAUD_DETECTION)
        local_vc_check = bool(local_vector_clock['vcArray'] == LOCAL_VC_CORRECT_AFTER_USERDATA_FRAUD_DETECTION)
        timestamp_check = bool(vector_clock['timestamp'] < datetime.now().timestamp())
        return request_vc_check and local_vc_check and timestamp_check
    
    def is_creditcard_valid(self, credit_card):
        card_number = credit_card.number
        card_expiration_date = credit_card.expirationDate
        card_cvv = credit_card.cvv
        
        is_valid_date = True
        if "/" not in card_expiration_date:
            is_valid_date = False
        else:
            mm, yy = card_expiration_date.split("/")
            is_valid_date = (mm.isdigit() and int(mm) > 0 and int(mm) <= 12) and (yy.isdigit() and int(yy) > 23 and int(yy) < 50)

        is_correct_card_format = is_valid_date and ((len(card_number) >= 10 and len(card_number) <= 19) and card_number.isdigit()) \
            and ((len(card_cvv) == 3 or len(card_cvv) == 4) and card_cvv.isdigit())

        return is_correct_card_format
    
    def VerifyCardinfo(self, request, context):
        global local_vector_clock
        start_time = datetime.now()
        with tracer.start_as_current_span("verify_cardinfo") as span:
            span.set_attribute("order_id", request.orderId)
            verification_counter.add(1, {"operation": "verify_cardinfo"})
            verification_status.add(1)
            print("Transaction verification request received")
            print(f"[Transaction verification] Server index: {SERVER_INDEX}")

            error_response = lambda error_message: {
                "isValid": False,
                "errorMessage": error_message,
                "books": None
            }

            vector_clock = MessageToDict(request.vectorClock)
            credit_card = request.creditCard
            order_id = request.orderId

            ### Order Id Confirm ------------------------------------
            if not self.check_order_id(order_id):
                error_message = "Server Error. Please retry later."
                verification_status.add(-1)
                return transaction_verification.CardinfoVerificationResponse(**error_response(error_message))

            print('[Transaction verification] Order Id is confirmed.')

            ### Order Id Confirm ------------------------------------
            if not self.check_vc_after_usredata_fraud_detection(vector_clock, local_vector_clock):
                error_message = "Server Error. Please retry later."
                verification_status.add(-1)
                return transaction_verification.CardinfoVerificationResponse(**error_response(error_message))

            print('[Transaction verification] VC is correct after userdata fraud detection.')

            ### c: card info is correct format? -------------------------------
            is_creditcard_valid = self.is_creditcard_valid(credit_card)
            if not is_creditcard_valid:
                error_message = "Transaction Invalid. Couldn't verify your payment details."
                verification_status.add(-1)
                return transaction_verification.CardinfoVerificationResponse(**error_response(error_message))
            
            local_vector_clock = increment_vector_clock(local_vector_clock)
            vector_clock = increment_vector_clock(vector_clock)
            print(f"[Transaction verification] VCArray updated (valid creditcard) in Transaction verification: {vector_clock['vcArray']}")
            # print(f"[Transaction verification] Timestamp updated (valid creditcard) in Transaction verification: {vector_clock['timestamp']}")

            
            print(f"[Transaction verification] cardinfo verification response: Valid")
            with futures.ThreadPoolExecutor() as executor:
                cardinfo_fraud_future = executor.submit(cardinfo_fraud_detection_service, request, vector_clock)
            message = cardinfo_fraud_future.result()
            response = MessageToDict(message)
            end_time = datetime.now()
            verification_latency.record((end_time - start_time).total_seconds(), {"operation": "verify_cardinfo"})
            verification_status.add(-1)
            return transaction_verification.CardinfoVerificationResponse(**response)

    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    transaction_verification_grpc.add_OrderIdStorageServiceServicer_to_server(OrderIdStorageService(), server)
    transaction_verification_grpc.add_ItemAndUserdataVerificationServiceServicer_to_server(ItemAndUserdataVerificationService(), server)
    transaction_verification_grpc.add_CardinfoVerificationServiceServicer_to_server(CardinfoVerificationService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Transaction Verification Service started on port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
