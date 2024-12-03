from Demands.demand_profiles import Demand



class PassDemand(Demand):
    def __init__(self, av_rate: float, amount: int, av_pass_factor: float):
        super().__init__(av_rate=av_rate, av_pass_factor=av_pass_factor)
        self.av_pass_factor = av_pass_factor
        self.amount = amount
        self.veh_amount = {6: amount}
        self.bus_amount = {6: amount // 100}
        self.hour_len = 3600
        self.toy = True

    def set_veh_amount(self, av_rate):
        exp_av_pass = sum([k * v for k, v in self.prob_pass_av.items()])
        exp_hd_pass = sum([k * v for k, v in self.prob_pass_hd.items()])
        exp_pass = exp_av_pass * av_rate + exp_hd_pass * (1 - av_rate)
        self.veh_amount = {6: self.amount / exp_pass}

    def __str__(self):
        return f"PassDemand_AvPassFactor_{self.av_pass_factor}_{self.amount}"


class PassDemandUniform(Demand):
    def __init__(self, av_rate: float, amount: int):
        super().__init__(av_rate=av_rate)
        self.amount = amount
        self.veh_amount = {6: amount}
        self.prob_pass_av = {1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2}
        self.bus_amount = {6: amount // 100}
        self.hour_len = 3600
        self.toy = True

    def set_veh_amount(self, av_rate):
        exp_av_pass = sum([k * v for k, v in self.prob_pass_av.items()])
        exp_hd_pass = sum([k * v for k, v in self.prob_pass_hd.items()])
        exp_pass = exp_av_pass * av_rate + exp_hd_pass * (1 - av_rate)
        self.veh_amount = {6: self.amount / exp_pass}

    def __str__(self):
        return f"PassDemandUniform_{self.amount}"
