import sys
import os
from datetime import datetime
import queue
import time

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "order_executor"})))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://observability:4318/v1/traces"))
trace.get_tracer_provider().add_span_processor(span_processor)

metrics.set_meter_provider(MeterProvider(resource=Resource.create({"service.name": "order_executor"})))
meter = metrics.get_meter(__name__)
metric_exporter = OTLPMetricExporter(endpoint="http://observability:4318/v1/metrics")

order_counter = meter.create_counter("order_count", description="Counts processed orders")
order_status = meter.create_up_down_counter("order_status", description="Counts active orders")
request_latency = meter.create_histogram("request_latency", description="Request latency")


active_orders_count = 0

def get_active_orders():
    global active_orders_count
    return active_orders_count

active_orders = meter.create_observable_gauge("active_orders", callbacks=[get_active_orders])


# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, utils_path)

from order_queue import order_queue_pb2 as order_queue
from order_queue import order_queue_pb2_grpc as order_queue_grpc
from order_executor import order_executor_pb2 as order_executor
from order_executor import order_executor_pb2_grpc as order_executor_grpc
from book_database import book_database_pb2 as book_database
from book_database import book_database_pb2_grpc as book_database_grpc
from payment_executor import payment_executor_pb2 as payment_executor
from payment_executor import payment_executor_pb2_grpc as payment_executor_grpc
from book_database import book_database_pb2 as book_database
from book_database import book_database_pb2_grpc as book_database_grpc

import grpc
from concurrent import futures

import socket

replica_id = int(os.getenv('REPLICA_ID', '0'))  # Gets the ID of the current replica from the environment.
print(f"My ID is: {replica_id}")
total_replicas = int(os.getenv('TOTAL_REPLICAS', '6'))

def dequeue():
    # Access the order queue to dequeue.
    with tracer.start_as_current_span("dequeue_order") as span:
        span.set_attribute("replica_id", replica_id)
        with grpc.insecure_channel('order_queue:50054') as channel:
                print(f"Replica {replica_id} has accessed the queue")
                stub = order_queue_grpc.OrderQueueServiceStub(channel)
                response = stub.Dequeue(order_queue.DequeueRequest())

        return response

def send_vote_request_to_payment_executor():
    with tracer.start_as_current_span("vote_request_payment_executor") as span:
        print(f"Order Executor-{replica_id}: Phase 1a - Sending vote request to Payment Executor.")
        with grpc.insecure_channel('payment_executor:50059') as channel:
            stub = payment_executor_grpc.PaymentExecutorServiceStub(channel)
            response = stub.SendVoteToCoordinator(payment_executor.VoteCommitRequest())
            return response.success
    
def send_vote_request_to_book_database():
    with tracer.start_as_current_span("vote_request_book_database") as span:
        print(f"Order Executor-{replica_id}: Phase 1a - Sending vote request to Book Database.")
        with grpc.insecure_channel('book_database_1:50056') as channel:
            stub = book_database_grpc.BookDatabaseServiceStub(channel)
            response = stub.SendVoteToCoordinator(book_database.VoteCommitRequest())
            return response.success
    
def send_execute_request_to_payment_executor(global_commit):
    with tracer.start_as_current_span("execute_request_payment_executor") as span:
        span.set_attribute("global_commit", global_commit)
        with grpc.insecure_channel('payment_executor:50059') as channel:
            stub = payment_executor_grpc.PaymentExecutorServiceStub(channel)
            response = stub.ExecutePayment(payment_executor.PaymentExecutionRequest(commitStatus=global_commit))
            return response.success
    
def send_execute_request_to_book_database(global_commit, item):
    with tracer.start_as_current_span("execute_request_book_database") as span:
        span.set_attribute("global_commit", global_commit)
        delaytime = {"1": 0, "2": 20, "3": 20, "4": 20, "5": 20, "6": 20}
        print(f'[Orcer Executor] Book Id is {item.book.id}. Add a delay time {delaytime[item.book.id]}')
        time.sleep(delaytime[item.book.id])
        print(f'[Order Executor] Send request of getting the book data. requesting book_id is {item.book.id}')
        with grpc.insecure_channel('book_database_1:50056') as channel:
            stub = book_database_grpc.BookDatabaseServiceStub(channel)
            book = stub.GetBook(book_database.GetBookRequest(
                request_id=item.book.id, # Learning Python (String)
                commitStatus=global_commit
            ), global_commit)

        if book and book.copiesAvailable >= item.quantity:
            book.copiesAvailable -= item.quantity
            # Change the available counts.
            print(f'[Order Executor] Changed the copiedAvailable from {book.copiesAvailable+item.quantity} to {book.copiesAvailable}')
        else:
            print(f'[Order Executor] BookId: {book.id} copiedAvailable is less than ordering quantity.')
            return False
        
        print(f'[Order Executor] Send request of updating the book data.') 
        with grpc.insecure_channel('book_database_1:50056') as channel:
            stub = book_database_grpc.BookDatabaseServiceStub(channel)
            response = stub.UpdateBook(book_database.UpdateBookRequest(
                book=book, 
                commitStatus=global_commit)
            )
            return response.success
    
class OrderExecutorService(order_executor_grpc.OrderExecutorServiceServicer):
    def __init__(self):
        self.is_busy = False
        self.has_token = replica_id == 1  # Set the first token holder
        if self.has_token:
            print(f"Replica {replica_id} is the leader.")

    def PassToken(self, request, context):
        # print(f"Replica {replica_id} received the token.")
        self.has_token = True
        return order_executor.TokenResponse(success=True)
    
    def CheckHealth(self, request, context):
        # check if a replica is alive
        return order_executor.HealthCheckResponse(alive=True)
    
    def SendVoteRequestToParticipants(self):
        with futures.ThreadPoolExecutor() as executor:
            payment_executor_vote = executor.submit(send_vote_request_to_payment_executor)
            book_database_vote = executor.submit(send_vote_request_to_book_database)

        futures.wait([payment_executor_vote, book_database_vote], return_when=futures.ALL_COMPLETED)

        if not payment_executor_vote.result():
            print(f"Phase 2a - Order Executor-{replica_id}: Received VOTE ABORT from Payment Executor. Will send GLOBAL ABORT")
        if not book_database_vote.result():
            print(f"Phase 2a - Order Executor-{replica_id}: Received VOTE ABORT from Book Database. Will send GLOBAL ABORT")
        if payment_executor_vote.result() and book_database_vote.result():
            print(f"Phase 2a - Order Executor-{replica_id}: Received VOTE COMMIT from both participants. Will send GLOBAL COMMIT")

        return payment_executor_vote.result() and book_database_vote.result()
        
    
    # def SendGlobalCommit(self, request, context):
    #     # send global commit to all participants if vote-commit received from all 
    #     return order_executor.GlobalCommitResponse(alive=True)
    
    def execute_order(self, order):
        with tracer.start_as_current_span("execute_order") as span:
            span.set_attribute("order_id", order.orderId)
            order_counter.add(1, {"status": "processed"})
            order_status.add(1)
            self.is_busy = True # to indicate when they do not need the critical regiion

            global_commit = self.SendVoteRequestToParticipants()
            span.add_event(f"Global commit: {global_commit}")
            print(f"global_commit ={type(global_commit)}= {global_commit}")

            with futures.ThreadPoolExecutor() as executor:
                payment_future = executor.submit(send_execute_request_to_payment_executor, global_commit)
            
                database_futures_list = []
                for item in order.items:
                    future = executor.submit(send_execute_request_to_book_database, global_commit, item)
                    database_futures_list.append(future)

                futures.wait([payment_future] + database_futures_list, return_when=futures.ALL_COMPLETED)
                
            # Check all future results for True
            payment_success = payment_future.result()
            database_all_success = all(future.result() for future in database_futures_list)

            if payment_success and database_all_success:
                print("[Order Executor] Payment execution is successful")
                print('[Order Executor] All book database updates are successful.')
                for item in order.items:
                    print(f'[Order Executor] Execution success. user name: {order.user.name}, ordered book: {item.book.title}, quantity: {item.quantity}')
            else:
                if not payment_success:
                    print("[Order Executor] Payment executes failed.")
                if not database_all_success:
                    print('[Order Executor] Some book database updates failed.')
                print(f'[Order Executor] Execution failed, even though we showed the order-successful confirmation page. \
                    Send mail or call to the user contact: {order.user.contact} user name: {order.user.name}')   

            print(f"Order with id {order.orderId} with priority {order.priority} has been executed by executor Replica-{replica_id} ...")
            time.sleep(30)  # Simulate time taken to process the order
            self.is_busy = False

    def dequeue_order(self):
        while True:
            if self.has_token:
                if not self.is_busy:
                    with grpc.insecure_channel('order_queue:50054') as channel:
                        stub = order_queue_grpc.OrderQueueServiceStub(channel)
                        response = stub.Dequeue(order_queue.DequeueRequest())
                        if response.success:
                            print(f"Replica-{replica_id} has entered the critical region and dequeued an order")
                            self.pass_token()

                            #send vote response. 
                            self.execute_order(response.order)
                        else:
                            self.pass_token()
                else:
                    print(f"Replica-{replica_id} is busy.")
                    self.pass_token()

            time.sleep(20)  # delay then check if you have token

    def pass_token(self):
        for i in range(0, total_replicas):
            next_replica_id = (replica_id + i) % total_replicas + 1
            next_replica_address = f'order_executor_{next_replica_id}:50055'
        
            # making the token ring fault-tolerant so token does not get stuck with a dead replica
            try:
                with grpc.insecure_channel(next_replica_address) as channel:
                    stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                    health_response = stub.CheckHealth(order_executor.HealthCheckRequest(), timeout=5)
                    if health_response.alive:
                        stub.PassToken(order_executor.Token(token=str(next_replica_id)))
                        break # stop looking for next viable replica
                    else:
                        print(f"Replica-{next_replica_id} did not respond.")
            except grpc.RpcError as e:
                    print(f"Could not reach Replica-{next_replica_id}: Inactive Service")
        self.has_token = False
        print(f"Replica-{replica_id} passed token to Replica-{next_replica_id}.")


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add OrderExecutorService
    executor_service = OrderExecutorService()
    order_executor_grpc.add_OrderExecutorServiceServicer_to_server(executor_service, server)
    # Listen on port 50055
    port = "50055"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50055.")
    executor_service.dequeue_order()  # Start processing orders
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
