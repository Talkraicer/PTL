import os
import pickle
from multiprocessing.pool import Pool
from tqdm import tqdm
import numpy as np

from SUMO.SUMOAdpater import SUMOAdapter
from utils.argparse_utils import get_args
from Policies.policy_parameters import create_policy_definitions
from Demands.demand_parameters import create_demand_definitions
from results.parse_all_results import parse_all_results
import warnings
from env.PTLenv import PTLEnv
from Loggers.CSVLogger import CSVLogger

warnings.filterwarnings("ignore", message="API change now handles step as floating point seconds")


def simulate(args, logger=CSVLogger):
    sumo, policy, train = args
    sumo.init_simulation(policy)  # initialize simulation

    # initialize logger:
    if logger:
        logger = logger(sumo.output_folder, policy.__str__(), ["min_num_pass",])
    if policy.RL:
        if train:
            env = PTLEnv(sumo)
            policy.after_init_sumo(env)
            policy.agent.learn(total_timesteps=10**6 // policy.act_rate)
            env.save_policy()
        else:
            env = PTLEnv(sumo, train=False)
            policy.after_init_sumo(env)
            agent_path = os.path.join("agents", env.sumo.demand_profile.__str__(), policy.__str__() + ".zip")
            policy.agent = policy.agent.load(agent_path)
            policy.agent.set_env(env)

            env.reset()
            while not env.isFinish():
                policy.handle_step(env)
                if logger:
                    logger.log(sumo.get_state_dict())
            env.close()
    else:
        policy.after_init_sumo(sumo)
        # run simulation
        while not sumo.isFinish():
            policy.handle_step(sumo)
            if logger:
                # check if policy has attribute current_min_num_pass
                if hasattr(policy, "current_min_num_pass"):
                    value = policy.current_min_num_pass
                else:
                    value = policy.min_num_pass
                logger.log({"min_num_pass": value})
            sumo.step()
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
    POLICY_DEFINITIONS = create_policy_definitions(av_rate_range=args.av_rate, min_num_pass_range=args.min_num_pass,
                                                   train = args.train)
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
                simulation_args.append((sumo, policy, args.train))
    num_processes = args.num_processes if not args.gui else 1
    with Pool(num_processes) as pool:
        list(tqdm(pool.imap(simulate, simulation_args), total=len(simulation_args)))
    if args.parse_results:
        parse_all_results(output_folder=f"SUMO/outputs/{args.net_file}", demands=demand_instances)


if __name__ == '__main__':
    main(get_args())
