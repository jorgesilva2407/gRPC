import sys
import grpc
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grcp

class WalletClient:
    def __init__(self, client, addr) -> None:
        """
        Initializes the WalletClient class, setting up the gRPC channel and stub for communication with the Wallet service.

        Args:
            client (str): The client ID associated with the wallet.
            addr (str): The address of the gRPC server.
        """
        self.__client = client
        self.__channel = grpc.insecure_channel(addr)
        self.__stub = service_grcp.WalletStub(self.__channel)

    def GetBalance(self):
        """
        Retrieves the balance of the wallet associated with the client ID.

        Returns:
            GetBalanceResponse: The response object containing the wallet's balance.
        """
        response = self.__stub.GetBalance(service.GetBalanceRequest(id=self.__client))
        return response

    def CreateSalesOrder(self, value):
        """
        Creates a sales order by deducting the specified amount from the wallet associated with the client ID.

        Args:
            value (float): The amount to be deducted from the wallet.

        Returns:
            CreateSalesOrderResponse: The response object containing the status and order ID.
        """
        response = self.__stub.CreateSalesOrder(service.CreateSalesOrderRequest(id=self.__client, amount=value))
        return response

    def Transfer(self, order_id, value, dest_wallet_id):
        """
        Transfers the specified amount from a sales order to a destination wallet.

        Args:
            order_id (int): The ID of the sales order.
            value (float): The amount to be transferred.
            dest_wallet_id (str): The ID of the destination wallet.

        Returns:
            TransferResponse: The response object containing the status of the transfer.
        """
        response = self.__stub.Transfer(service.TransferRequest(order_id=order_id, amount=value, dest_wallet_id=dest_wallet_id))
        return response

    def EndWallet(self):
        """
        Ends the wallet service and retrieves the number of pending sales orders.

        Returns:
            EndWalletResponse: The response object containing the number of pending orders.
        """
        response = self.__stub.EndWallet(service.Empty())
        return response

def main():
    """
    Entry point of the WalletClient application. Interacts with the user to send commands
    to the Wallet service and process the responses.

    The available commands are:
    - "S": Retrieves and prints the balance of the wallet.
    - "O <value>": Creates a sales order with the specified value and prints the order ID.
    - "X <order_id> <value> <dest_wallet_id>": Transfers the specified value from the sales order to the destination wallet.
    - "F": Ends the wallet service and prints the number of pending sales orders.
    """
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
