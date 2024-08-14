import sys
import grpc
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grcp

class WalletClient:
    def __init__(self, client, addr) -> None:
        self.__client = client
        self.__channel = grpc.insecure_channel(addr)
        self.__stub = service_grcp.WalletStub(self.__channel)

    def GetBalance(self):
        response = self.__stub.GetBalance(service.GetBalanceRequest(id=self.__client))
        return response

    def CreateSalesOrder(self, value):
        response = self.__stub.CreateSalesOrder(service.CreateSalesOrderRequest(id=self.__client, amount=value))
        return response

    def Transfer(self, order_id, value, dest_wallet_id):
        response = self.__stub.Transfer(service.TransferRequest(order_id=order_id, amount=value, dest_wallet_id=dest_wallet_id))
        return response

    def EndWallet(self):
        response = self.__stub.EndWallet(service.Empty())
        return response

def main():
    client = sys.argv[1]
    addr = sys.argv[2]
    wallet_client = WalletClient(client, addr)

    while True:
        command = input().strip().split()
        if command[0] == "S":
            response = wallet_client.GetBalance()
            print(response.balance)
        elif command[0] == "O":
            value = int(command[1])
            response = wallet_client.CreateSalesOrder(value)
            if response.status < 0:
                print(response.status)
            else:
                print(response.order_id)
        elif command[0] == "X":
            order_id = int(command[1])
            value = int(command[2])
            dest_wallet_id = command[3]
            response = wallet_client.Transfer(order_id, value, dest_wallet_id)
            print(response.status)
        elif command[0] == "F":
            response = wallet_client.EndWallet()
            print(response.pendencies)
            break

if __name__ == "__main__":
    main()
