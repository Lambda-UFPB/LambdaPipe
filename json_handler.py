import json
import os
import utils


class JsonHandler:

    def __init__(self, pharmit_json=None):
        if pharmit_json:
            self.session = pharmit_json
        else:
            self.session = self.load_json()

    @staticmethod
    def load_json():
        download_path = utils.get_last_files('pharmit*.json')
        files_path = f"{os.getcwd()}/files"
        session_file = utils.get_file_name(download_path)
        utils.transfer_to_folder(download_path, files_path,  'cp')

        with open(f"{files_path}/{session_file}", 'r') as file:
            session = json.load(file)

        return session

    def pharma_switch(self, switch_number: int):
        # Tá desligada
        button = self.session["points"][switch_number-1]
        button["enabled"] = not button["enabled"]

    def create_json(self):
        modified_json_path = f"{os.getcwd()}/files/new_session.json"
        with open(modified_json_path, 'w') as file:
            json.dump(self.session, file)
        return modified_json_path


if __name__ == '__main__':
    #phc = PharmitControl()
    #jsh = JsonHandler()
    pass
