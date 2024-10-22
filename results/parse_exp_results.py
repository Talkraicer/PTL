import os.path

import pandas as pd
import xml.etree.ElementTree as ET
from results.results_utils import split_all_parts
import warnings
warnings.filterwarnings("ignore")
import pickle
class ResultsParser:
    def __init__(self, exp_file, period=60):
        self.tripinfo_file = exp_file + "_tripinfo.xml"
        self.lanes_file = exp_file + "_lanes.xml"
        parts = split_all_parts(exp_file)
        self.policy_name = parts[-1]
        self.seed = int(parts[-2])
        self.av_rate = float(parts[-3])
        self.demand_name = str(parts[-4])

        if os.path.exists(exp_file+"_tripinfo.pkl"):
            self.tripinfo_df = pd.read_pickle(exp_file+"_tripinfo.pkl")
        else:
            self.tripinfo_df = self._parse_tripinfo_output()
            self.tripinfo_df.to_pickle(exp_file+"_tripinfo.pkl")

        self.PTL_lanes = ["E1_4", "E2_3", "E3_4", "E4_3", "E5_4", "E6_3"]
        self.occupancy_df, self.speed_df, self.density_df, self.num_vehs = {}, {}, {}, {}
        self.period = period
        self._parse_lanes_output()

        self.lanes_metrics_map = {"speed": self.speed_df, "occupancy": self.occupancy_df,
                                  "num_vehs": self.num_vehs, "density": self.density_df}

        pickle.dump(self, open(exp_file + ".pkl", "wb"))


    def _parse_tripinfo_output(self):
        """
        Parse the XML file into pd dataframe`
        :param output_file: path to the output file (XML)
        :return: pd dataframe of the output file, with the following columns:
                    ['id', 'vType', 'numPass', 'duration, 'totalDelay', 'passDelay', 'passDuration']
        """
        tree = ET.parse(self.tripinfo_file)
        root = tree.getroot()

        dict = {"duration": [], "departDelay": [], "routeLength": [], "vType": [], "timeLoss": [], "id": []}
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
        df["passDuration"] = df["duration"] * df["numPass"]
        return df[["id", "vType", "numPass", "duration", "totalDelay", "passDelay", "passDuration"]]

    def _append_all_dataframes(self, key, value):
        if key not in self.speed_df:
            self.speed_df[key] = []
            self.occupancy_df[key] = []
            self.density_df[key] = []
            self.num_vehs[key] = []
            if value is None:
                return
        self.speed_df[key].append(value)
        self.occupancy_df[key].append(value)
        self.density_df[key].append(value)
        self.num_vehs[key].append(value)

    def _switch_all_dataframes(self):
        self.speed_df = pd.DataFrame(self.speed_df).set_index("time").fillna(0)
        self.occupancy_df = pd.DataFrame(self.occupancy_df).set_index("time").fillna(0)
        self.density_df = pd.DataFrame(self.density_df).set_index("time").fillna(0)
        self.num_vehs = pd.DataFrame(self.num_vehs).set_index("time").fillna(0)

    def _parse_lanes_output(self):
        """
        Parse the XML file into pd dataframe`
        :param output_file: path to the output file (XML)
        :return: pd dataframe of the output file, with the following columns:
        """
        tree = ET.parse(self.lanes_file)
        root = tree.getroot()
        for interval in root.findall('interval'):
            time = interval.get('end')
            self._append_all_dataframes("time", time)
            for edge in interval.findall('edge'):
                for lane in edge.findall('lane'):
                    lane_id = lane.get('id')
                    if lane_id not in self.speed_df:
                        self._append_all_dataframes(lane_id, None)
                    self.speed_df[lane_id].append(lane.get('speed'))
                    self.occupancy_df[lane_id].append(lane.get('occupancy'))
                    self.density_df[lane_id].append(lane.get('density'))
                    self.num_vehs[lane_id].append(float(lane.get('sampledSeconds')) / self.period)
        self._switch_all_dataframes()

    def _validate_tripinfo_metric(self, metric):
        assert metric in self.tripinfo_df.columns, f"Metric {metric} is not in the sumo output file"

    def mean_metric(self, metric, vType=None):
        """
        Calculate the mean of a metric for all vehicles in the simulation
        :param metric: the metric to calculate the mean for
        :return: a float representing the mean of the metric
        """
        self._validate_tripinfo_metric(metric)
        tripinfo = self.tripinfo_df
        if vType:
            tripinfo = self.tripinfo_df[self.tripinfo_df["vType"] == vType]
        if "pass" in metric:
            return tripinfo[metric].mean()/ tripinfo["numPass"].sum()
        return tripinfo[metric].mean()


    def num_vehs_PTL(self):
        """
        Calculate the number of vehicles in the PTL lanes
        :return: a dictionary with the PTL lanes as keys and the number of vehicles in each lane as values
        """
        return self.num_vehs[self.PTL_lanes].apply(sum, axis=1)

    def num_vehs_all_lanes(self):
        """
        Calculate the number of vehicles in all lanes
        :return: a dictionary with the lanes as keys and the number of vehicles in each lane as values
        """
        return self.num_vehs.apply(sum, axis=1)

    def mean_speed_PTL(self):
        """
        Calculate the mean speed of vehicles in the PTL lanes
        :return: a dictionary with the PTL lanes as keys and the mean speed of vehicles in each lane as values
        """
        # multiply speed by number of vehicles in each lane
        weighted_speed = self.speed_df[self.PTL_lanes].astype(float)*self.num_vehs[self.PTL_lanes]
        avg_speed = weighted_speed.apply(sum,axis=1) / self.num_vehs[self.PTL_lanes].apply(sum,axis=1)
        return avg_speed.fillna(0)

    def mean_speed_all_lanes(self):
        """
        Calculate the mean speed of vehicles in all lanes
        :return: a dictionary with the lanes as keys and the mean speed of vehicles in each lane as values
        """
        # multiply speed by number of vehicles in each lane
        weighted_speed = self.speed_df.astype(float)*self.num_vehs
        avg_speed = weighted_speed.apply(sum,axis=1) / self.num_vehs.apply(sum,axis=1)
        return avg_speed.fillna(0)

if __name__ == '__main__':
    tripinfo_file = "../SUMO/outputs/Test/0/0/Nothing_tripinfo.xml"
    lanes_file = "../SUMO/outputs/Test/0/0/Nothing_lanes.xml"
    parser = ResultsParser(tripinfo_file, lanes_file)
    print(parser.mean_speed_all_lanes())