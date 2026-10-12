import zmq

socket = zmq.Context().socket(zmq.REP)
socket.bind("tcp://*:5557")

while True:
    data = socket.recv_pyobj()
    print(f"Request received, sorting array...")
    socket.send_pyobj(sorted(data, key=str.lower))
    print(f"Sending sorted array...")