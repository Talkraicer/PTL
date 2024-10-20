import os


class Logger:
    def __init__(self, output_file_path, output_file_name, dict_keys):
        self.output_file = os.path.join(output_file_path, output_file_name + ".csv")
        self.dict_keys = dict_keys

    def log(self, state_dict):
        pass

    def get_df(self):
        pass