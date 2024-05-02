import sys
import os
import json

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, utils_path)
from book_database import book_database_pb2 as book_database
from book_database import book_database_pb2_grpc as book_database_grpc

from concurrent import futures
import grpc

bd_node_id = int(os.getenv('DB_NODE_ID', '0'))
print(f"My Book Database ID is: {bd_node_id}")
total_nodes = int(os.getenv('TOTAL_REPLICAS', '3'))

class BookDatabaseService(book_database_grpc.BookDatabaseServiceServicer):
    def __init__(self):
        self.books = {}
        with open(os.path.abspath(os.path.join(FILE, '../book_list.json'))) as f:
            book_list_json = json.load(f)
            for _, value in book_list_json.items():
                book = book_database.Book(**value)
                self.books[book.id] = book

    def AddBook(self, request, context):
        with grpc.insecure_channel("book_database_1:50056") as channel:
            stub = book_database_grpc.BookDatabaseServiceStub(channel)
            response = stub.Head2Tail(request)
        return response

    def GetBook(self, request, context):
        return self.books[request.request_id]
    
    def ListBooks(self, request, context):
        return None
    
    def UpdateBook(self, request, context):
        with grpc.insecure_channel("book_database_1:50056") as channel:
            stub = book_database_grpc.BookDatabaseServiceStub(channel)
            response = stub.Head2Tail(request)
        return response

    def DeleteBook(self, request, context):
        return None
    
    def Head2Tail(self, request, context):
        # request # book_database.Book()
        if bd_node_id < total_nodes:
            next_bd_node_id = bd_node_id + 1
            print(f'Head To Tail: {bd_node_id} to {next_bd_node_id}')
            next_bd_node_address = f'book_database_{next_bd_node_id}:50056'
            try:
                with grpc.insecure_channel(next_bd_node_address) as channel:
                    stub = book_database_grpc.BookDatabaseServiceStub(channel)
                    response = stub.Head2Tail(request)
                    return response
            except grpc.RpcError as e:
                    print(f"Could not reach Update-commitment-{next_bd_node_id}: Inactive Service")
        elif bd_node_id == total_nodes: # if it reaches the Tail
            next_bd_node_id = bd_node_id
            next_bd_node_address = f'book_database_{next_bd_node_id}:50056'
            try:
                with grpc.insecure_channel(next_bd_node_address) as channel:
                    stub = book_database_grpc.BookDatabaseServiceStub(channel)
                    response = stub.Tail2Head(request)
                    return book_database.Head2TailResponse(success=response.success)
            except grpc.RpcError as e:
                    print(f"Could not reach Update-commitment-{next_bd_node_id}: Inactive Service")

    def Tail2Head(self, request, context):
        # request # book_database.Book()
        next_bd_node_id = bd_node_id - 1

        self.books[request.id] = request # Override the book information
        print(bd_node_id, 'updated the book info')

        if 0 < next_bd_node_id: # if it reaches the Tail
            print(f'Tail To Head: {bd_node_id} to {next_bd_node_id}')
            next_bd_node_address = f'book_database_{next_bd_node_id}:50056'
            try:
                with grpc.insecure_channel(next_bd_node_address) as channel:
                    stub = book_database_grpc.BookDatabaseServiceStub(channel)
                    response = stub.Tail2Head(request)
                    return response
            except grpc.RpcError as e:
                    print(f"Could not reach Update-commitment-{next_bd_node_id}: Inactive Service")
        else:
            return book_database.Tail2HeadResponse(success=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = BookDatabaseService()
    book_database_grpc.add_BookDatabaseServiceServicer_to_server(service, server)
    server.add_insecure_port('[::]:50056')
    server.start()
    print("Book Database Service started on port 50056")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()