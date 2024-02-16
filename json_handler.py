import json
import os
import utils


class JsonHandler:

    def __init__(self, output_file_path, pharmit_json=None):
        self.output_file_path = output_file_path
        if pharmit_json:
            self.session = pharmit_json
        else:
            self.session = self.load_json()

    def load_json(self):
        session_download_path, dlist = utils.get_last_files('pharmit*.json*')
        session_file = utils.get_file_name(session_download_path)
        utils.transfer_to_folder(session_download_path, self.output_file_path,  'cp')

        with open(f"{self.output_file_path}/{session_file}", 'r') as file:
            session = json.load(file)

        utils.check_session(session)
        return session

    def pharma_switch(self, switch_number: int):
        button = self.session["points"][switch_number-1]
        button["enabled"] = not button["enabled"]

    def create_json(self):
        modified_json_path = f"{self.output_file_path}/new_session.json"
        with open(modified_json_path, 'w') as file:
            json.dump(self.session, file)
        return modified_json_path


if __name__ == '__main__':
    #phc = PharmitControl()
    #jsh = JsonHandler()
    pass
