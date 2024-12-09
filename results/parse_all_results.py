import os
import pickle

import plotly.graph_objects as go

from results.parse_exp_results import ResultsParser
import pandas as pd
import numpy as np
from multiprocessing import Pool
from tqdm import tqdm
from SUMO.netfile_utils import get_PTL_lanes
from Demands.demand_parameters import create_demand_definitions


def parse_experiment(args):
    exp_path, PTL_lanes = args
    """Helper function to parse a single experiment path."""
    return ResultsParser(exp_path, PTL_lanes=PTL_lanes)


def get_all_results_parsers(outputs_folder, demands=None, one_av_rate=None, policy=None):
    demands = os.listdir(outputs_folder) if not demands else demands

    net_file = [f for f in os.listdir(outputs_folder) if f.endswith(".net.xml")][0]
    net_file = os.path.join(outputs_folder, net_file)
    PTL_lanes = get_PTL_lanes(net_file)
    demands = [demand for demand in demands if os.path.isdir(os.path.join(outputs_folder, demand))]

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
                    if policy and experiment != policy:
                        continue
                    exp_path = os.path.join(seed_folder, experiment)
                    if os.path.exists(exp_path + "_ResultsParser.pkl"):
                        results_parsers.append(pickle.load(open(exp_path + "_ResultsParser.pkl", "rb")))
                    else:
                        tasks.append((exp_path, PTL_lanes))  # Collecting paths to process
    if len(tasks) > 1:
        # Use multiprocessing to parse experiments in parallel with tqdm
        with Pool() as pool:
            pool_output = list(tqdm(pool.imap(parse_experiment, tasks), total=len(tasks)))
        results_parsers.extend(pool_output)
    return results_parsers


def calc_mean_std(df):
    # Calculate mean and standard deviation of each column
    means = df.mean()
    stds = df.std()

    # Create a new DataFrame with the required structure
    return pd.DataFrame({
        'mean': means,
        'std': stds}).T


def calc_metric_over_simulations(results_parsers, metric, vType=None, baselines=None):
    """
    Calculate the mean and std of a metric for all the results parsers
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :param PTL: weather to calculate the metric for PTL and not PTL separately
    :param baseline: the baselines to compare the metric to (list of ResultsParser objects)
    :return: a dataframe with the mean and std of the metric for all the results parsers
    """
    if baselines:
        means = [rp.mean_metric(metric, vType, baseline) for rp in results_parsers for baseline in baselines
                 if rp.seed == baseline.seed]
    else:
        means = [rp.mean_metric(metric, vType) for rp in results_parsers]
    return {"mean": np.mean(means), "std": np.std(means)}


def process_combination(args):
    results_parsers, metric, vType, baselines, key = args
    if vType:
        vTypes = ["AV", "HD", "Bus"]
        result = {}
        for v in vTypes:
            vtype_results = calc_metric_over_simulations(results_parsers, metric, v)
            result[v] = {"mean": vtype_results["mean"], "std": vtype_results["std"]}
        return result, key
    else:
        av_rate_results = calc_metric_over_simulations(results_parsers, metric, baselines=baselines)
        return {"mean": av_rate_results["mean"], "std": av_rate_results["std"]}, key


def highlight_min(s):
    # return style of background color for the minimum value in the column if the column is "mean"
    is_min = s == s.min()
    unenforceable = [f"Plus_{i}" for i in range(2, 6)] + [f"PlusSplit_{i}" for i in range(2, 6)]
    min_enforceable = s[~s.index.isin(unenforceable)].min()
    is_min_enforceable = s == min_enforceable
    if "mean" in s.name:
        styles = []
        # highlight the minimum value in the mean column, bold the minimum value where enforceable
        for m, e in zip(is_min, is_min_enforceable):
            if m and e:
                styles.append('background-color: yellow; font-weight: bold')
            elif m:
                styles.append('background-color: yellow')
            elif e:
                styles.append('font-weight: bold')
            else:
                styles.append('')
        return styles
    return ['' for _ in is_min]


def create_metrics_results_tables(results_parsers, metrics, result_folder,
                                  demands=None, av_rates=None, policies=None,
                                  vType=False, baseline=False):
    """
    Create a table with the mean and std of a metric for all the results parsers
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :return: a dataframe of columns demand, subcolumns of av_rates, (optional) subcolumns of vTypes,
                subcolumns mean and std, and rows of policies
    """
    demands = sorted(list(set(map(lambda x: x.demand_name, results_parsers))) if not demands else demands)
    av_rates = sorted(list(set(map(lambda x: x.av_rate, results_parsers)))) if not av_rates else av_rates
    policies = sorted(list(set(map(lambda x: x.policy_name, results_parsers)))) if not policies else policies
    baselines = list(filter(lambda x: x.policy_name == "Nothing", results_parsers)) if baseline else None
    if vType:
        vTypes = ["AV", "HD", "Bus"]
        df = pd.DataFrame(index=policies,
                          columns=pd.MultiIndex.from_product([demands, av_rates, vTypes, ["mean", "std"]]))
    else:
        df = pd.DataFrame(index=policies, columns=pd.MultiIndex.from_product([demands, av_rates, ["mean", "std"]]))
    for metric in metrics:
        tasks = []
        df_metric = df.copy()
        for demand in demands:
            for policy in policies:
                for av_rate in av_rates:
                    task_parsers = list(filter(lambda x: x.av_rate == av_rate and
                                                         x.demand_name == demand and
                                                         x.policy_name == policy,
                                               results_parsers))
                    tasks.append((task_parsers, metric, vType, baselines, (policy, demand, av_rate)))

        with Pool() as pool:
            # Use imap instead of starmap for progress tracking
            results = list(tqdm(pool.imap(process_combination, tasks), total=len(tasks)))
        for result, key in results:
            policy, demand, av_rate = key
            if vType:  # If vType was used
                for v in vTypes:
                    df_metric.loc[policy, (demand, av_rate, v, "mean")] = result[v]["mean"]
                    df_metric.loc[policy, (demand, av_rate, v, "std")] = result[v]["std"]
            else:
                df_metric.loc[policy, (demand, av_rate, "mean")] = result["mean"]
                df_metric.loc[policy, (demand, av_rate, "std")] = result["std"]

        df_name = f"{metric}_vType" if vType else f"{metric}_baseline" if baseline else f"{metric}"
        df_metric.to_csv(os.path.join(result_folder, f"{df_name}.csv"))
        df_metric.to_pickle(os.path.join(result_folder, f"{df_name}.pkl"))

        # Create a table where the min value in the mean column is highlighted
        df_metric.style.apply(highlight_min) \
            .to_excel(os.path.join(result_folder, f"{df_name}.xlsx"))


def create_plots(results_parsers, result_folder, metric,
                 PTL=False,
                 demands=None, policies=None, one_av_rate=None,
                 errorbars=True
                 ):
    demands = list(set(map(lambda x: x.demand_name, results_parsers))) if not demands else demands
    av_rates = sorted(list(set(map(lambda x: x.av_rate, results_parsers)))) if not one_av_rate else [one_av_rate]
    policies = sorted(list(set(map(lambda x: x.policy_name, results_parsers)))) if not policies else policies

    for demand in demands:
        for av_rate in av_rates:
            fig = go.Figure()
            for policy in policies:
                task_parsers = list(filter(lambda x: x.av_rate == av_rate and
                                                     x.demand_name == demand and
                                                     x.policy_name == policy,
                                           results_parsers))
                if len(task_parsers) == 0:
                    continue
                y_values = [rp.mean_plot_metric(metric, PTL=PTL) for rp in task_parsers]

                # cut all y_values to the same length
                min_len = min(map(len, y_values))
                y_values = np.array([y[:min_len] for y in y_values])
                masked_y = np.ma.masked_where(y_values == 0, y_values)

                mean_y_values = np.ma.mean(masked_y, axis=0)
                mean_y_values = mean_y_values.filled(0)
                std_y_values = np.ma.std(masked_y, axis=0)
                std_y_values = std_y_values.filled(0)
                if errorbars:
                    fig.add_trace(go.Scatter(x=list(range(len(mean_y_values))), y=mean_y_values, mode='lines',
                                             name=policy, error_y=dict(type='data', array=std_y_values, visible=True)))
                else:
                    fig.add_trace(go.Scatter(x=list(range(len(mean_y_values))), y=mean_y_values, mode='lines',
                                             name=policy))
            fig.update_layout(
                title=f"{metric} for {demand} demand and {av_rate} AV rate",
                xaxis_title="Time",
                yaxis_title=f"{metric}",
                legend_title="Policies"
            )
            output_filename = f"{metric}_{demand}_{av_rate}" + ("_PTL" if PTL else "") + ".html"
            os.makedirs(os.path.join(result_folder, "plots"), exist_ok=True)
            fig.write_html(os.path.join(result_folder, "plots", output_filename))


def parse_all_results(output_folder="SUMO/outputs/network_new", demands=None, one_av_rate=None, policy=None):
    if not demands:
        demands = os.listdir(output_folder)
        demands = [demand for demand in demands if os.path.isdir(os.path.join(output_folder, demand))]
        demands = sorted(demands)
    else:
        demands = sorted(list(set([demand.__str__() for demand in demands])))
    folder_name = "_".join(demands[0].split("_")[:-1])
    result_folder = os.path.join("results", "output_results", output_folder.split("/")[-1], folder_name)
    if policy:
        result_folder = os.path.join(result_folder, policy)
    os.makedirs(result_folder, exist_ok=True)
    results_parsers = get_all_results_parsers(output_folder, demands=demands, one_av_rate=one_av_rate, policy=policy)
    metrics = ["passDelay", "totalDelay", "duration", "passDuration", "departDelay"]
    # create_metrics_results_tables(results_parsers, metrics, result_folder=result_folder, vType=False, demands=demands)
    # create_metrics_results_tables(results_parsers, metrics, result_folder=result_folder, vType=True, demands=demands)
    # create_plots(results_parsers, metric="speed", PTL=True, result_folder=result_folder, demands=demands,
    #              errorbars=False)
    # create_plots(results_parsers, metric="speed", PTL=False, result_folder=result_folder, demands=demands,
    #              errorbars=False)
    create_plots(results_parsers, metric="num_vehs", PTL=True, result_folder=result_folder, demands=demands,
                 errorbars=False)
    create_plots(results_parsers, metric="num_vehs", PTL=False, result_folder=result_folder, demands=demands,
                    errorbars=False)
    if "toy" not in output_folder:
        create_metrics_results_tables(results_parsers, metrics, result_folder=result_folder, baseline=True, )


if __name__ == '__main__':
    DEMAND_DEFINITIONS = create_demand_definitions()
    parse_all_results(output_folder=f"SUMO/outputs/network_simple",
                      demands=[DEMAND_DEFINITIONS["DemandToy"]["class"](**params) for params in
                               DEMAND_DEFINITIONS["DemandToy"]["params"]])
