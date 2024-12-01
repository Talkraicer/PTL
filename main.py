from multiprocessing.pool import Pool
from tqdm import tqdm
import numpy as np

from SUMO.SUMOAdpater import SUMOAdapter
import Demands.demand_profiles as demand_profiles
import Policies.static_step_handle_functions as static_step_handle_functions
from utils.argparse_utils import get_args
from utils.class_utils import get_all_subclasses
from results.parse_all_results import parse_all_results
import warnings

from Demands.DemandToyUniform import *
from Demands.DemandToy import *
from Demands.PassengerDemand import *

warnings.filterwarnings("ignore", message="API change now handles step as floating point seconds")


def simulate(args, logger=None):
    sumo, min_num_pass, policy, policy_args = args
    policy = policy(sumo, policy_args) if policy_args is not None else policy(sumo)
    if policy.is_num_pass_dependent:
        policy.set_num_pass(min_num_pass)
    sumo.init_simulation(policy)  # initialize simulation
    policy.after_init_sumo()
    # initialize logger:
    if logger:
        logger = logger(sumo.output_folder, policy.__str__(), sumo.get_state_dict(0).keys())

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


def main(args):
    demand_instances = []
    if args.demand is None:
        demands = get_all_subclasses(demand_profiles.Demand)
    else:
        demands = [globals().get(args.demand)]
    for demand in demands:
        if demand.ranges is not None:
            for amount in demand.ranges:
                demand_instances.append(demand(amount))
        else:
            demand_instances.append(demand())
    num_exps = args.num_experiments
    np.random.seed(args.seed)
    seeds = [np.random.randint(0, 10000) for _ in range(num_exps)]
    av_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] if args.av_rate is None else [args.av_rate]
    pass_range = range(1, 6)
    policies = get_all_subclasses(static_step_handle_functions.StepHandleFunction) if args.policy is None \
        else [getattr(static_step_handle_functions, args.policy)]
    simulation_args = []
    net_file = args.net_file + ".net.xml"
    for demand in demand_instances:
        pass_demand_changed = demand.prob_pass_av[1] != 0.63
        for seed in seeds:
            for policy in policies:
                for policy_args in policy.param_range:
                    if policy.is_av_rate_dependent or pass_demand_changed:
                        if not policy.is_av_rate_dependent:
                            av_rates_run = av_rates + [0.0]
                        else:
                            av_rates_run = av_rates
                        for av_rate in av_rates_run:
                            if policy.is_num_pass_dependent:
                                for min_num_pass in pass_range:
                                    sumo = SUMOAdapter(demand, seed, av_rate, net_file=net_file,
                                                       gui=args.gui)
                                    simulation_args.append((sumo, min_num_pass, policy, policy_args))
                            else:
                                sumo = SUMOAdapter(demand, seed, av_rate, net_file=net_file,
                                                   gui=args.gui)
                                simulation_args.append((sumo, 0, policy, policy_args))

                    elif policy.is_num_pass_dependent:
                        for min_num_pass in pass_range:
                            sumo = SUMOAdapter(demand, seed, 0, net_file=net_file,
                                               gui=args.gui)
                            simulation_args.append((sumo, min_num_pass, policy, policy_args))
                    else:
                        sumo = SUMOAdapter(demand, seed, 0, net_file=net_file,
                                           gui=args.gui)
                        simulation_args.append((sumo, 0, policy, policy_args))
    num_processes = args.num_processes if not args.gui else 1
    with Pool(num_processes) as pool:
        list(tqdm(pool.imap(simulate, simulation_args), total=len(simulation_args)))
    # if args.parse_results:
    #     parse_all_results(output_folder=f"SUMO/outputs/{args.net_file}", demands=demand_instances)


if __name__ == '__main__':
    main(get_args())
