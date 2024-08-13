import sys
import json
import grpc
from concurrent import futures
import wallet_pb2
import wallet_pb2_grpc
import threading
from dataclasses import dataclass

@dataclass
class SalesOrder:
    id: int
    account_id: str
    value: int

class WallerServicer(wallet_pb2_grpc.WalletServicer):
    def __init__(self):
        self.__wallets: dict[str, int] = {}
        self.__read_wallets()
        self.__sales_orders: list[SalesOrder] = []
        self.__sales_order_id_generator = 1
        self.terminate = threading.Event()

    def __read_wallets(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            identificador, valor = line.split()
            valor = int(valor)
            self.__wallets[identificador] = valor
            if len(self.__wallets) == 10:
                break

    def Balance(self, request, context):
        balance = self.__wallets.get(request.account_id, -1)
        return wallet_pb2.BalanceResponse(balance=balance)

    def SalesOrder(self, request, context):
        accout = request.account_id
        value = request.value
        if accout not in self.__wallets:
            return wallet_pb2.SalesOrderResponse(status=-1)

        if self.__wallets[accout] < value:
            return wallet_pb2.SalesOrderResponse(status=-2)

        self.__wallets[accout] -= value
        salesOrder = SalesOrder(self.__sales_order_id_generator, accout, value)
        self.__sales_orders.append(salesOrder)
        self.__sales_order_id_generator += 1
        return wallet_pb2.SalesOrderResponse(status=0, order_id=salesOrder.id)

    def Transfer(self, request, context):
        order_id = request.order_id
        value = request.value
        account_id = request.account_id

        sales_order = next((so for so in self.__sales_orders if so.id == order_id), None)

        if sales_order is None:
            return wallet_pb2.TransferResponse(status=-1)
        if sales_order.value != value:
            return wallet_pb2.TransferResponse(status=-2)
        if account_id not in self.__wallets:
            return wallet_pb2.TransferResponse(status=-3)

        self.__sales_orders.remove(sales_order)
        self.__wallets[account_id] += value

        return wallet_pb2.TransferResponse(status=0)

    def End(self, request, context):
        print(json.dumps(self.__wallets, indent=2))
        self.terminate.set()
        return wallet_pb2.EndResponse(pendencies=len(self.__sales_orders))

    def should_terminate(self):
        return self.terminate.is_set()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = WallerServicer()
    wallet_pb2_grpc.add_WalletServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{int(sys.argv[1])}')
    server.start()

    while not servicer.should_terminate():
        try:
            server.wait_for_termination(timeout=1)
        except grpc.RpcError:
            pass

    server.stop(grace=0)

if __name__ == '__main__':
    serve()
