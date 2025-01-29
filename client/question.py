import questionary
from questionary import Choice, Validator, ValidationError


class Question:
    @staticmethod
    def video_process_question():
        answer = {
            "filepath": None,
            "process": None,
            "params": {
                "resolution": None,
                "aspect_ratio": None,
                "gif": {"start": None, "end": None},
            },
        }

        answer["filepath"] = questionary.path("Type in a file to upload").ask()

        answer["process"] = questionary.select(
            "Select process for file ",
            choices=[
                Choice(title="compress video file", value="compress"),
                Choice(title="change video resolution", value="change_resolution"),
                Choice(title="change video aspect ratio", value="change_aspect_ratio"),
                Choice(title="convert video to audio", value="convert_to_audio"),
                Choice(title="create GIF or WEBM on time range", value="create_gif"),
            ],
        ).ask()

        is_change_resolution = answer["process"] == "change_resolution"
        is_change_aspect_ratio = answer["process"] == "change_aspect_ratio"
        is_create_gif = answer["process"] == "create_gif"

        answer["params"]["resolution"] = (
            questionary.select(
                "Select resolution",
                choices=[
                    Choice(title="1080p", value="1080"),
                    Choice(title="720p", value="720"),
                    Choice(title="480p", value="480"),
                    Choice(title="360p", value="360"),
                    Choice(title="240p", value="240"),
                ],
            )
            .skip_if(not is_change_resolution)
            .ask()
        )

        answer["params"]["aspect_ratio"] = (
            questionary.select("Select aspect ratio", choices=["16:9", "4:3"])
            .skip_if(not is_change_aspect_ratio)
            .ask()
        )

        answer["params"]["gif"]["start"] = (
            questionary.text("Type start time for gif", validate=IntegerValidator)
            .skip_if(not is_create_gif)
            .ask()
        )
        answer["params"]["gif"]["end"] = (
            questionary.text("Type end time for gif", validate=IntegerValidator)
            .skip_if(not is_create_gif)
            .ask()
        )

        return answer


class IntegerValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except:
            raise ValidationError(
                message=f"{document.text} is not valid integer.",
                cursor_position=len(document.text),
            )
