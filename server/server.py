import socket
import os
import json
import shutil

from dotenv import load_dotenv

load_dotenv()

from video_process import VideoProcess

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

                json_length = int.from_bytes(header[:2], "big")
                media_type_length = int.from_bytes(header[2:3], "big")
                data_length = int.from_bytes(header[3:], "big")
                stream_rate = 4096

                print(
                    "Received header from client. Byte lengths: JSON length {}, Media type length {}, Data Length {}".format(
                        json_length, media_type_length, data_length
                    )
                )

                request_json = conn.recv(json_length).decode("utf-8")
                request = json.loads(request_json)

                print("Request: {}".format(request))

                media_type = conn.recv(media_type_length).decode("utf-8")
                print("Media type: {}".format(media_type))

                if data_length == 0:
                    raise Exception("No data to read from client.")

                with open(os.path.join(dpath, request["filename"]), "wb+") as f:
                    while data_length > 0:
                        data = conn.recv(
                            data_length if data_length <= stream_rate else stream_rate
                        )
                        f.write(data)
                        print("recieved {} bytes".format(len(data)))
                        data_length -= len(data)
                        print(data_length)

                print("Finished downloading the file from client.")

                inputFile = dpath + "/" + request["filename"]
                outputDir = "output"
                if not os.path.exists(outputDir):
                    os.makedirs(outputDir)

                method = request["process"]
                params = request["params"]

                video_process = VideoProcess(method, params, inputFile, outputDir)
                video_process.execute()

            except Exception as e:
                print("Error:" + str(e))

            finally:
                shutil.rmtree(dpath)
                print("Closing current connection")
                conn.close()


if __name__ == "__main__":
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    server = Server(SERVER_ADDRESS, SERVER_PORT)
    server.start()
