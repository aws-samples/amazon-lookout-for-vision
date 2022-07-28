import time
import sys
import grpc
import edge_agent_pb2 as pb2 
from edge_agent_pb2_grpc import (
            EdgeAgentStub
)

channel = grpc.insecure_channel("unix:///tmp/aws.iot.lookoutvision.EdgeAgent.sock")
stub = EdgeAgentStub(channel)
stub.StartModel(pb2.StartModelRequest(model_component=sys.argv[1]))
