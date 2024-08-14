import sys
import grpc
from client.wallet import WalletClient
from proto import services_pb2 as service
from proto import services_pb2_grpc as service_grcp

class StoreClient:
    def __init__(self, client, wallet_addr, store_addr):
        """
        Initializes the StoreClient class, setting up the WalletClient, gRPC channel, and stub for communication with the Store service.

        Args:
            client (str): The client ID associated with the wallet.
            wallet_addr (str): The address of the Wallet service.
            store_addr (str): The address of the Store service.
        """
        self.__client = client
        self.__price = None
        self.__wallet = WalletClient(client, wallet_addr)
        self.__channel = grpc.insecure_channel(store_addr)
        self.__stub = service_grcp.StoreStub(self.__channel)

    def Buy(self):
        """
        Executes a purchase by first retrieving the price from the store, creating a sales order via the Wallet service,
        and then finalizing the purchase with the store.

        Returns:
            tuple: A tuple containing the status of the wallet operation and the status of the store operation.
        """
        if self.__price is None:
            response = self.__stub.GetPrice(service.Empty())
            self.__price = response.price

        sales_order_response = self.__wallet.CreateSalesOrder(self.__price)
        if sales_order_response.status < 0:
            return sales_order_response.status, -11

        response = self.__stub.Sell(service.SellRequest(order_id=sales_order_response.order_id))
        return sales_order_response.status, response.status

    def EndStore(self):
        """
        Ends the store service and retrieves the store's total revenue and the status of any pending transactions from the Wallet service.

        Returns:
            tuple: A tuple containing the total revenue and the number of pending transactions from the Wallet service.
        """
        response = self.__stub.EndStore(service.Empty())
        return response.revenue, response.wallet_server_response

def main():
    """
    Entry point of the StoreClient application. Interacts with the user to send commands
    to the Store service and process the responses.

    The available commands are:
    - "C": Executes a purchase and prints the status of the wallet and store operations.
    - "T": Ends the store service, prints the total revenue and pending transactions, and terminates the program.
    """
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
