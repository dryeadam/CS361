# This will be a service that connects with the main program to sort a list by alphabetical order
# Use ZMQ for communication (model after home server project)
import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

while True:
    games = socket.recv_pyobj()
    print(f"Received {games}")
    result = sorted(games, key=str.lower)  # A-Z sort
    socket.send_pyobj(result)