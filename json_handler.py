import json
import os


class JsonHandler:
    def __init__(self):
        self.session = self._load_json()

    @staticmethod
    def _get_path():
        cmd_1 = "xdg-user-dir DOWNLOAD"
        download_path = os.popen(cmd_1).read()
        download_path = download_path.replace("\n", "")
        download_path = download_path + "/pharmit.json"
        new_path = f"{os.getcwd()}/files"
        return download_path, new_path

    @staticmethod
    def _load_json():
        download_path, new_path = JsonHandler._get_path()
        cmd_2 = f"mv {download_path} {new_path}"
        while True:
            if os.path.exists(download_path):
                os.system(cmd_2)
                with open(f"{new_path}/pharmit.json", 'r') as file:
                    session = json.load(file)
                    break
        return session

    @staticmethod
    def check_existence():
        download_path, _ = JsonHandler._get_path()
        if os.path.exists(download_path):
            os.remove(download_path)

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
