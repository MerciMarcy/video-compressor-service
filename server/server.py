import socket
import os

from dotenv import load_dotenv

load_dotenv()

class Server:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = None

    def start(self):
        # create socket
        sock = self.sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        dpath = "tmp"
        if not os.path.exists(dpath):
            os.makedirs(dpath)

        print("Starting up on {} port {}".format(self.server_address, self.server_port))

        # bind address
        sock.bind((self.server_address, self.server_port))

        # listen for connection
        sock.listen(1)

        while True:
            # accept for connection
            conn, client_address = sock.accept()

            try:
                print("connection from", client_address)

                header = conn.recv(8)

                filename_length = int.from_bytes(header[:1], "big")
                json_length = int.from_bytes(header[1:3], "big")
                data_length = int.from_bytes(header[4:8], "big")
                stream_rate = 4096

                print(
                    "Received header from client. Byte lengths: Title length {}, JSON length {}, Data Length {}".format(
                        filename_length, json_length, data_length
                    )
                )

                filename = conn.recv(filename_length).decode("utf-8")

                print("Filename: {}".format(filename))

                if json_length != 0:
                    raise Exception("JSON data is not currently supported.")

                if data_length == 0:
                    raise Exception("No data to read from client.")

                with open(os.path.join(dpath, filename), "wb+") as f:
                    while data_length > 0:
                        data = conn.recv(
                            data_length if data_length <= stream_rate else stream_rate
                        )
                        f.write(data)
                        print("recieved {} bytes".format(len(data)))
                        data_length -= len(data)
                        print(data_length)

                print("Finished downloading the file from client.")

            except Exception as e:
                print("Error:" + str(e))

            finally:
                print("Closing current connection")
                conn.close()


if __name__ == "__main__":
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    server = Server(SERVER_ADDRESS, SERVER_PORT)
    server.start()
