from Policies.static_step_handle_functions import StaticNumPass
from SUMO.SUMOAdpater import SUMOAdapter


class SpeedPTLControl(StaticNumPass):
    param_range = [(22, 24), (21, 23), (20, 22), (23, 25), (21.5, 23.5)]

    def __init__(self, env: SUMOAdapter, speed_range):
        super().__init__(env)
        self.arrival_split = True
        self.min_speed, self.max_speed = speed_range

    def handle_step(self, state_dict):
        ptl_speed = state_dict["ptl_speed"]


    def __str__(self):
        return "SpeedControl"
