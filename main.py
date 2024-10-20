from SUMO.SUMOAdpater import SUMOAdapter
from SUMO.demand_profiles import *
from Policies.step_handle_functions import *
from multiprocessing.pool import Pool
import numpy as np
from tqdm import tqdm
from Loggers.CSVLogger import CSVLogger
import os

np.random.seed(42)
MAX_NUM_PROCESS = None  # set to None to use all available cores


# Get all policies
def get_all_subclasses(cls):
    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        subclasses += get_all_subclasses(subclass)
    return subclasses


def clear_older_configs():
    for file in os.listdir("SUMO/SUMOconfig"):
        # check if file is a directory
        if os.path.isdir(file):
            # remove the directory
            os.rmdir(file)


def simulate(args, logger=CSVLogger):
    sumo, min_num_pass, policy = args


    # initialize simulation
    output_filename = f"{sumo.demand_profile.__str__()}_{policy.__name__}"
    output_filename += f"_{min_num_pass}" if policy.is_num_pass_dependent else ""
    sumo.init_simulation(output_file=f"{output_filename}.xml")  # initialize simulation

    # initialize logger:
    if logger:
        logger = logger(sumo.output_folder, output_filename, sumo.get_state_dict(0).keys())

    # initialize policy:
    policy = policy(sumo)
    if policy.is_num_pass_dependent:
        policy.set_num_pass(min_num_pass)

    # run simulation
    t = 0
    while not sumo.isFinish():
        state_dict = sumo.get_state_dict(t)
        policy.handle_step(state_dict)
        if logger:
            logger.log(state_dict)
        sumo.step(t)
        t += 1

    sumo.close()


def main():
    clear_older_configs()
    demands = get_all_subclasses(Demand)
    seeds = [np.random.randint(0, 10000) for _ in range(10)]
    av_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    pass_range = range(1, 6)
    policies = get_all_subclasses(StepHandleFunction)
    args = []
    for demand in demands:
        demand_inst = demand()
        for seed in seeds:
            for policy in policies:
                if policy.is_num_pass_dependent:
                    if policy.is_av_rate_dependent:
                        for av_rate in av_rates:
                            sumo = SUMOAdapter(demand_inst, seed, av_rate)
                            for min_num_pass in pass_range:
                                args.append((sumo, min_num_pass, policy))
                    else:
                        sumo = SUMOAdapter(demand_inst, seed, 0)
                        for min_num_pass in pass_range:
                            args.append((sumo, min_num_pass, policy))
                else:
                    sumo = SUMOAdapter(demand_inst, seed, 0)
                    args.append((sumo, 0, policy))
    with Pool(MAX_NUM_PROCESS) as pool:
        list(tqdm(pool.imap(simulate, args), total=len(args)))


if __name__ == '__main__':
    main()
