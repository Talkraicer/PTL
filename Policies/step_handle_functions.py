import traci
from SUMO.SUMOAdpater import SUMOAdapter


class StepHandleFunction:
    def __init__(self, env: SUMOAdapter):
        if env.isFinish():
            raise Exception("Simulation is not running")
        self.env = env

    def handle_step(self, state_dict):
        pass

    def __str__(self):
        pass



class Nothing(StepHandleFunction):
    def __init__(self, env: SUMOAdapter):
        super().__init__(env)
        for lane in traci.lane.getIDList():
            if "bus" in traci.lane.getAllowed(lane):
                traci.lane.setAllowed(lane, "bus")

    def handle_step(self, state_dict):
        pass

    def __str__(self):
        return "Nothing"


class Plus(StepHandleFunction):
    pass_range = range(1, 6)
    def __init__(self, env: SUMOAdapter, min_num_pass):
        super().__init__(env)
        assert min_num_pass in self.pass_range, "min_num_pass should be between 1 and 5"
        self.min_num_pass = min_num_pass

    def handle_step(self, state_dict):
        self.env.allow_vehicles(min_num_pass=self.min_num_pass)

    def __str__(self):
        return f"Plus_{self.min_num_pass}"


class StaticNumPass(Plus):
    def __init__(self, env: SUMOAdapter, min_num_pass):
        super().__init__(env, min_num_pass)

    def handle_step(self, state_dict):
        self.env.allow_vehicles(min_num_pass=self.min_num_pass, veh_type="AV")

    def __str__(self):
        return f"StaticNumPass_{self.min_num_pass}"


class StaticNumPassFL(Plus):
    def __init__(self, env: SUMOAdapter, min_num_pass):
        super().__init__(env, min_num_pass)

    def handle_step(self, state_dict):
        self.env.allow_vehicles(min_num_pass=self.min_num_pass, veh_type="AV", edge="E0")

    def __str__(self):
        return f"StaticNumPassFL_{self.min_num_pass}"
