import sys
import grpc
import store_pb2
import store_pb2_grpc
import threading
from concurrent import futures
from wallet_client import WalletClient

class StoreServicer(store_pb2_grpc.StoreServicer):
    def __init__(self, server_id, account_id, price) -> None:
        self.__client = WalletClient(server_id)
        self.__account_id = account_id
        self.__price: int = price
        self.__revenue = 0
        self.terminate = threading.Event()

    def GetPrice(self, request, context):
        print(self.__price)
        return store_pb2.GetPriceResponse(price=self.__price)

    def Sell(self, request, context):
        order_id = request.order_id
        status = self.__client.Transfer(order_id, self.__price, self.__account_id)
        if (status == 0):
            self.__revenue += self.__price
        return store_pb2.SellResponse(status=status)

    def End(self, request, context):
        pendencies = self.__client.End()
        self.terminate.set()
        return store_pb2.EndResponse(revenue=self.__revenue, pendencies=pendencies)

    def should_terminate(self):
        return self.terminate.is_set()

def serve():
    price = int(sys.argv[1])
    port = int(sys.argv[2])
    account_id = sys.argv[3]
    server_id = sys.argv[4]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = StoreServicer(server_id, account_id, price)
    store_pb2_grpc.add_StoreServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    while not servicer.should_terminate():
        try:
            server.wait_for_termination(1)
        except grpc.RpcError:
            pass

if __name__ == '__main__':
    serve()
