import argparse
import os
import numpy as np


# from Policies import static_step_handle_functions

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_args():
    parser = argparse.ArgumentParser(description='Simulation and Policy Arguments')
    parser.add_argument("-s", '--seed', type=int, default=42,
                        help='Seed for the simulation')
    parser.add_argument("-n", "--num_experiments", type=int, default=3,
                        help='Number of experiments to run')
    parser.add_argument("-ss", "--skip_seeds", type=int, default=0, )
    parser.add_argument("--num_processes", type=int, default=None,
                        help='Number of processes to run in parallel, None=All available cores')
    parser.add_argument("-p", "--policy", type=str, default=None, help='Policy to run, None=all policies')
    parser.add_argument("-d", "--demand", type=str, default="DailyCaseStudy", help='Demand to run, None=all demands')
    parser.add_argument("--net_file", type=str, default="Ayalon_Casestudy2",
                        help='Network file name (has to be in the SUMOconfig folder)')
    parser.add_argument("--parse_results", type=str2bool, default=True, help='Parse results')
    parser.add_argument("--gui", type=str2bool, default=False, help='Run with GUI')
    parser.add_argument("--av_rate_min", type=float, default=0, help='AV rate to run, None=all av rates')
    parser.add_argument("--av_rate_max", type=float, default=1, help='AV rate to run, None=all av rates')
    parser.add_argument("--av_rate_step", type=float, default=0.1, help='AV rate to run, None=all av rates')
    parser.add_argument("--min_num_pass", type=int, default=None,
                        help='Minimum number of passengers - for static policies')
    parser.add_argument("-t", "--train", type=str2bool, default=False, help='Train the RL agent')

    args = parser.parse_args()
    assert os.path.exists(
        f"SUMO/SUMOconfig/{args.net_file}.net.xml"), f"Network file {args.net_file}.net.xml does not exist"
    if args.av_rate_min is not None:
        assert args.av_rate_max is not None, "av_rate_max has to be set if av_rate_min is set"
        assert args.av_rate_step is not None, "av_rate_step has to be set if av_rate_min is set"
        av_rates = np.arange(args.av_rate_min, args.av_rate_max + args.av_rate_step, args.av_rate_step)
        av_rates = list(set(np.round(av_rates, len(str(args.av_rate_step)) - 2)))
        args.av_rate = av_rates
    else:
        args.av_rate = None
    if args.train:
        args.parse_results = False
    args.min_num_pass = [args.min_num_pass] if args.min_num_pass is not None else None
    return args


if __name__ == '__main__':
    args = get_args()
    print(args.parse_results)
