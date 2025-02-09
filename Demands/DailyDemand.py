from Demands.demand_profiles import Demand
class DailyDemand(Demand):
    def __init__(self, av_rate: float, factor: float):
        super().__init__(av_rate=av_rate)
        self.veh_amount = {6: 6163, 7: 6450, 8: 7053, 9: 6443, 10: 6287, 11: 5800, 12: 6266, 13: 5428,
                           14: 5661, 15: 4644, 16: 4937, 17: 5668, 18: 5184, 19: 5126}
        self.bus_amount = {6: 62, 7: 37, 8: 19, 9: 31, 10: 26, 11: 25, 12: 17, 13: 31,
                           14: 44, 15: 30, 16: 24, 17: 28, 18: 25, 19: 16}
        self.factor = factor
        self.veh_amount = [{k: int(v / factor) for k, v in self.veh_amount.items()}]
        self.bus_amount = [{k: int(v / factor) for k, v in self.bus_amount.items()}]
        self.toy = False
        self.hour_len = 1800

    def __str__(self):
        return f"Daily_{self.factor}"

class DailyDemandPaper(DailyDemand):
    def __init__(self, av_rate: float, factor: float):
        super().__init__(av_rate=av_rate, factor=factor)
    def __str__(self):
        return f"DailyPaper_{self.factor}"

class DailyDemand12(DailyDemand):
    def __init__(self, av_rate: float, factor: float):
        super().__init__(av_rate=av_rate, factor=factor)
        self.hour_len = 3600
    def __str__(self):
        return f"Daily12_{self.factor}"


class DailyCaseStudy(Demand):
    def __init__(self, av_rate: float):
        super().__init__(av_rate=av_rate)
        self.veh_amount = [{6: 3599, 7: 3657, 8: 3472, 9: 2953, 10: 3364, 11: 3119, 12: 3380, 13: 3571,
                           14: 2882, 15: 2740, 16: 2293, 17: 2578, 18: 2780, 19: 2963},
                           {6: 956, 7: 1604, 8: 2094, 9: 1619, 10: 1553, 11: 1673, 12: 1928, 13: 2415,
                            14: 2713, 15: 3047, 16: 3051, 17: 2855, 18: 2634, 19: 2451},
                           {6: 478, 7: 802, 8: 1047, 9: 809, 10: 776, 11: 836, 12: 964, 13: 1207,
                            14: 1356, 15: 1523, 16: 1526, 17: 1427, 18: 1317, 19: 1226},
                           ]
        self.bus_amount = [{6: 9, 7: 5, 8: 1, 9: 4, 10: 4, 11: 3, 12: 6, 13: 10,
                           14: 16, 15: 7, 16: 2, 17: 5, 18: 2, 19: 5},
                           {6: 10, 7: 15, 8: 17, 9: 9, 10: 10, 11: 8, 12: 1, 13: 1,
                            14: 2, 15: 1, 16: 6, 17: 2, 18: 5, 19: 4},
                           {6: 5, 7: 8, 8: 8, 9: 5, 10: 5, 11: 4, 12: 1, 13: 1,
                            14: 3, 15: 2, 16: 9, 17: 3, 18: 8, 19: 6},
                           ]

        self.toy = False
        self.hour_len = 3600

    def __str__(self):
        return f"DailyCaseStudy_"