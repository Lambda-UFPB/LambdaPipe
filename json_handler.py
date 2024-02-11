import json
import os
import utils


class JsonHandler:
    def __init__(self):
        self.session = self._load_json()

    @staticmethod
    def _load_json():
        download_path = utils.get_last_files('pharmit*.json')
        files_path = f"{os.getcwd()}/files"
        session_file = utils.get_file_name(download_path)
        utils.transfer_to_folder(download_path, files_path,  'cp')

        with open(f"{files_path}/{session_file}", 'r') as file:
            session = json.load(file)

        return session

    def _pharma_switch(self):
        # Tá desligada
        for switch in self.session["points"][4:19]:
            switch["enabled"] = False

    def create_json(self):
        # self._pharma_switch()
        modified_json_path = f"{os.getcwd()}/files/file_1.json"
        with open(modified_json_path, 'w') as file:
            json.dump(self.session, file)
        return modified_json_path


if __name__ == '__main__':
    jsh = JsonHandler()
    jsh.create_json()
