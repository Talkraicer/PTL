import os.path

import pandas as pd
import xml.etree.ElementTree as ET
from results.results_utils import split_all_parts
import warnings

warnings.filterwarnings("ignore")
import pickle


class ResultsParser:
    def __init__(self, exp_file, PTL_lanes, period=60):
        self.tripinfo_file = exp_file + "_tripinfo.xml"
        self.lanes_file = exp_file + "_lanes.xml"
        parts = split_all_parts(exp_file)
        self.policy_name = parts[-1]
        self.seed = int(parts[-2])
        self.av_rate = float(parts[-3])
        self.demand_name = str(parts[-4])

        self.PTL_lanes = PTL_lanes
        self.tripinfo_df = self._parse_tripinfo_output()

        self.occupancy_df, self.speed_df, self.density_df, self.num_vehs = {}, {}, {}, {}
        self.period = period
        self._parse_lanes_output()

        self.lanes_metrics_map = {"speed": self.speed_df, "occupancy": self.occupancy_df,
                                  "num_vehs": self.num_vehs, "density": self.density_df}

        pickle.dump(self, open(exp_file + "_ResultsParser.pkl", "wb"))

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
        df["departDelay"] = df.departDelay.astype(float)
        df["totalDelay"] = df.departDelay.astype(float) + df.timeLoss.astype(float)
        df["vType"] = df["vType"].apply(lambda x: x.split("@")[0])
        df["numPass"] = df["vType"].apply(lambda x: x.split("_")[1]).astype(int)
        df["vType"] = df["vType"].apply(lambda x: x.split("_")[0])
        df["duration"] = df["duration"].astype(float)
        df["passDelay"] = df["totalDelay"] * df["numPass"]
        df["passDuration"] = df["duration"] * df["numPass"]
        df["timeLoss"] = df["timeLoss"].astype(float)
        return df[["id", "vType", "numPass", "duration", "totalDelay", "passDelay", "passDuration", "timeLoss",
                   "departDelay"]]

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

    def mean_metric(self, metric, vType=None, baseline=None):
        """
        Calculate the mean of a metric for all vehicles in the simulation
        :param metric: the metric to calculate the mean for
        :param vType: the vehicle type to calculate the mean for
        :param baseline: another ResultsParser object to compare the metric to
        :return: a float representing the mean of the metric
        """
        self._validate_tripinfo_metric(metric)
        assert not (vType and baseline), "Cannot compare vehicle type and baseline"
        tripinfo = self.tripinfo_df
        if vType:
            tripinfo = self.tripinfo_df[self.tripinfo_df["vType"] == vType]
            metric_data = tripinfo[metric]
        elif baseline:
            baseline_tripinfo = baseline.tripinfo_df
            # make sure ids are the same"
            joined_baseline = pd.merge(tripinfo, baseline_tripinfo, on="id", suffixes=("_new", "_baseline"))
            assert len(joined_baseline) == len(tripinfo), "Baseline and new tripinfo files have different ids"
            metric_data = ((joined_baseline[metric + "_new"] - joined_baseline[metric + "_baseline"])/joined_baseline[metric + "_baseline"]) * 100
        else:
            metric_data = tripinfo[metric]
        if "pass" in metric:
            return metric_data.sum() / tripinfo["numPass"].sum()
        return metric_data.mean()

    def num_vehs_lanes(self, PTL=False):
        """
        Calculate the number of vehicles in all lanes
        :return: a dictionary with the lanes as keys and the number of vehicles in each lane as values
        """
        if PTL:
            return self.num_vehs[self.PTL_lanes].apply(sum, axis=1)
        return self.num_vehs.apply(sum, axis=1)

    def mean_speed_lanes(self, PTL=False):
        """
        Calculate the mean speed of vehicles in all lanes
        :return: a dictionary with the lanes as keys and the mean speed of vehicles in each lane as values
        """
        speed_df = self.speed_df[self.PTL_lanes] if PTL else self.speed_df
        num_vehs = self.num_vehs[self.PTL_lanes] if PTL else self.num_vehs
        # multiply speed by number of vehicles in each lane
        weighted_speed = speed_df.astype(float) * num_vehs
        avg_speed = weighted_speed.apply(sum, axis=1) / num_vehs.apply(sum, axis=1)
        return avg_speed.fillna(0).values

    def mean_occupancy_lanes(self, PTL=False):
        """
        Calculate the mean occupancy of vehicles in all lanes
        :return: a dictionary with the lanes as keys and the mean occupancy of vehicles in each lane as values
        """
        occupancy_df = self.occupancy_df[self.PTL_lanes] if PTL else self.occupancy_df

        return occupancy_df.fillna(0).mean(axis=1).values


    def mean_plot_metric(self, metric, PTL=False):
        if metric == "speed":
            return self.mean_speed_lanes(PTL)
        elif metric == "num_vehs":
            return self.num_vehs_lanes(PTL)
        elif metric == "occupancy":
            return self.mean_occupancy_lanes(PTL)
        else:
            raise Exception("Metric not supported")


if __name__ == '__main__':
    tripinfo_file = "../SUMO/outputs/Test/0/0/Nothing_tripinfo.xml"
    lanes_file = "../SUMO/outputs/Test/0/0/Nothing_lanes.xml"
    parser = ResultsParser(tripinfo_file, lanes_file)
    print(parser.mean_speed_all_lanes())
