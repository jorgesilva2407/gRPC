import sys
import grpc
import threading
from concurrent import futures
from client.wallet import WalletClient
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grpc

class StoreServicer(service_grpc.StoreServicer):
    def __init__(self, price, id, addr):
        """
        Initializes the StoreServicer class, setting up the price of the store's goods,
        the store's ID, revenue, synchronization primitives, and a WalletClient for managing payments.

        Args:
            price (int): The price of the goods sold by the store.
            id (str): The unique identifier of the store.
            addr (str): The address of the Wallet service for making transactions.
        """
        self.__price = price
        self.__id = id
        self.__revenue = 0
        self.terminate = threading.Event()
        self.__lock = threading.Lock()
        self.__wallet = WalletClient(id, addr)

    def GetPrice(self, request, context):
        """
        Retrieves the price of the goods sold by the store.

        Args:
            request (GetPriceRequest): The request object.
            context: The gRPC context.

        Returns:
            GetPriceResponse: The response object containing the price of the goods.
        """
        return service.GetPriceResponse(price=self.__price)

    def Sell(self, request, context):
        """
        Processes the sale of goods by transferring the price from the client's wallet to the store's wallet.

        Args:
            request (SellRequest): The request object containing the order ID.
            context: The gRPC context.

        Returns:
            SellResponse: The response object containing the status of the sale.
        """
        response = self.__wallet.Transfer(order_id=request.order_id, value=self.__price, dest_wallet_id=self.__id)

        if response.status < 0:
            return service.SellResponse(status=-9)

        with self.__lock:
            self.__revenue += self.__price

        return service.SellResponse(status=response.status)

    def EndStore(self, request, context):
        """
        Ends the store service, retrieves the total revenue, and signals the termination of the server.

        Args:
            request (EndStoreRequest): The request object.
            context: The gRPC context.

        Returns:
            EndStoreResponse: The response object containing the total revenue and any pending transactions from the wallet service.
        """
        response = self.__wallet.EndWallet()
        self.terminate.set()
        with self.__lock:
            revenue = self.__revenue
        return service.EndStoreResponse(revenue=revenue, wallet_server_response=response.pendencies)

def serve():
    """
    Starts the gRPC server for the Store service, initializes the StoreServicer,
    and runs the server on the specified port until the termination event is triggered.
    """
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
