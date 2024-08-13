import sys
import grpc
import wallet_pb2
import wallet_pb2_grpc

class WalletClient:
    def __init__(self, server_id) -> None:
        self.channel = grpc.insecure_channel(server_id)
        self.stub = wallet_pb2_grpc.WalletStub(self.channel)

    def Balance(self, account_id) -> int:
        response = self.stub.Balance(wallet_pb2.BalanceRequest(account_id=account_id))
        return response.balance

    def SalesOrder(self, account_id, value) -> tuple[int, int]:
        response = self.stub.SalesOrder(wallet_pb2.SalesOrderRequest(account_id=account_id, value=value))
        return response.status, response.order_id

    def Transfer(self, order_id, value, account_id) -> int:
        response = self.stub.Transfer(wallet_pb2.TransferRequest(order_id=order_id, value=value, account_id=account_id))
        return response.status

    def End(self) -> int:
        response = self.stub.End(wallet_pb2.EndRequest())
        return response.pendencies

    def __del__(self):
        self.channel.close()

def run():
    account_id = sys.argv[1]
    server_id = sys.argv[2]

    client = WalletClient(server_id)

    while(True):
        params = input().strip().split()
        if params[0] == "S":
            print(f"Balance: {client.Balance(account_id)}")

        elif params[0] == "O":
            value = int(params[1])
            status, order_id = client.SalesOrder(account_id, value)
            if (status == 0):
                print(f"Order placed successfully - Order id = {order_id}")
            elif (status == -1):
                print("Wallet doesn't exist")
            elif (status == -2):
                print("Insufficient balance")

        elif params[0] == "X":
            order_id = int(params[1])
            value = int(params[2])
            dest = params[3]
            status = client.Transfer(order_id, value, dest)
            if (status == 0):
                print("Transfer successful")
            elif (status == -1):
                print("Order not found")
            elif (status == -2):
                print("Invalid value")
            elif (status == -3):
                print("Destination wallet doesn't exist")

        elif params[0] == "F":
            print(f"Pending orders: {client.End()}")
            break

if __name__ == '__main__':
    run()
