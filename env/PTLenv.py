import os.path
from typing import SupportsFloat, Any

import gymnasium as gym
import numpy as np
from collections import OrderedDict
from SUMO.SUMOAdpater import SUMOAdapter
from SUMO.netfile_utils import *
from Policies.static_step_handle_functions import StaticNumPass

NUM_ACTIONS = 3


class PTLEnv(gym.Env):
    def __init__(self, sumo: SUMOAdapter):
        self.sumo = sumo
        self.state_lanes = None
        self.target_lanes = None
        self.observation_space = self._set_observations()
        self.observation_space.spaces = OrderedDict(sorted(self.observation_space.spaces.items()))
        self.action_space = gym.spaces.Discrete(NUM_ACTIONS)
        self.action_mapping = [-1, 0, 1]  # 0: -1, 1:0, 2:+1

        self.state = self.observation_space.sample()
        self.current_min_num_pass = 1
        self.act_rate = 0
        self.policy = None

    def step(self, action):

        self.current_min_num_pass = self._clamp(self.current_min_num_pass + self.action_mapping[action], 1, 6)

        reward = 0
        for _ in range(self.act_rate):
            self.sumo.allow_vehicles(veh_types=["AV"], min_num_pass=self.current_min_num_pass)
            self.sumo.step()
            for lane in self.target_lanes:
                reward += self.sumo.get_num_pass(laneID=lane.getID())

        # update state from SUMO
        for lane in self.state_lanes:
            HD, AV, ALLOWED = self.sumo.get_num_vehs(lane_ID=lane.getID())
            self.state[f"{lane.getID()}_HD"] = HD
            self.state[f"{lane.getID()}_AV"] = AV
            self.state[f"{lane.getID()}_ALLOWED"] = ALLOWED
        self.state["current_min_num_pass"] = self.current_min_num_pass
        self.state["time_since_change"] += self.act_rate
        if action != 1:
            self.state["time_since_change"] = self.act_rate

        for k in self.state.keys():
            if self.state[k] >= self.observation_space[k].n:
                self.state[k] = self.observation_space[k].n - 1
        done = self.sumo.isFinish()

        return self.state, reward, done, False, {}

    def reset(self, seed: int = None):
        # check if a SUMO instance is already running
        self.act_rate = self.policy.act_rate
        try:
            self.sumo.close()
        except:
            pass

        # reset the state
        self.current_min_num_pass = 1
        for k in self.state.keys():
            self.state[k] = 0
        self.state["current_min_num_pass"] = self.current_min_num_pass

        # init SUMO
        self.sumo.seed = seed if seed is not None else np.random.randint(0, 10000)
        self.sumo.av_rate = np.random.randint(1, 11) / 10.0
        self.sumo.init_simulation(self.policy)

        return self.state, {}

    def render(self):
        pass

    def close(self):
        self.sumo.close()

    def _set_observations(self):
        edges = get_edges(self.sumo.network_file)
        edges = [edge for edge in edges if edge.getID() != get_last_edge(self.sumo.network_file).getID()]
        self.state_lanes = [lane for edge in edges for lane in edge.getLanes()]
        self.target_lanes = [lane for lane in get_last_edge(self.sumo.network_file).getLanes()]

        # Construct an OrderedDict for observation spaces
        obs_dict = OrderedDict()
        for lane in self.state_lanes:
            lane_id = lane.getID()
            max_vehicles = get_lane_max_vehicles(lane)
            obs_dict[f"{lane_id}_HD"] = gym.spaces.Discrete(max_vehicles)
            obs_dict[f"{lane_id}_AV"] = gym.spaces.Discrete(max_vehicles)
            obs_dict[f"{lane_id}_ALLOWED"] = gym.spaces.Discrete(max_vehicles)

        # Add additional observation keys
        obs_dict["current_min_num_pass"] = gym.spaces.Discrete(7)
        obs_dict["time_since_change"] = gym.spaces.Discrete(15000)

        # Ensure Dict is created with an OrderedDict
        return gym.spaces.Dict(obs_dict)

    def _clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def save_policy(self):
        path = os.path.join("agents", self.sumo.demand_profile.__str__())
        os.makedirs(path, exist_ok=True)
        self.policy.save(path)
