import sys
import os
from datetime import datetime
import random

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, utils_path)

from payment_executor import payment_executor_pb2 as payment_executor
from payment_executor import payment_executor_pb2_grpc as payment_executor_grpc

import grpc
from concurrent import futures


class PaymentExecutionService(payment_executor_grpc.PaymentExecutionServiceServicer):
    def ExecutePayment(self, request, context):
        response = False
        if request.global_commit: 
            print("Phase 2b - GLOBAL COMMIT received from cordinator")
            print("Payment execution is being processed")
        else:
            print("Phase 2b - GLOBAL ABORT received from cordinator")
            print("Payment execution is being aborted")
        return payment_executor.ExecutePaymentResponse(success=response)

    def SendVoteToCordinator(self, request, context): 
        #Dummy logic. Sends vote commit 95% of the time and abort the otehr 5%
        response = random.choices([True, False], weights=[95, 5], k=1)[0]
        if response:
            print("Phase 1b - Payment Executor Service: Vote request received. Sending vote commit to executor\n")
        else:
            print("Phase 1b - Payment Executor Service: Vote request received. Sending vote abort to executor\n")
        return payment_executor.VoteCommitResponse(success=True)


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add HelloService
    payment_executor_grpc.add_PaymentExecutionServiceServicer_to_server(PaymentExecutionService(), server)
    # Listen on port 50059
    port = "50096"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print("Server started. Listening on port 50059.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()