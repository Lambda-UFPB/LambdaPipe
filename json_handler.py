import json
import os


class JsonHandler:
    def __init__(self):
        cmd_1 = "xdg-user-dir DOWNLOAD"
        download_path = os.popen(cmd_1).read()
        download_path = download_path.replace("\n", "")
        new_path = f"{os.getcwd()}/files"
        cmd_2 = f"mv {download_path}/pharmit.json {new_path}"
        os.system(cmd_2)
        with open(f"{new_path}/pharmit.json", 'r') as file:
            self.session = json.load(file)

    def _pharma_switch(self):
        for i in range(4, 20):
            self.session["points"][i]["enabled"] = False

    def create_json(self):
        self._pharma_switch()
        with open('/home/kdunorat/Documentos/LambdaPipe/files/file_1.json', 'w') as file:
            json.dump(self.session, file)


if __name__ == '__main__':
    jsh = JsonHandler()
    jsh.create_json()
