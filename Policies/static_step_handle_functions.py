import traci
from SUMO.SUMOAdpater import SUMOAdapter
from SUMO.netfile_utils import get_PTL_lanes


class StepHandleFunction:

    def __init__(self):
        self.veh_kinds = None
        self.min_num_pass = None
        self.endToEnd = False
        self.arrival_split = False
        self.av_rate = 0.0
        self.RL = False

    def handle_step(self, env:SUMOAdapter):
        pass

    def after_init_sumo(self, env: SUMOAdapter):
        # run this function after sumo is initialized
        pass

    def __str__(self):
        pass


class Nothing(StepHandleFunction):
    def __init__(self,):
        super().__init__()

    def after_init_sumo(self, env: SUMOAdapter):
        PTL_lane_ids = get_PTL_lanes(env.network_file)
        for lane in PTL_lane_ids:
            traci.lane.setAllowed(lane, "bus")

    def __str__(self):
        return "Nothing"


class Plus(StepHandleFunction):

    def __init__(self, min_num_pass: int):
        super().__init__()
        self.min_num_pass = min_num_pass
        self.veh_kinds = ["AV", "HD"]

    def __str__(self):
        return f"Plus_{self.min_num_pass}"


class StaticNumPass(Plus):

    def __init__(self, min_num_pass: int, av_rate: float):
        super().__init__(min_num_pass)
        self.veh_kinds = ["AV"]
        self.av_rate = av_rate

    def __str__(self):
        assert self.min_num_pass is not None, "min_num_pass is not set"
        return f"StaticNumPass_{self.min_num_pass}"


# class StaticNumPassFL(StaticNumPass):
#     def __init__(self,):
#         super().__init__()
#         self.endToEnd = True
#
#     def __str__(self):
#         assert self.min_num_pass is not None, "min_num_pass is not set"
#         return f"StaticNumPassFL_{self.min_num_pass}"

#
# class NothingSplit(Nothing):
#     def __init__(self,):
#         super().__init__()
#         self.arrival_split = True
#
#     def __str__(self):
#         return "NothingSplit"

#
# class PlusSplit(Plus):
#     def __init__(self,, min_num_pass: int):
#         super().__init__(, min_num_pass)
#         self.arrival_split = True
#
#     def __str__(self):
#         assert self.min_num_pass is not None, "min_num_pass is not set"
#         return f"PlusSplit_{self.min_num_pass}"

#
# class StaticNumPassSplit(StaticNumPass):
#     def __init__(self,, min_num_pass: int):
#         super().__init__(, min_num_pass)
#         self.arrival_split = True
#
#     def __str__(self):
#         assert self.min_num_pass is not None, "min_num_pass is not set"
#         return f"StaticNumPassSplit_{self.min_num_pass}"

class Percentage:
    pass
