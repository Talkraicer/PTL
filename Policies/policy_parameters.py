from Policies.static_step_handle_functions import *
from numpy import arange


def create_policy_definitions(min_num_pass_range=None, av_rate_range=None):
    if av_rate_range is None:
        av_rate_range = arange(0.1, 1.1, 0.1)
    if min_num_pass_range is None:
        min_num_pass_range = [1, 2, 3, 4, 5]
    return {
        "Nothing":
            {
                "class": Nothing,
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
        # "StaticNumPassFL":
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
