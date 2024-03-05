import json
from utils import *


class JsonHandler:

    def __init__(self, output_file_path, old_download_list=None, pharmit_json=None):
        self.output_file_path = output_file_path
        self.old_download_list = old_download_list
        if pharmit_json:
            with open(pharmit_json, 'r') as file:
                pharmit_json = json.load(file)
            self.session = pharmit_json
        else:
            self.session = self.load_json()
        self._pharma_set_parameters()
        self.new_sessions_list = []

    def __str__(self):
        pharma_string = ""
        for index, pharmacophore in enumerate(self.session["points"]):
            pharma_name = pharmacophore["name"]
            if pharma_name == "InclusionSphere":
                continue
            pharma_coord = f"{pharmacophore['x']}, {pharmacophore['y']}, {pharmacophore['z']}"
            pharma_status = pharmacophore["enabled"]
            _pharma_switch = "[on]" if pharma_status else "[off]"
            pharma_string += f"[{index + 1}]{_pharma_switch}---{pharma_name}({pharma_coord})\n"

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

    def _pharma_switch(self, switch_number: int):
        button = self.session["points"][switch_number-1]
        button["enabled"] = not button["enabled"]

    def _pharma_set_parameters(self):
        self.session["minMolWeight"] = 300
        self.session["maxMolWeight"] = 700
        self.session["maxlogp"] = 7
        self.session["maxrotbonds"] = 7

    @staticmethod
    def _generate_points_list(sphere_tuple: tuple):
        points = []
        for sphere in sphere_tuple:
            point = {
                "name": sphere.interaction_type,
                "hasvec": False,
                "x": sphere.x,
                "y": sphere.y,
                "z": sphere.z,
                "radius": sphere.radius,
                "enabled": True,
                "vector_on": 0,
                "svector": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "minsize": "",
                "maxsize": "",
                "selected": False}
            points.append(point)
        return points

    def write_points(self, sphere_list: list):
        for sphere_tuple in sphere_list:
            new_session = self.session.copy()
            new_session["points"] = self._generate_points_list(sphere_tuple)
            self.new_sessions_list.append(new_session)

    def create_json(self, return_list=False):
        modified_json_path_list = []
        if return_list:
            for index, new_session in enumerate(self.new_sessions_list):
                modified_json_path = f"{self.output_file_path}/new_session{index+1}.json"
                with open(modified_json_path, 'w') as file:
                    json.dump(new_session, file)
                modified_json_path_list.append(modified_json_path)
            return modified_json_path_list
        else:
            modified_json_path = f"{self.output_file_path}/new_session.json"
            with open(modified_json_path, 'w') as file:
                json.dump(self.session, file)
            return modified_json_path
