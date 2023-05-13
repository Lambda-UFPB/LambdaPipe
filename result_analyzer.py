import utils


class ResultAnalyzer:
    def __init__(self):
        file = "minimized_results.sdf.gz"
        zipped_path, _ = utils.get_path(file)
        utils.remove_previous(file)
        file_unzip = file.replace(".gz", "")
        utils.remove_previous(file_unzip)
        unzipped_path = utils.unzip(zipped_path)
        # mexer no json



