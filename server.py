import socket
from encryption import Public, Private


SIZE = 1048576
FORMAT = "utf-8"

class Communicator:
    def send_encr(self, data: bytes) -> None:
        pass
    def send_str(self, data: str) -> None:
        pass
    def recieve_ecr(self) -> bytes:
        return b""

class Server(Communicator):
    def __init__(self) -> None:
        self.ip = socket.gethostbyname(socket.gethostname())
        
    def setup(self, port: int) -> None:
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, port))
        self.socket.listen(1)

        self.clientSocket, self.returnAddress = self.socket.accept()

        self.private = Private()
        self.clientSocket.send(self.private.public_bytes)
        encrypted_fernet_key = self.clientSocket.recv(SIZE)
        self.private.setup_with_encrypted_fernet_key(encrypted_fernet_key)

    def send(self, data: bytes) -> None:
        self.clientSocket.send(data)
    def sendall(self, data: bytes) -> None:
        self.clientSocket.sendall(data)
    def send_encr(self, data: bytes) -> None:
        encrypted_data = self.private.encrypt(data)
        self.clientSocket.send(encrypted_data)
    def send_str(self, data: str) -> None:
        encrypted_data = self.private.encrypt(data.encode(FORMAT))
        self.clientSocket.send(encrypted_data)
    def recieve(self, size: int = -1) -> bytes:
        if size < 1: size = SIZE
        return self.clientSocket.recv(size)
    def recieve_to(self, to_read: int) -> bytes:
        if to_read > SIZE: size = SIZE
        else: size = to_read
        return self.clientSocket.recv(size)
    def recieve_ecr(self) -> bytes:
        encrypted_data = self.clientSocket.recv(SIZE)
        return self.private.decrypt(encrypted_data)
    
    
    def close(self) -> None:
        try:
            self.socket.close()
            self.clientSocket.close()
        except: pass



class Client(Communicator):
    def __init__(self) -> None:
        pass

    def connect(self, ip: str, port: int) -> None:
        self.socket = socket.socket()
        self.socket.connect((ip, port))

        public_bytes = self.socket.recv(SIZE)
        self.public = Public(public_bytes)
        self.socket.send(self.public.encrypted_fernet_key())

    def send(self, data: bytes) -> None:
        self.socket.send(data)
    def sendall(self, data: bytes) -> None:
        self.socket.sendall(data)
    def send_encr(self, data: bytes) -> None:
        encrypted_data = self.public.encrypt(data)
        self.socket.send(encrypted_data)
    def send_str(self, data: str) -> None:
        encrypted_data = self.public.encrypt(data.encode(FORMAT))
        self.socket.send(encrypted_data)
    def recieve(self, size: int = -1) -> bytes:
        if size < 1: size = SIZE
        return self.socket.recv(size)
    def recieve_ecr(self, size: int = -1) -> bytes:
        if size < 1: size = SIZE
        encrypted_data = self.socket.recv(size)
        return self.public.decrypt(encrypted_data)
    
    def close(self) -> None:
        try: self.socket.close()
        except: pass


if __name__ == "__main__":
    from threading import Thread
    from time import sleep

    PORT = 5555

    ONE = "Test1"
    TWO = "YAYDWAYDI8282+_"
    THREE = "FINALLLAAYYY"

    def server():
        server = Server()
        server.setup(PORT)

        server.send_encr(ONE.encode())
        print(server.recieve_ecr().decode() == TWO)
        print(server.recieve_ecr().decode() == THREE)

    Thread(target=server).start()
    sleep(0.1)

    ip = socket.gethostbyname(socket.gethostname())
    client = Client()
    client.connect(ip, PORT)

    print(client.recieve_ecr().decode() == ONE)
    client.send_encr(TWO.encode())
    client.send_encr(THREE.encode())