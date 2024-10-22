import os
from results.parse_exp_results import ResultsParser
import pandas as pd
import numpy as np
from multiprocessing import Pool
from tqdm import tqdm

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
                    exp_path = seed_folder + "/"+experiment
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

def process_combination(demand, policy, av_rate, vType, metric, results_parsers):
    av_rate_parsers = list(filter(lambda x: x.av_rate == av_rate and x.demand_name == demand
                                          and x.policy_name == policy, results_parsers))
    if vType:
        result = {}
        for v in vType:
            vtype_results = calc_metric_over_simulations(av_rate_parsers, metric, v)
            result[(policy, demand, av_rate, v)] = {"mean": vtype_results["mean"], "std": vtype_results["std"]}
        return result
    else:
        av_rate_results = calc_metric_over_simulations(av_rate_parsers, metric)
        return {(policy, demand, av_rate): {"mean": av_rate_results["mean"], "std": av_rate_results["std"]}}

# Function to parallelize

def create_metric_results_table(results_parsers, metric,
                                demands = None, av_rates=None,policies=None,
                                vType=False):
    """
    Create a table with the mean and std of a metric for all the results parsers
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :return: a dataframe of columns demand, subcolumns of av_rates, (optional) subcolumns of vTypes,
                subcolumns mean and std, and rows of policies
    """
    demands = list(set(map(lambda x: x.demand_name, results_parsers))) if not demands else demands
    av_rates = list(set(map(lambda x: x.av_rate, results_parsers))) if not av_rates else av_rates
    policies = list(set(map(lambda x: x.policy_name, results_parsers))) if not policies else policies

    if vType:
        vTypes = ["AV", "HD", "Bus"]
        df = pd.DataFrame(index=policies, columns=pd.MultiIndex.from_product([demands,av_rates, vTypes, ["mean", "std"]]))
    else:
        df = pd.DataFrame(index=policies, columns=pd.MultiIndex.from_product([demands,av_rates, ["mean", "std"]]))

    pool = Pool()
    tasks = []
    for demand in demands:
        for policy in policies:
            for av_rate in av_rates:
                tasks.append((demand, policy, av_rate, vType, metric, results_parsers))

    with Pool() as pool:
        # Use imap instead of starmap for progress tracking
        results = pool.imap_unordered(process_combination, tasks)
        for result in tqdm(results, total=len(tasks)):
            for key, value in result.items():
                if len(key) == 4:  # If vType was used
                    policy, demand, av_rate, v = key
                    df.loc[policy, (demand, av_rate, v, "mean")] = value["mean"]
                    df.loc[policy, (demand, av_rate, v, "std")] = value["std"]
                else:
                    policy, demand, av_rate = key
                    df.loc[policy, (demand, av_rate, "mean")] = value["mean"]
                    df.loc[policy, (demand, av_rate, "std")] = value["std"]


    return df

if __name__ == '__main__':
    parsers = get_all_results_parsers("SUMO/outputs")
    create_metric_results_table(parsers,"passDelay", vType=True, demands=["DailyDemand"]).to_csv("passDelay.csv")