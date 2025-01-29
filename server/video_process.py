import os
import subprocess
import datetime


class VideoProcess:
    def __init__(self, process, params, inputFile, outputDir):
        self.process = process
        self.params = params
        self.inputFile = inputFile
        self.outputDir = outputDir

    def compress(self, input, output):
        subprocess.call("ffmpeg -i " + input + " -crf 18 " + output, shell=True)

    def change_resolution(self, input, output):
        if self.params["resolution"] is not None:
            subprocess.call(
                "ffmpeg -i "
                + input
                + " -vf scale=-1:"
                + self.params["resolution"]
                + " "
                + output,
                shell=True,
            )

    def change_aspect_ratio(self, input, output):
        if self.params["aspect_ratio"] is not None:
            subprocess.call(
                "ffmpeg -i "
                + input
                + " -c copy -aspect "
                + self.params["aspect_ratio"]
                + " "
                + output,
                shell=True,
            )

    def convert_to_audio(self, input, output):
        subprocess.call(
            "ffmpeg -i " + input + " -f mp3 -ab 192000 -vn " + output,
            shell=True,
        )

    def create_gif(self, input, output):
        if (
            self.params["gif"]["start"] is not None
            and self.params["gif"]["end"] is not None
        ):
            subprocess.call(
                "ffmpeg -i "
                + input
                + " -ss "
                + self.params["gif"]["start"]
                + " -t "
                + self.params["gif"]["end"]
                + " "
                + output,
                shell=True,
            )

    def execute(self):
        process_table = {
            "compress": self.compress,
            "change_resolution": self.change_resolution,
            "change_aspect_ratio": self.change_aspect_ratio,
            "convert_to_audio": self.convert_to_audio,
            "create_gif": self.create_gif,
        }
        root, ext = os.path.splitext(os.path.basename(self.inputFile))
        now = datetime.datetime.now().strftime("%y%m%d")

        if self.process == "convert_to_audio":
            ext = ".mp3"
        elif self.process == "create_gif":
            ext = ".gif"

        outputFile = self.outputDir + "/" + root + "_" + self.process + "_" + now + ext

        try:
            return process_table[self.process](self.inputFile, outputFile)
        except:
            print("request error")
            pass
