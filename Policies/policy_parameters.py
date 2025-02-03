from Policies.static_step_handle_functions import *
from Policies.dynamic_step_handle_functions import *
from Policies.RL_step_handle_function import *
from numpy import arange


def create_policy_definitions(min_num_pass_range=None, av_rate_range=None, train=False):
    if av_rate_range is None:
        av_rate_range = arange(0, 1.1, 0.1)
    if min_num_pass_range is None:
        min_num_pass_range = range(1, 6)
    RL_av_rate_range = [0.1] if train else av_rate_range
    return {
        "Nothing":
            {
                "class": Nothing,
                "params": [{}]
            },
        "NoBody":
            {
                "class": NoBody,
                "params": [{}]
            },
        "Plus":
            {
                "class": Plus,
                "params": [{"min_num_pass": min_num_pass} for min_num_pass in min_num_pass_range],
            },
        "StaticNumPass":
            {
                "class": StaticNumPass,
                "params": [{"min_num_pass": min_num_pass, "av_rate": av_rate} for min_num_pass in min_num_pass_range for
                           av_rate in av_rate_range if av_rate > 0]
            },
        # "OneVariableControlOptimal":
        #     {
        #         "class": OneVariableControl,
        #         "params":
        #             [
        #                 {"av_rate": av_rate, "variable": "ptl_speed", "param_range": param_range, "decision_rate": rate,
        #                  "inverse": True}
        #                 for param_range in
        #                 [(23, 24),  # Designed for Toy_2000
        #                  (20, 24), (18, 22),
        #                  ]
        #                 for av_rate in av_rate_range if av_rate > 0
        #                 for rate in [10, 60]
        #             ]
        # #     },
        # "OneVariableControl_threshold":
        #     {
        #         "class": OneVariableControl_threshold,
        #         "params":
        #             [
        #                 {"av_rate": av_rate, "variable": "ptl_speed", "param_threshold": param_threshold,
        #                  "decision_rate": rate,
        #                  "inverse": True}
        #                 for param_threshold in arange(20, 25.1, 0.5)
        #                 for av_rate in av_rate_range if av_rate > 0
        #                 for rate in [60]
        #             ]
        #     }

        "OneVariableControl_threshold":
            {
                "class": OneVariableControl_threshold,
                "params":
                    [
                        {"av_rate": av_rate, "variable": "num_vehs_ptl", "param_threshold": param_threshold,
                         "decision_rate": rate,
                         "inverse": False}
                        for param_threshold in [1]
                        for av_rate in av_rate_range if av_rate > 0
                        for rate in [60]
                    ]
            }
        # "OneVariableControl":
        #     {
        #         "class": OneVariableControl,
        #         "params":
        #             [
        #                 {"av_rate": av_rate, "variable": "ptl_speed", "param_range": param_range, "decision_rate": rate,
        #                  "inverse": True}
        #                 for param_range in
        #                 [(22.5, 23.5), (23.5, 24.5), (23, 24.5), (23, 24),  # Designed for Toy_2000
        #                  (21.5, 23), (21.5, 22.5),  # Designed for Toy_3000
        #                  (20, 22), (20.5, 22),  # Designed for Toy_4000
        #                  (20, 24), (18, 22), (18, 23)  # Expanded
        #                  ]
        #                 for av_rate in av_rate_range if av_rate > 0
        #                 for rate in [10, 60]
        #             ]
        #  [
        #      {"av_rate": av_rate, "variable": "speed", "param_range": param_range, "decision_rate": rate, "inverse": True} for
        #      param_range in
        #      [(19,20),(18.5,19.5), # Designed for Toy_2000
        #       (7,8), (7.2,7.8), # Designed for Toy_3000
        #       ]
        #      for av_rate in av_rate_range if av_rate > 0
        #      for rate in [10, 60]
        #  ] +
        #  [
        #      {"av_rate": av_rate, "variable": "num_vehs", "decision_rate": rate, "param_range": param_range}
        #      for param_range in
        #      [(52,62), # Designed for Toy_2000
        #       (160,168), (162,168), # Designed for Toy_3000
        #       ]
        #      for av_rate in av_rate_range if av_rate > 0
        #      for rate in [10, 60]
        #  ] +
        #  [
        #      {"av_rate": av_rate, "variable": "num_vehs_ptl", "decision_rate": rate, "param_range": param_range}
        #      for param_range in
        #      [(0.1, 1), # Designed for Toy_2000
        #       # (1,2),(1,3), # Designed for Toy_3000
        #       ]
        #      for av_rate in av_rate_range if av_rate > 0
        #      for rate in [10, 60]
        # ]

        # [
        #     {"variable": "occupancy", "param_range": param_range} for param_range in
        #     [(0, 1), (0, 0.5), (0.5, 1)]
        # ] +
        # [
        #     {"variable": "occupancy_ptl", "param_range": param_range} for param_range in
        #     [(0, 1), (0, 0.5), (0.5, 1)]
        # ]
        # },
        # "RLAgent":
        #     {
        #         "class": RLAgent,
        #         "params": [{"av_rate": av_rate, "act_rate": act_rate, "agent_type": agent_type
        #                     }
        #                    for av_rate in RL_av_rate_range if av_rate > 0
        #                    for act_rate in [3, 10, 60]
        #                     for agent_type in ["DQN", "PPO", "A2C"]]
        #     },
        #     {
        #         "class": StaticNumPassFL,
        #         "params": [{"min_num_pass": min_num_pass, "av_rate": av_rate} for min_num_pass in min_num_pass_range
        #         for av_rate in av_rate_range if av_rate > 0]
        #     },
        # "NothingSplit":
        #     {
        #         "class": NothingSplit,
        #         "params": [{}]
        #     },
        # "PlusSplit":
        #     {
        #         "class": PlusSplit,
        #         "params": [{"min_num_pass": min_num_pass} for min_num_pass in min_num_pass_range],
        #     },
        # "StaticNumPassSplit":
        #     {
        #         "class": StaticNumPassSplit,
        #         "params": [{"min_num_pass": min_num_pass, "av_rate": av_rate} for min_num_pass in min_num_pass_range
        #         for av_rate in av_rate_range if av_rate > 0]
        #     }
        #
    }
