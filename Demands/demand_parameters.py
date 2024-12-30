from Demands.demand_profiles import *
from Demands.DemandToyUniform import *
from Demands.DemandToy import *
from Demands.PassengerDemand import *
from numpy import arange
from Demands.DailyDemand import *


def create_demand_definitions(av_rate_range=None):
    if av_rate_range is None:
        av_rate_range = arange(0.1, 1.1, 0.1)
    veh_amount_range = range(1000, 6000, 1000)
    pass_amount_range = range(1000, 9000, 1000)
    return {
        "DemandToyUniform": {
            "class": DemandToyUniform,
            "params": [{"amount": amount, "av_rate": av_rate}
                       for amount in veh_amount_range
                       for av_rate in av_rate_range]
        },
        "DemandToy": {
            "class": DemandToy,
            "params": [{"amount": amount, "av_rate": av_rate}
                       for amount in veh_amount_range
                       for av_rate in av_rate_range]
        },
        "PassDemand": {
            "class": PassDemand,
            "params": [{"amount": amount, "av_pass_factor": av_pass_factor, "av_rate": av_rate}
                       for amount in pass_amount_range
                       for av_pass_factor in arange(0, 1.1, 0.1)
                       for av_rate in av_rate_range]
        },
        "PassDemandUniform": {
            "class": PassDemandUniform,
            "params": [{"amount": amount, "av_rate": av_rate}
                       for amount in pass_amount_range
                       for av_rate in av_rate_range]
        },
        "DailyDemand": {
            "class": DailyDemand,
            "params": [{"factor": factor, "av_rate": av_rate}
                       for factor in [2,2.5,3]
                       for av_rate in av_rate_range]
        },
        "DailyDemandPaper": {
            "class": DailyDemand,
            "params": [{"factor": factor, "av_rate": av_rate}
                       for factor in [2, 2.5, 3]
                       for av_rate in av_rate_range]
        }

    }
