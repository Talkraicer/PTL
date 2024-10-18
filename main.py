from SUMO.SUMOAdpater import SUMOAdapter
from SUMO.demand_profiles import *
from Policies.step_handle_functions import *
from multiprocessing.pool import Pool
import numpy as np
from tqdm import tqdm

np.random.seed(42)


# Get all policies
def get_all_subclasses(cls):
    subclasses = cls.__subclasses__()
    for subclass in subclasses:
        subclasses += get_all_subclasses(subclass)
    return subclasses

def simulate(args):
    demand, seed, av_rate, min_num_pass, policy = args
    print(demand.__name__, policy.__name__)
    demand = demand()
    sumo = SUMOAdapter(demand, seed, av_rate)
    sumo.init_simulation(output_file=f"{demand.__str__()}_{policy.__name__}_{min_num_pass}.xml")
    policy = policy(sumo, min_num_pass) if policy.__name__ != "Nothing" else policy(sumo)
    t = 0
    while not sumo.isFinish():
        policy.handle_step(sumo.get_state_dict(t))
        sumo.step(t)
        t += 1
    sumo.close()



def main():
    demands = get_all_subclasses(Demand)
    seeds = [np.random.randint(0, 10000) for _ in range(10)]
    av_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    pass_range = range(1, 6)
    policies = get_all_subclasses(StepHandleFunction)
    args = []
    for demand in demands:
        for seed in seeds:
            for av_rate in av_rates:
                for min_num_pass in pass_range:
                    for policy in policies:
                        args.append((demand, seed, av_rate, min_num_pass, policy))
    with Pool() as pool:
        list(tqdm(pool.imap(simulate, args), total=len(args)))

if __name__ == '__main__':
    main()