import os

from stable_baselines3 import DQN, PPO, A2C
from Policies.static_step_handle_functions import StepHandleFunction
from SUMO.SUMOAdpater import SUMOAdapter
from env.PTLenv import PTLEnv


class RLAgent(StepHandleFunction):
    def __init__(self,
                 av_rate: float = 0.1,
                 act_rate: int = 10,
                 agent_type: str = "DQN",
                 policy_type: str = "MultiInputPolicy", ):
        super().__init__()
        assert agent_type in ["DQN", "PPO", "A2C"]
        self.agent_type = agent_type
        self.RL = True
        self.act_rate = act_rate
        self.veh_kinds = ["AV"]
        self.min_num_pass = 6   # NEVER CHANGE
        self.endToEnd = False
        self.agent = None
        self.policy_type = policy_type
        self.av_rate = av_rate

    def after_init_sumo(self, env: PTLEnv):
        self.agent = eval(self.agent_type)(self.policy_type, env, verbose=1)
        env.policy = self

    def handle_step(self, env: PTLEnv):
        env.step(self.agent.predict(env.state, deterministic=True)[0])

    def __str__(self):
        return f"{self.agent_type}_{self.act_rate}"

    def save(self, path):
        self.agent.save(os.path.join(path, f"{self.agent_type}_{self.act_rate}"))
