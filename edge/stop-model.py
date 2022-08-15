import time
import grpc
import edge_agent_pb2 as pb2 
from edge_agent_pb2_grpc import (
            EdgeAgentStub
)

channel = grpc.insecure_channel("unix:///tmp/aws.iot.lookoutvision.EdgeAgent.sock")
stub = EdgeAgentStub(channel)
print(stub.StopModel(pb2.StopModelRequest(model_component="ComponentCircuitBoard")))
