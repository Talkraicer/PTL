import csv
import pandas as pd
import os
from Logger import Logger


class CSVLogger(Logger):
    def __init__(self, output_file_path, output_file_name, dict_keys):
        super().__init__(output_file_path, output_file_name, dict_keys)
        with open(self.output_file, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(list(dict_keys))

    def log(self, log_dict):
        with open(self.output_file, mode='a', newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([log_dict[key] for key in self.dict_keys])

    def get_df(self):
        return pd.read_csv(self.output_file, delimiter=";")