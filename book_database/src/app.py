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
# from pysyncobj import SyncObj, replicated

class BookDatabaseService(book_database_grpc.BookDatabaseServiceServicer):
    def __init__(self):
        self.books = {}

        with open(os.path.abspath(os.path.join(FILE, '../book_list.json'))) as f:
            book_list_json = json.load(f)
            for _, value in book_list_json.items():
                book = book_database.Book(**value)
                self.books[book.id] = book

    def AddBook(self, request, context):
        self.books[request.id] = request # bookdb_pb2.Book()
        return request

    def GetBook(self, request, context):
        return self.books[request.request_id]
    
    def ListBooks(self, request, context):
        return None
    
    def UpdateBook(self, request, context):
        return None

    def DeleteBook(self, request, context):
        return None

    # Implement other methods similarly, using @replicated for methods that modify state

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_database_grpc.add_BookDatabaseServiceServicer_to_server(BookDatabaseService(), server)
    server.add_insecure_port('[::]:50056')
    server.start()
    print("Book Database Service started on port 50056")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()