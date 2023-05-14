import json
import os
import utils


class JsonHandler:
    def __init__(self):
        self.session = self._load_json()

    @staticmethod
    def _load_json():
        download_path, new_path = utils.get_path("pharmit.json")
        cmd_2 = f"mv {download_path} {new_path}"
        while True:
            if os.path.exists(download_path):
                os.system(cmd_2)
                with open(f"{new_path}/pharmit.json", 'r') as file:
                    session = json.load(file)
                    break
        return session

    def _pharma_switch(self):
        for i, switch in enumerate(self.session["points"]):
            switch["enabled"] = False

    def create_json(self):
        self._pharma_switch()
        with open('/home/kdunorat/Documentos/LambdaPipe/files/file_1.json', 'w') as file:
            json.dump(self.session, file)


if __name__ == '__main__':
    jsh = JsonHandler()
    jsh.create_json()

