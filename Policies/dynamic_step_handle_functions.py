from Policies.static_step_handle_functions import StepHandleFunction
from SUMO.SUMOAdpater import SUMOAdapter
from typing import Tuple


class OneVariableControl(StepHandleFunction):

    def __init__(self, av_rate: float,
                 variable: str,
                 param_range: Tuple[float, float],
                 decision_rate: int,
                 inverse=False):
        super().__init__()
        self.av_rate = av_rate
        self.control_variable = variable
        self.min_param, self.max_param = param_range
        self.min_num_pass = 6
        self.veh_kinds = ["AV"]
        self.current_min_num_pass = 1
        self.inverse = inverse
        self.decision_rate = decision_rate
        self.running_sum = 0

    def handle_step(self, env: SUMOAdapter):
        feature = env.get_state_dict(self.control_variable)
        self.running_sum += feature
        if env.timestep % self.decision_rate == 0:
            mean_feature = self.running_sum / self.decision_rate
            if mean_feature < self.min_param:
                if self.inverse:
                    self.current_min_num_pass += 1
                else:
                    self.current_min_num_pass -= 1
            elif mean_feature > self.max_param:
                if self.inverse:
                    self.current_min_num_pass -= 1
                else:
                    self.current_min_num_pass += 1
            self.current_min_num_pass = max(1, self.current_min_num_pass)
            self.current_min_num_pass = min(6, self.current_min_num_pass)
            self.running_sum = 0
        env.allow_vehicles(veh_types=self.veh_kinds, min_num_pass=self.current_min_num_pass)
        # print(f"Current min num pass: {self.current_min_num_pass}, timestep: {env.timestep}")

    def __str__(self):
        return f"OneVariableControl_{self.control_variable}_{self.min_param}_{self.max_param}_{self.decision_rate}"

class OneVariableControl_threshold(StepHandleFunction):

    def __init__(self, av_rate: float,
                 variable: str,
                 param_threshold: float,
                 decision_rate: int,
                 inverse=False):
        super().__init__()
        self.av_rate = av_rate
        self.control_variable = variable
        self.param_threshold = param_threshold
        self.min_num_pass = 6
        self.veh_kinds = ["AV"]
        self.current_min_num_pass = 1
        self.inverse = inverse
        self.decision_rate = decision_rate

    def handle_step(self, env: SUMOAdapter):
        if env.timestep % self.decision_rate == 0:
            mean_feature = env.get_state_dict(self.control_variable)
            if mean_feature < self.param_threshold:
                if self.inverse:
                    self.current_min_num_pass += 1
                else:
                    self.current_min_num_pass -= 1
            elif mean_feature >= self.param_threshold:
                if self.inverse:
                    self.current_min_num_pass -= 1
                else:
                    self.current_min_num_pass += 1
            self.current_min_num_pass = max(1, self.current_min_num_pass)
            self.current_min_num_pass = min(6, self.current_min_num_pass)
        env.allow_vehicles(veh_types=self.veh_kinds, min_num_pass=self.current_min_num_pass)
        # print(f"Current min num pass: {self.current_min_num_pass}, timestep: {env.timestep}")

    def __str__(self):
        return f"OneVariableControl_threshold_{self.control_variable}_{self.param_threshold}_{self.decision_rate}"

if __name__ == '__main__':
    # create an instance of the class
    control = OneVariableControl(av_rate=0.1, variable="ptl_speed", param_range=(23, 24), decision_rate=10)
    print(hasattr(control, "current_min_num_pass"))
    # create an instance of StepHandleFunction
    step = StepHandleFunction()
    print(hasattr(step, "current_min_num_pass"))