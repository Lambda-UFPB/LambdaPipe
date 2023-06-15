import json
import os
import utils


class JsonHandler:
    def __init__(self):
        self.session = self._load_json()

    @staticmethod
    def _load_json():
        download_path = utils.get_last_file()
        new_path = f"{os.getcwd()}/files"
        cmd_2 = f"cp '{download_path}' {new_path}"
        session_file = utils.get_file_name(download_path)
        os.system(cmd_2)
        with open(f"{new_path}/{session_file}", 'r') as file:
            session = json.load(file)

        return session

    def _pharma_switch(self):
        for switch in self.session["points"][4:19]:
            switch["enabled"] = False

    def create_json(self):
        self._pharma_switch()
        with open('/home/kdunorat/Documentos/LambdaPipe/files/file_1.json', 'w') as file:
            json.dump(self.session, file)


if __name__ == '__main__':
    jsh = JsonHandler()
    jsh.create_json()

