clean:
	rm proto/services_pb2.py proto/services_pb2_grpc.py

stubs: proto/*.proto
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/services.proto

run_serv_banco:
	if [ ! -f proto/services_pb2.py ] || [ ! -f proto/services_pb2_grpc.py ]; then make stubs; fi
	python3 -m server.wallet $(arg1)

run_cli_banco:
	if [ ! -f proto/services_pb2.py ] || [ ! -f proto/services_pb2_grpc.py ]; then make stubs; fi
	python3 -m client.wallet $(arg1) $(arg2)

run_serv_loja:
	if [ ! -f proto/services_pb2.py ] || [ ! -f proto/services_pb2_grpc.py ]; then make stubs; fi
	python3 -m server.store $(arg1) $(arg2) $(arg3) $(arg4)

run_cli_loja:
	if [ ! -f proto/services_pb2.py ] || [ ! -f proto/services_pb2_grpc.py ]; then make stubs; fi
	python3 -m client.store $(arg1) $(arg2) $(arg3)
