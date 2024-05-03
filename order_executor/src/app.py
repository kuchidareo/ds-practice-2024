import sys
import os
from datetime import datetime
import queue
import time

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
from payment_executor import payment_executor_pb2 as payment_executor
from payment_executor import payment_executor_pb2_grpc as payment_executor_grpc
# from book_database import book_database_pb2 as book_database
# from book_database import book_database_pb2_grpc as book_database_grpc

import grpc
from concurrent import futures

import socket

replica_id = int(os.getenv('REPLICA_ID', '0'))  # Gets the ID of the current replica from the environment.
print(f"My ID is: {replica_id}")
total_replicas = int(os.getenv('TOTAL_REPLICAS', '6'))

def dequeue():
    # Access the order queue to dequeue.
    with grpc.insecure_channel('order_queue:50054') as channel:
            print(f"Replica {replica_id} has accessed the queue")
            stub = order_queue_grpc.OrderQueueServiceStub(channel)
            response = stub.Dequeue(order_queue.DequeueRequest())

    return response

def send_vote_request_to_payment_executor():
    print("Order Exector: Phase 1a - Sending vote request to Payment Executor.")
    with grpc.insecure_channel('payment_executor:50059') as channel:
        stub = payment_executor_grpc.PaymentExecutorStub(channel)
        response = stub.SendVoteToCoordinator(payment_executor.VoteCommitRequest())
        return response.success
    
def send_vote_request_to_book_database():
    print("Order Exector: Phase 1a - Sending vote request to Book Database.")
    with grpc.insecure_channel('book_database:50057') as channel:
        stub = book_database_grpc.BookDatabaseServiceStub(channel)
        response = stub.SendVoteToCoordinator(book_database.VoteCommitRequest())
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

        if not payment_executor_vote:
            print("Order Exector: Phase 2a - Received VOTE ABORT from Payment Executor. Will send GLOBAL ABORT")
        if not book_database_vote:
            print("Order Exector: Phase 2a - Received VOTE ABORT from Book Database. Will send GLOBAL ABORT")
        if payment_executor_vote and book_database_vote:
            print("Order Exector: Phase 2a - Received VOTE COMMIT from both participants. Will send GLOBAL COMMIT")

        return payment_executor_vote and book_database_vote
        

        
    
    # def SendGlobalCommit(self, request, context):
    #     # send global commit to all participants if vote-commit received from all 
    #     return order_executor.GlobalCommitResponse(alive=True)
    
    def execute_order(self, order):
        self.is_busy = True # to indicate when they do not need the critical regiion

        global_commit = self.SendVoteRequestToParticipants().response

        with grpc.insecure_channel('payment_executor:50059') as channel:
            stub = payment_executor_grpc.PaymentExecutionServiceStub(channel)
            response = stub.ExecutePayment(payment_executor.PaymentExectionRequest(), global_commit)
            if response.success:
                print(f"Payment execution was a success")

        print(f"Order with id {order.orderId} with priority {order.priority} is being executed by executor Replica-{replica_id} ...")
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