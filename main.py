from multiprocessing.pool import Pool
from tqdm import tqdm
import numpy as np

from SUMO.SUMOAdpater import SUMOAdapter
import Demands.demand_profiles as demand_profiles
from utils.argparse_utils import get_args
from utils.class_utils import get_all_subclasses
from Policies.policy_parameters import create_policy_definitions
from Demands.demand_parameters import create_demand_definitions
from results.parse_all_results import parse_all_results
import warnings

warnings.filterwarnings("ignore", message="API change now handles step as floating point seconds")


def simulate(args, logger=None):
    sumo, policy = args
    sumo.init_simulation(policy)  # initialize simulation
    policy.after_init_sumo(sumo)
    # initialize logger:
    if logger:
        logger = logger(sumo.output_folder, policy.__str__(), sumo.get_state_dict(0).keys())

    # run simulation
    t = 0
    while not sumo.isFinish():
        # state_dict = sumo.get_state_dict(t)
        state_dict = {"t": t}
        policy.handle_step(state_dict)
        if logger:
            logger.log(state_dict)
        sumo.step(t)
        t += 1

    sumo.close()


def main(args):
    DEMAND_DEFINITIONS = create_demand_definitions(av_rate_range=args.av_rate)
    if args.demand:
        demand_instances = [DEMAND_DEFINITIONS[args.demand]["class"](**params) for params in
                            DEMAND_DEFINITIONS[args.demand]["params"]]
    else:
        demand_instances = [demand["class"](**params) for demand in DEMAND_DEFINITIONS.values() for params in
                            demand["params"]]
    num_exps = args.num_experiments
    np.random.seed(args.seed)
    seeds = [np.random.randint(0, 10000) for _ in range(num_exps)]
    POLICY_DEFINITIONS = create_policy_definitions(av_rate_range=args.av_rate, min_num_pass_range=args.min_num_pass)
    if args.policy:
        policy_instances = [POLICY_DEFINITIONS[args.policy]["class"](**params) for params in
                            POLICY_DEFINITIONS[args.policy]["params"]]
    else:
        policy_instances = [policy["class"](**params) for policy in POLICY_DEFINITIONS.values()
                            for params in policy["params"]]
    simulation_args = []
    net_file = args.net_file + ".net.xml"
    for demand in demand_instances:
        pass_demand_changed = demand.prob_pass_av[1] != 0.63
        for seed in seeds:
            for policy in policy_instances:
                if policy.av_rate != demand.av_rate:
                    continue
                sumo = SUMOAdapter(demand, seed, net_file=net_file,
                                   gui=args.gui)
                simulation_args.append((sumo, policy))
    num_processes = args.num_processes if not args.gui else 1
    with Pool(num_processes) as pool:
        list(tqdm(pool.imap(simulate, simulation_args), total=len(simulation_args)))
    if args.parse_results:
        parse_all_results(output_folder=f"SUMO/outputs/{args.net_file}", demands=demand_instances)


if __name__ == '__main__':
    main(get_args())
