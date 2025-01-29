import socket
import sys
import os
import json

from dotenv import load_dotenv

load_dotenv()

from question import Question


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
            answer = Question.video_process_question()
            filepath = answer["filepath"]

            with open(filepath, "rb") as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, 0)

                if filesize > pow(2, 32):
                    raise Exception("File must be below 4GB.")

                filename = os.path.basename(f.name)
                _, ext = os.path.splitext(filename)
                media_type = ext[1:]
                if media_type != "mp4":
                    raise Exception("File type must be mp4.")

                request = {
                    "filename": filename,
                    "process": answer["process"],
                    "params": answer["params"],
                }
                request_json = json.dumps(request)
                request_json_bits = request_json.encode("utf-8")

                media_type_bits = media_type.encode("utf-8")

                header = self.mmp_header(
                    len(request_json), len(media_type_bits), filesize
                )

                sock.send(header)
                sock.send(request_json_bits)
                sock.send(media_type_bits)

                data = f.read(4096)
                while data:
                    print("Sending...")
                    sock.send(data)
                    data = f.read(4096)

        finally:
            print("closing socket")
            sock.close()

    def protocol_header(self, request_length, json_length, data_length):
        return (
            request_length.to_bytes(1, "big")
            + json_length.to_bytes(3, "big")
            + data_length.to_bytes(4, "big")
        )

    def mmp_header(self, json_length, media_type_length, payload_length):
        return (
            json_length.to_bytes(2, "big")
            + media_type_length.to_bytes(1, "big")
            + payload_length.to_bytes(5, "big")
        )


if __name__ == "__main__":
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    client = Client(SERVER_ADDRESS, SERVER_PORT)
    client.start()
