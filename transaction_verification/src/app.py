import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_pb2 as transaction_verification
import transaction_pb2_grpc as transaction_verification_grpc

from concurrent import futures
import grpc


class TransactionService(transaction_verification_grpc.TransactionServiceServicer):
    def VerifyTransaction(self, request, context):
        print("Transaction verification request received")
        
        is_valid = bool(request.user.name and request.user.contact)
        print(f"Transaction verification response: {'Valid' if is_valid else 'Invalid'}")
        return transaction_verification.TransactionResponse(is_valid=is_valid)

    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor())
    transaction_verification_grpc.add_TransactionServiceServicer_to_server(TransactionService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Transaction Verification Service started on port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()