import sys
import grpc
import threading
from dataclasses import dataclass
from concurrent import futures
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grcp

@dataclass
class SalesOrder:
    id: int
    amount: float

class WalletServicer(service_grcp.WalletServicer):
    def __init__(self):
        self.__wallets: dict[str, int] = {}
        self.__sales_order_id_generator = 1
        self.__sales_orders: list[SalesOrder] = []
        self.terminate = threading.Event()
        self.__lock = threading.Lock()

        for line in sys.stdin:
            wallet_id, balance = line.strip().split()
            self.__wallets[wallet_id] = int(balance)

    def GetBalance(self, request, context):
        with self.__lock:
            balance = self.__wallets.get(request.id, -1)
        return service.GetBalanceResponse(balance=balance)

    def CreateSalesOrder(self, request, context):
        with self.__lock:
            if request.id not in self.__wallets:
                return service.CreateSalesOrderResponse(status = -1, order_id = -1)

            if request.amount > self.__wallets[request.id]:
                return service.CreateSalesOrderResponse(status = -2, order_id = -2)

            self.__wallets[request.id] -= request.amount
            order = SalesOrder(self.__sales_order_id_generator, request.amount)
            self.__sales_order_id_generator += 1
            self.__sales_orders.append(order)
        return service.CreateSalesOrderResponse(status = 0, order_id = order.id)

    def Transfer(self, request, context):
        with self.__lock:
            order = [o for o in self.__sales_orders if o.id == request.order_id]
            if len(order) == 0:
                return service.TransferResponse(status = -1)

            order = order[0]

            if order.amount != request.amount:
                return service.TransferResponse(status = -2)

            if request.dest_wallet_id not in self.__wallets:
                return service.TransferResponse(status = -3)

            self.__wallets[request.dest_wallet_id] += request.amount
            self.__sales_orders.remove(order)
        return service.TransferResponse(status = 0)

    def EndWallet(self, request, context):
        with self.__lock:
            for wallet_id, balance in self.__wallets.items():
                print(f"Wallet {wallet_id} has balance {balance}")
            pending_orders = len(self.__sales_orders)
            self.terminate.set()
        return service.EndWalletResponse(pendencies = pending_orders)

def serve():
    port = int(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    wallet_servicer = WalletServicer()
    service_grcp.add_WalletServicer_to_server(wallet_servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    wallet_servicer.terminate.wait()
    server.stop(1)

if __name__ == "__main__":
    serve()
