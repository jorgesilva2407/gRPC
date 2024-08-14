import sys
import grpc
from client.wallet import WalletClient
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grcp

class StoreClient:
    def __init__(self, client, wallet_addr, store_addr):
        print(wallet_addr)
        print(store_addr)
        self.__client = client
        self.__price = None
        self.__wallet = WalletClient(client, wallet_addr)
        self.__channel = grpc.insecure_channel(store_addr)
        self.__stub = service_grcp.StoreStub(self.__channel)

    def Buy(self):
        if self.__price is None:
            response = self.__stub.GetPrice(service.Empty())
            self.__price = response.price

        sales_order_response = self.__wallet.CreateSalesOrder(self.__price)
        if sales_order_response.status < 0:
            return sales_order_response.status, -11

        response = self.__stub.Sell(service.SellRequest(order_id=sales_order_response.order_id))
        return sales_order_response.status, response.status

    def EndStore(self):
        response = self.__stub.EndStore(service.Empty())
        return response.revenue, response.wallet_server_response

def main():
    client = sys.argv[1]
    wallet_addr = sys.argv[2]
    store_addr = sys.argv[3]
    store_client = StoreClient(client, wallet_addr, store_addr)

    while True:
        command = input().strip().split()
        if command[0] == "C":
            wallet_status, store_status = store_client.Buy()
            print(wallet_status)
            if (wallet_status == 0):
                print(store_status)
        elif command[0] == "T":
            revenue, pendencies = store_client.EndStore()
            print(revenue, pendencies)
            break

if __name__ == "__main__":
    main()
