from multiprocessing import connection as mc

ADDRESS = "localhost", 1234


connection = mc.Client(ADDRESS)
while True:
    msg = connection.recv()
    print(msg)
    if msg == "q":
        break
    connection.send(f"{msg} received")
