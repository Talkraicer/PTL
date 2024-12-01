import traci
from SUMO.SUMOAdpater import SUMOAdapter
from SUMO.netfile_utils import get_PTL_lanes


class StepHandleFunction:
    param_range = [None]
    is_num_pass_dependent = False
    is_av_rate_dependent = False

    def __init__(self, env: SUMOAdapter, param=None):
        # if env.isFinish():
        #     raise Exception("Simulation is not running")
        self.env = env
        self.veh_kinds = None
        self.min_num_pass = None
        self.endToEnd = False
        self.arrival_split = False

    def handle_step(self, state_dict):
        pass

    def after_init_sumo(self):
        # run this function after sumo is initialized
        pass

    def __str__(self):
        pass


class Nothing(StepHandleFunction):
    def __init__(self, env: SUMOAdapter):
        super().__init__(env)

    def after_init_sumo(self):
        PTL_lane_ids = get_PTL_lanes(self.env.network_file)
        for lane in PTL_lane_ids:
            traci.lane.setAllowed(lane, "bus")

    def __str__(self):
        return "Nothing"


class Plus(StepHandleFunction):
    pass_range = range(1, 6)
    is_num_pass_dependent = True

    def __init__(self, env: SUMOAdapter):
        super().__init__(env)
        self.min_num_pass = None
        self.veh_kinds = ["AV", "HD"]

    def set_num_pass(self, min_num_pass):
        assert min_num_pass in self.pass_range, "min_num_pass should be between 1 and 5"
        self.min_num_pass = min_num_pass

    def __str__(self):
        assert self.min_num_pass is not None, "min_num_pass is not set"
        return f"Plus_{self.min_num_pass}"


class StaticNumPass(Plus):
    is_av_rate_dependent = True

    def __init__(self, env: SUMOAdapter):
        super().__init__(env)
        assert env.av_rate != 0, "av_rate is not set"
        self.veh_kinds = ["AV"]

    def __str__(self):
        assert self.min_num_pass is not None, "min_num_pass is not set"
        return f"StaticNumPass_{self.min_num_pass}"


# class StaticNumPassFL(StaticNumPass):
#     def __init__(self, env: SUMOAdapter):
#         super().__init__(env)
#         self.endToEnd = True
#
#     def __str__(self):
#         assert self.min_num_pass is not None, "min_num_pass is not set"
#         return f"StaticNumPassFL_{self.min_num_pass}"


class NothingSplit(Nothing):
    def __init__(self, env: SUMOAdapter):
        super().__init__(env)
        self.arrival_split = True

    def __str__(self):
        return "NothingSplit"


class PlusSplit(Plus):
    def __init__(self, env: SUMOAdapter):
        super().__init__(env)
        self.arrival_split = True

    def __str__(self):
        assert self.min_num_pass is not None, "min_num_pass is not set"
        return f"PlusSplit_{self.min_num_pass}"


class StaticNumPassSplit(StaticNumPass):
    def __init__(self, env: SUMOAdapter):
        super().__init__(env)
        self.arrival_split = True

    def __str__(self):
        assert self.min_num_pass is not None, "min_num_pass is not set"
        return f"StaticNumPassSplit_{self.min_num_pass}"

