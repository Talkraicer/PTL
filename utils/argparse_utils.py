import argparse
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
    parser.add_argument("-c","--closed", type=bool, default=False, help='Closed PTL')


    args = parser.parse_args()
    return args