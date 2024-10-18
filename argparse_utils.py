import argparse
from Policies import step_handle_functions
def get_args():
    parser = argparse.ArgumentParser(description='Simulation and Policy Arguments')
    parser.add_argument("-p", '--policy', type=str, default='Nothing', help='Policy to use')
    parser.add_argument("-s", '--seed', type=int, default=42, help='Seed for the simulation')
    parser.add_arguemnt("-n","--num_experiments", type=int, default=10, help='Number of experiments to run')
    parser.add_arguemnt("-d","--demand",type=str, default='Daily', help='Demand type')

    args = parser.parse_args()

    assert args.policy in step_handle_functions.keys(), f"Policy {args.policy} not found in the Policies module"
