from Demands.demand_profiles import *
from Demands.DemandToyUniform import *
from Demands.DemandToy import *
from Demands.PassengerDemand import *
from numpy import arange

DEMAND_DEFINITIONS = {
    "DemandToyUniform": {
        "class": DemandToyUniform,
        "params": [{"amount": amount, "av_rate": av_rate}
                   for amount in range(1000, 6000, 1000)
                   for av_rate in arange(0, 1.1, 0.1)]
    },
    "DemandToy": {
        "class": DemandToy,
        "params": [{"amount": amount, "av_rate": av_rate}
                   for amount in range(1000, 6000, 1000)
                   for av_rate in arange(0, 1.1, 0.1)]
    },
    "PassDemand": {
        "class": PassDemand,
        "params": [{"amount": amount, "av_pass_factor": av_pass_factor, "av_rate": av_rate}
                   for amount in range(1000, 6000, 1000)
                   for av_pass_factor in arange(0, 1.1, 0.1)
                   for av_rate in arange(0, 1.1, 0.1)]
    },
    "PassDemandUniform": {
        "class": PassDemandUniform,
        "params": [{"amount": amount, "av_rate": av_rate}
                   for amount in range(1000, 6000, 1000)
                   for av_rate in arange(0, 1.1, 0.1)]
    }

}
