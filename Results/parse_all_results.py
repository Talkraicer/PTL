import os
from Results.parse_exp_results import ResultsParser
import pandas as pd
import numpy as np


def get_all_results_parsers(outputs_folder):
    results_parsers = []
    for demand in os.listdir(outputs_folder):
        demand_folder = os.path.join(outputs_folder,demand)
        for av_rate in os.listdir(demand_folder):
            av_rate_folder = os.path.join(demand_folder, av_rate)
            for seed in os.listdir(av_rate_folder):
                seed_folder = os.path.join(av_rate_folder, seed)
                experiments = list(set(map(lambda x: "_".join(x.split(".")[0].split("_")[:-1]),
                                           os.listdir(seed_folder))))
                for experiment in experiments:
                    exp_path = seed_folder + "\\"+experiment
                    results_parsers.append(ResultsParser(exp_path))
    return results_parsers

def calc_mean_std(df):
    # Calculate mean and standard deviation of each column
    means = df.mean()
    stds = df.std()

    # Create a new DataFrame with the required structure
    return pd.DataFrame({
        'mean': means,
        'std': stds}).T


def calc_metric_over_simulations(results_parsers, metric, vType=None):
    """
    Calculate the mean and std of a metric for all the results parsers
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :param PTL: weather to calculate the metric for PTL and not PTL separately
    :return: a dataframe with the mean and std of the metric for all the results parsers
    """
    means = [rp.mean_metric(metric, vType) for rp in results_parsers]
    return {"mean": np.mean(means), "std": np.std(means)}


def create_metric_results_table(results_parsers, metric, vType=False):
    """
    Create a table with the mean and std of a metric for all the results parsers
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :return: a dataframe of columns av_rate, (optional) subcolumns of vTypes,
                subcolumns mean and std, and rows of policies
    """
    av_rates = list(set(map(lambda x: x.av_rate, results_parsers)))
    policies = list(set(map(lambda x: x.policy_name, results_parsers)))
    if vType:
        vTypes = ["AV", "HD", "Bus"]
        df = pd.DataFrame(index=policies, columns=pd.MultiIndex.from_product([av_rates, vTypes, ["mean", "std"]]))
    else:
        df = pd.DataFrame(index=policies, columns=pd.MultiIndex.from_product([av_rates, ["mean", "std"]]))
    for policy in policies:
        policy_parsers = list(filter(lambda x: x.policy_name == policy, results_parsers))
        for av_rate in av_rates:
            av_rate_parsers = list(filter(lambda x: x.av_rate == av_rate, policy_parsers))
            if vType:
                for vType in vTypes:
                    vtype_results = calc_metric_over_simulations(av_rate_parsers, metric, vType)
                    df.loc[policy, (av_rate, vType, "mean")] = vtype_results["mean"]
                    df.loc[policy, (av_rate, vType, "std")] = vtype_results["std"]
            else:
                df.loc[policy, (av_rate, "mean")] = calc_metric_over_simulations(av_rate_parsers, metric)["mean"]
                df.loc[policy, (av_rate, "std")] = calc_metric_over_simulations(av_rate_parsers, metric)["std"]
    return df

if __name__ == '__main__':
    parsers = get_all_results_parsers("../SUMO/outputs")
    create_metric_results_table(parsers, "passDelay", vType=True).to_csv("passDelay.csv")