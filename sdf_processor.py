import utils
import os


class SdfProcessor:
    def __init__(self, minimize_count):
        self.minimize_count = minimize_count
        self.sdf_files = []

    def _get_sdfs(self):
        last_files = utils.get_last_files('minimized_results')
        files_path = f"{os.getcwd()}/files"
        if len(last_files) != self.minimize_count:
            n = len(last_files) - self.minimize_count
            last_files = last_files[:n-1]
        for file in last_files:
            utils.transfer_to_folder(file, files_path, 'cp')
            file_name = utils.get_file_name(file)
            zipped_path = f"{files_path}/{file_name}"
            unzipped_path = utils.unzip(zipped_path)
            self.sdf_files.append(unzipped_path)

    def run(self):
        self._get_sdfs()


if __name__ == '__main__':
    sdf = SdfProcessor(9)
    sdf.run()
