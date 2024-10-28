import argparse
import os

from Policies import static_step_handle_functions


def get_args():
    parser = argparse.ArgumentParser(description='Simulation and Policy Arguments')
    parser.add_argument("-s", '--seed', type=int, default=42,
                        help='Seed for the simulation')
    parser.add_argument("-n", "--num_experiments", type=int, default=10,
                        help='Number of experiments to run')
    parser.add_argument("--num_processes", type=int, default=None,
                        help='Number of processes to run in parallel, None=All available cores')
    parser.add_argument("-p", "--policy", type=str, default=None, help='Policy to run, None=all policies')
    parser.add_argument("-d", "--demand", type=str, default=None, help='Demand to run, None=all demands')
    parser.add_argument("-av", "--av_rate", type=float, default=None, help='AV rate to run, None=all av rates')
    parser.add_argument("--net_file" , type=str, default="network_toy", help='Network file name (has to be in the SUMOconfig folder)')
    parser.add_argument("--parse_results", type=bool, default=True, help='Parse results')
    parser.add_argument("--gui", type=bool, default=False, help='Run with GUI')

    args = parser.parse_args()
    assert os.path.exists(f"SUMO/SUMOconfig/{args.net_file}.net.xml"), f"Network file {args.net_file}.net.xml does not exist"
    return args