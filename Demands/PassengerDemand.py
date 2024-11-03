from Demands.demand_profiles import Demand

PassRange = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000]
AV_Factor_Range = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
class PassDemand(Demand):

    ranges = [(amount, av_pass_factor) for amount in PassRange for av_pass_factor in AV_Factor_Range]

    def __init__(self, args):
        amount, av_pass_factor = args
        super().__init__(av_pass_factor)
        self.av_pass_factor = av_pass_factor
        self.amount = amount
        self.veh_amount = {6: amount}
        self.bus_amount = {6: 0}
        self.hour_len = 3600
        self.toy = True

    def set_veh_amount(self, av_rate):
        exp_av_pass = sum([k * v for k, v in self.prob_pass_av.items()])
        exp_hd_pass = sum([k * v for k, v in self.prob_pass_hd.items()])
        exp_pass = exp_av_pass * av_rate + exp_hd_pass * (1 - av_rate)
        self.veh_amount = {6: self.amount / exp_pass}

    def __str__(self):
        return f"PassDemand_{self.amount}_AvPassFactor_{self.av_pass_factor}"