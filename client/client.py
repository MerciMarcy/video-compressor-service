import socket
import sys
import os

from dotenv import load_dotenv

load_dotenv()


class Client:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.sock = None

    def start(self):
        sock = self.sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("connecting to {}".format(self.server_address, self.server_port))

        try:
            sock.connect((self.server_address, self.server_port))
        except socket.error as err:
            print(err)
            sys.exit(1)

        try:
            filepath = input("Type in a file to upload: ")

            with open(filepath, "rb") as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, 0)

                if filesize > pow(2, 32):
                    raise Exception("File must be below 4GB.")

                filename = os.path.basename(f.name)
                if not filename.endswith(".mp4"):
                    raise Exception("File type must be mp4.")
                filename_bits = filename.encode("utf-8")
                header = self.protocol_header(len(filename_bits), 0, filesize)

                sock.send(header)
                sock.send(filename_bits)

                data = f.read(4096)
                while data:
                    print("Sending...")
                    sock.send(data)
                    data = f.read(4096)

        finally:
            print("closing socket")
            sock.close()

    def protocol_header(self, filename_length, json_length, data_length):
        return (
            filename_length.to_bytes(1, "big")
            + json_length.to_bytes(3, "big")
            + data_length.to_bytes(4, "big")
        )


if __name__ == "__main__":
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    client = Client(SERVER_ADDRESS, SERVER_PORT)
    client.start()
