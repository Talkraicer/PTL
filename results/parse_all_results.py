import os
import pickle

from results.parse_exp_results import ResultsParser
import pandas as pd
import numpy as np
from multiprocessing import Pool
from tqdm import tqdm


def parse_experiment(exp_path):
    """Helper function to parse a single experiment path."""
    return ResultsParser(exp_path)


def get_all_results_parsers(outputs_folder, one_demand=None, one_av_rate=None):
    demands = os.listdir(outputs_folder) if not one_demand else [one_demand]

    tasks = []  # List to hold all tasks to be processed in parallel
    results_parsers = []
    for demand in demands:
        demand_folder = os.path.join(outputs_folder, demand)
        av_rates = os.listdir(demand_folder) if not one_av_rate else [one_av_rate]
        for av_rate in av_rates:
            av_rate_folder = os.path.join(demand_folder, av_rate)
            for seed in os.listdir(av_rate_folder):
                seed_folder = os.path.join(av_rate_folder, seed)
                experiments = list(set(map(lambda x: "_".join(x.split(".")[0].split("_")[:-1]),
                                           os.listdir(seed_folder))))
                for experiment in experiments:
                    exp_path = os.path.join(seed_folder, experiment)
                    if exp_path + "_ResultsParser.pkl" in os.listdir(seed_folder):
                        results_parsers.append(pickle.load(open(exp_path + "_ResultsParser.pkl", "rb")))
                    else:
                        tasks.append(exp_path)  # Collecting paths to process
    # Use multiprocessing to parse experiments in parallel with tqdm
    with Pool() as pool:
        results_parsers += list(tqdm(pool.imap(parse_experiment, tasks), total=len(tasks)))

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


def process_combination(args):
    results_parsers, metric, vType, key = args
    if vType:
        vTypes = ["AV", "HD", "Bus"]
        result = {}
        for v in vTypes:
            vtype_results = calc_metric_over_simulations(results_parsers, metric, v)
            result[v] = {"mean": vtype_results["mean"], "std": vtype_results["std"]}
        return result, key
    else:
        av_rate_results = calc_metric_over_simulations(results_parsers, metric)
        return {"mean": av_rate_results["mean"], "std": av_rate_results["std"]}, key


# Function to parallelize

def create_metric_results_table(results_parsers, metric,
                                demands=None, av_rates=None, policies=None,
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
    av_rates = sorted(list(set(map(lambda x: x.av_rate, results_parsers)))) if not av_rates else av_rates
    policies = sorted(list(set(map(lambda x: x.policy_name, results_parsers)))) if not policies else policies

    if vType:
        vTypes = ["AV", "HD", "Bus"]
        df = pd.DataFrame(index=policies,
                          columns=pd.MultiIndex.from_product([demands, av_rates, vTypes, ["mean", "std"]]))
    else:
        df = pd.DataFrame(index=policies, columns=pd.MultiIndex.from_product([demands, av_rates, ["mean", "std"]]))

    tasks = []
    for demand in demands:
        for policy in policies:
            for av_rate in av_rates:
                task_parsers = list(filter(lambda x: x.av_rate == av_rate and
                                                     x.demand_name == demand and
                                                     x.policy_name == policy,
                                           results_parsers))
                tasks.append((task_parsers, metric, vType, (policy, demand, av_rate)))

    with Pool() as pool:
        # Use imap instead of starmap for progress tracking
        results = list(tqdm(pool.imap_unordered(process_combination, tasks), total=len(tasks)))
    for result, key in results:
        policy, demand, av_rate = key
        if vType:  # If vType was used
            for v in vTypes:
                df.loc[policy, (demand, av_rate, v, "mean")] = result[v]["mean"]
                df.loc[policy, (demand, av_rate, v, "std")] = result[v]["std"]
        else:
            df.loc[policy, (demand, av_rate, "mean")] = result["mean"]
            df.loc[policy, (demand, av_rate, "std")] = result["std"]

    return df


def create_speeds_plot(results_parsers,
                       demands=None, av_rates=None, policies=None,
                       ):
    demands = list(set(map(lambda x: x.demand_name, results_parsers))) if not demands else demands
    av_rates = sorted(list(set(map(lambda x: x.av_rate, results_parsers)))) if not av_rates else av_rates
    policies = sorted(list(set(map(lambda x: x.policy_name, results_parsers)))) if not policies else policies


if __name__ == '__main__':
    parsers = get_all_results_parsers("SUMO/outputs", one_demand="Daily")
    output_path = "results/output_results"
    for metric in ["passDelay", "totalDelay", "duration", "passDuration"]:
        res = create_metric_results_table(parsers, metric)
        res.to_csv(os.path.join(output_path,f"{metric}.csv"))
        res.to_pickle(os.path.join(output_path,f"{metric}.pkl"))

        res = create_metric_results_table(parsers, metric, vType=True)
        res.to_csv(os.path.join(output_path,f"{metric}_vType.csv"))
        res.to_pickle(os.path.join(output_path,f"{metric}_vType.pkl"))
