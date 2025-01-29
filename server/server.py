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

    STREAM_RATE = 4096

    def start(self):
        # create socket
        sock = self.sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        dpath = "server/tmp"
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
                            data_length
                            if data_length <= self.STREAM_RATE
                            else self.STREAM_RATE
                        )
                        f.write(data)
                        print("recieved {} bytes".format(len(data)))
                        data_length -= len(data)
                        print(data_length)

                print("Finished downloading the file from client.")

                filename = os.path.basename(request["filename"])
                process = request["process"]
                params = request["params"]

                video_process = VideoProcess(process, params, dpath, filename)
                output = video_process.execute()

                if output:
                    self.send_file(conn, output, process)
                else:
                    raise Exception("Send file to client failed")

            except Exception as e:
                print(e)
                self.send_error(conn, e)

            finally:
                shutil.rmtree(dpath)
                print("Closing current connection")
                conn.close()

    def send_file(self, conn, filepath, process):
        try:
            with open(filepath, "rb") as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                f.seek(0, 0)

                filename = os.path.basename(f.name)
                _, ext = os.path.splitext(filename)
                media_type = ext[1:]

                response = {"filename": filename, "process": process}
                response_json = json.dumps(response)
                print(response_json)
                response_json_bits = response_json.encode("utf-8")

                media_type_bits = media_type.encode("utf-8")

                header = self.mmp_header(
                    len(response_json), len(media_type_bits), filesize
                )

                conn.send(header)
                conn.send(response_json_bits)
                conn.send(media_type_bits)

                payload = f.read(4096)
                while payload:
                    print("Sending...")
                    conn.send(payload)
                    payload = f.read(4096)

        except Exception as e:
            print(e)
            self.send_error(conn, e)

    def send_error(self, conn, error):
        response = {"error_code": error.__class__.__name__, "error_description": error}
        response_json = json.dumps(response)
        response_json_bits = response_json.encode("utf-8")
        header = self.mmp_header(len(response_json), 0, 0)

        conn.send(header)
        conn.send(response_json_bits)

    def mmp_header(self, json_length, media_type_length, payload_length):
        return (
            json_length.to_bytes(2, "big")
            + media_type_length.to_bytes(1, "big")
            + payload_length.to_bytes(5, "big")
        )


if __name__ == "__main__":
    SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    server = Server(SERVER_ADDRESS, SERVER_PORT)
    server.start()
