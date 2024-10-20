import pandas as pd
import xml.etree.ElementTree as ET
from Loggers.Logger import Logger


class ResultsParser:
    def __init__(self, sumo_output_file, logger_output_file=None, logger=None, av_rate=None):
        assert logger_output_file is not None or logger is not None, "Either logger_output_file or logger must be provided"
        self.exp_name = sumo_output_file.split("/")[-1].split(".")[0]
        self.demand_name = self.exp_name.split("_")[0]
        self.policy_name = "_".join(self.exp_name.split("_")[1:])
        self.av_rate = av_rate

        self.sumo_output_file = sumo_output_file
        self.sumo_df = self._parse_sumo_output()

        if logger_output_file is not None:
            self.logger_output_file = logger_output_file
            self.logger_df = pd.read_csv(logger_output_file, delimiter=";")
        else:
            self.logger = logger
            self.logger_df = logger.get_df()

    def _parse_sumo_output(self):
        """
        Parse the XML file into pd dataframe`
        :param output_file: path to the output file (XML)
        :return: pd dataframe of the output file, with the following columns:
                    ['id', 'vType', 'numPass', 'duration, 'totalDelay', 'passDelay']
        """
        tree = ET.parse(self.sumo_output_file)
        root = tree.getroot()

        dict = {"duration": [], "departDelay": [], "routeLength": [], "vType": [], "timeLoss": [], "id": [],
                "depart": []}
        for tripinfo in root.findall('tripinfo'):
            for key in dict.keys():
                dict[key].append(tripinfo.get(key))
        df = pd.DataFrame(dict)
        df["totalDelay"] = df.departDelay.astype(float) + df.timeLoss.astype(float)
        df["vType"] = df["vType"].apply(lambda x: x.split("@")[0])
        df["numPass"] = df["vType"].apply(lambda x: x.split("_")[1]).astype(int)
        df["vType"] = df["vType"].apply(lambda x: x.split("_")[0])
        df["duration"] = df["duration"].astype(float)
        df["passDelay"] = df["totalDelay"] * df["numPass"]
        return df[["id", "vType", "numPass", "duration", "totalDelay", "passDelay"]]

    def _validate_metric(self, metric):
        assert metric in self.sumo_df.columns, f"Metric {metric} is not in the sumo output file"

    def mean_metric(self, metric):
        """
        Calculate the mean of a metric for all vehicles in the simulation
        :param metric: the metric to calculate the mean for
        :return: a float representing the mean of the metric
        """
        self._validate_metric(metric)
        return self.sumo_df[metric].mean().values[0]

    def mean_metric_vType(self, metric):
        """
        Calculate the mean of a metric for all vehicle types in the simulation
        :param metric: the metric to calculate the mean for
        :return: a dictionary with the vehicle types as keys and the mean of the metric for each vehicle type as values
        """
        self._validate_metric(metric)
        return self.sumo_df.groupby("vType")[metric].mean().to_dict()

    def mean_metric_PTL(self, metric):
        """
        Calculate the mean of a metric for vehicles that have been in the PTL and vehicles that have not been in the PTL
        :param metric: the metric to calculate the mean for
        :return: a dictionary with the mean of the metric for vehicles that have been in the PTL and vehicles that have not
        """
        self._validate_metric(metric)
        veh_ids_been_in_PTL = list(set(sum(self.logger_df['veh_ids_in_PTL'], [])))
        veh_ids_not_been_in_PTL = list(set(self.sumo_df['id']) - set(veh_ids_been_in_PTL))
        PTL_mean_vehicle_delay = self.sumo_df[self.sumo_df['id'].isin(veh_ids_been_in_PTL)][metric].mean().values[0]
        not_PTL_mean_vehicle_delay = self.sumo_df[self.sumo_df['id'].isin(veh_ids_not_been_in_PTL)][metric].mean().values[0]
        return {"been_in_PTL": PTL_mean_vehicle_delay, "not_been_in_PTL": not_PTL_mean_vehicle_delay}
