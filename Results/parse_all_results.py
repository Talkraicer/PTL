import os
from Results.parse_exp_results import ResultsParser
import pandas as pd
import numpy as np


def get_all_results_parsers(outputs_folder):
    results_parsers = []
    for av_rate in os.listdir(outputs_folder):
        av_rate_folder = os.path.join(outputs_folder, av_rate)
        for seed in os.listdir(av_rate_folder):
            seed_folder = os.path.join(av_rate_folder, seed)
            experiments = list(set(map(lambda x: x.split(".")[0], os.listdir(seed_folder))))
            for experiment in experiments:
                exp_path = os.path.join(seed_folder, experiment)
                results_parsers.append(ResultsParser(exp_path + ".xml", logger_output_file=exp_path + ".csv",
                                                     av_rate=av_rate))
    return results_parsers


def calc_metric_over_simulations(results_parsers, metric, vType=False, PTL=False):
    """
    Calculate the mean and std of a metric for all the results parsers
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :param PTL: weather to calculate the metric for PTL and not PTL separately
    :return: a dataframe with the mean and std of the metric for all the results parsers
    """
    assert not (vType and PTL), "Cannot calculate metric for both vType and PTL"
    if vType:
        means = [rp.mean_metric_vType(metric) for rp in results_parsers]
        df_means = pd.DataFrame(means, means[0].keys())
        # calculate mean of means and std of means for each column
        return df_means.aggregate({col: "mean" for col in df_means.columns} + {col: "std" for col in df_means.columns},
                                  axis=0)
    elif PTL:
        means = [rp.mean_metric_PTL(metric) for rp in results_parsers]
        df_means = pd.DataFrame(means, means[0].keys())
        # calculate mean of means and std of means for each column
        return df_means.aggregate({col: "mean" for col in df_means.columns} + {col: "std" for col in df_means.columns},
                                  axis=0)
    else:
        means = [rp.mean_metric(metric) for rp in results_parsers]
        return pd.DataFrame({"mean": np.mean(means), "std": np.std(means)}, index=[metric])


def calc_metric_over_avrates(results_parsers, metric, vType=False, PTL=False):
    """
    Calculate the mean and std of a metric for all the results parsers for each av rate
    :param results_parsers: a list of ResultsParser objects
    :param metric: the metric to calculate the mean and std for
    :param vType: weather to calculate the metric for each vehicle type
    :param PTL: weather to calculate the metric for PTL and not PTL separately
    :return: a dataframe with the mean and std of the metric for all the results parsers for each av rate
    """
    assert not (vType and PTL), "Cannot calculate metric for both vType and PTL"
    av_rates = set(map(lambda x: x.av_rate, results_parsers))
    final_dict = {"av_rate":[]}
    for av_rate in av_rates:
        final_dict[av_rate] = av_rate
        av_rate_parsers = list(filter(lambda x: x.av_rate == av_rate, results_parsers))
        df_av_rate = calc_metric_over_simulations(av_rate_parsers, metric, vType, PTL)
        for col in df_av_rate.columns:
            if col not in final_dict:
                final_dict[col] = []
            final_dict[col].append(df_av_rate[col].values[0])
    return pd.DataFrame(final_dict)