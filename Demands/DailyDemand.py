from Demands.demand_profiles import Demand
class DailyDemand(Demand):
    def __init__(self, av_rate: float, factor: float):
        super().__init__(av_rate=av_rate)
        self.veh_amount = {6: 6163, 7: 6450, 8: 7053, 9: 6443, 10: 6287, 11: 5800, 12: 6266, 13: 5428,
                           14: 5661, 15: 4644, 16: 4937, 17: 5668, 18: 5184, 19: 5126}
        self.bus_amount = {6: 62, 7: 37, 8: 19, 9: 31, 10: 26, 11: 25, 12: 17, 13: 31,
                           14: 44, 15: 30, 16: 24, 17: 28, 18: 25, 19: 16}
        self.factor = factor
        self.veh_amount = {k: int(v / factor) for k, v in self.veh_amount.items()}
        self.bus_amount = {k: int(v / factor) for k, v in self.bus_amount.items()}
        self.toy = False
        self.hour_len = 1800

    def __str__(self):
        return f"Daily_{self.factor}"

class DailyDemandPaper(DailyDemand):
    def __init__(self, av_rate: float, factor: float):
        super().__init__(av_rate=av_rate, factor=factor)
    def __str__(self):
        return f"DailyPaper_{self.factor}"
