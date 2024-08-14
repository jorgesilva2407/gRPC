import sys
import grpc
import threading
from concurrent import futures
from client.wallet import WalletClient
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grpc

class StoreServicer(service_grpc.StoreServicer):
    def __init__(self, price, id, addr):
        self.__price = price
        self.__id = id
        self.__revenue = 0
        self.terminate = threading.Event()
        self.__lock = threading.Lock()
        self.__wallet = WalletClient(id, addr)

    def GetPrice(self, request, context):
        return service.GetPriceResponse(price=self.__price)

    def Sell(self, request, context):
        response = self.__wallet.Transfer(order_id=request.order_id, value=self.__price, dest_wallet_id=self.__id)

        if response.status < 0:
            return service.SellResponse(status=-9)

        with self.__lock:
            self.__revenue += self.__price

        return service.SellResponse(status=response.status)

    def EndStore(self, request, context):
        response = self.__wallet.EndWallet()
        self.terminate.set()
        with self.__lock:
            revenue = self.__revenue
        return service.EndStoreResponse(revenue=revenue, wallet_server_response=response.pendencies)

def serve():
    price = int(sys.argv[1])
    port = int(sys.argv[2])
    id = sys.argv[3]
    addr = sys.argv[4]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    store_servicer = StoreServicer(price, id, addr)
    service_grpc.add_StoreServicer_to_server(store_servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    store_servicer.terminate.wait()
    server.stop(1)

if __name__ == '__main__':
    serve()
