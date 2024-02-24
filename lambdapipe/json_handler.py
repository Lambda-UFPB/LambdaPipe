import json
from utils import *


class JsonHandler:

    def __init__(self, output_file_path, old_download_list, pharmit_json=None):
        self.output_file_path = output_file_path
        self.old_download_list = old_download_list
        if pharmit_json:
            self.session = pharmit_json
        else:
            self.session = self.load_json()

    def __str__(self):
        pharma_string = ""
        for index, pharmacophore in enumerate(self.session["points"]):
            pharma_name = pharmacophore["name"]
            if pharma_name == "InclusionSphere":
                continue
            pharma_coord = f"{pharmacophore['x']}, {pharmacophore['y']}, {pharmacophore['z']}"
            pharma_status = pharmacophore["enabled"]
            pharma_switch = "[on]" if pharma_status else "[off]"
            pharma_string += f"[{index + 1}]{pharma_switch}---{pharma_name}({pharma_coord})\n"

        return pharma_string

    def load_json(self):
        session_download_path = get_last_files(file_pattern='pharmit*.json*',
                                               old_download_list=self.old_download_list)
        session_file = get_file_name(session_download_path)
        transfer_to_folder(session_download_path, self.output_file_path, 'cp')

        with open(f"{self.output_file_path}/{session_file}", 'r') as file:
            session = json.load(file)

        check_session(session)
        return session

    def pharma_switch(self, switch_number: int):
        button = self.session["points"][switch_number-1]
        button["enabled"] = not button["enabled"]

    def create_json(self):
        modified_json_path = f"{self.output_file_path}/new_session.json"
        with open(modified_json_path, 'w') as file:
            json.dump(self.session, file)
        return modified_json_path
