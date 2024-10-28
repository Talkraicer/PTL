def normalize_dict(d):
    total = sum(d.values())
    if total == 0:
        return d
    return {k: v / total for k, v in d.items()}


class Demand:
    def __init__(self, av_pass_factor=1, exit_prop=0.1):
        self.prob_pass_hd = {1: 0.63, 2: 0.28, 3: 0.06, 4: 0.02,
                             5: 0.01}  # Probability of having k passengers in a human-driven vehicle based on the data
        prob_pass_av = {k: v for k, v in self.prob_pass_hd.items()}
        prob_pass_av[1] *= av_pass_factor
        self.prob_pass_av = normalize_dict(prob_pass_av)
        bus_pass_range = range(25, 45)
        self.prob_pass_bus = {i: 1 / len(bus_pass_range) for i in bus_pass_range}
        self.exit_prop = exit_prop

        self.bus_amount = None
        self.veh_amount = None
        self.hour_len = None
        self.enter_speed = "max"
        self.toy = False

    def get_vehicle_amount(self):
        return self.veh_amount

    def get_bus_amount(self):
        return self.bus_amount

    def __str__(self):
        raise NotImplementedError



# class ScenariosDemand(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {
#             6: 4000, 7: 7000, 8: 7000, 9: 4000,  # RUSH HOURS
#             10: 0, 11: 0,  # BREAK
#             12: 9000,  # PEAK
#             13: 0, 14: 0,  # BREAK
#             15: 5800, 16: 5800,  # MID DAY
#             17: 0, 18: 0,  # BREAK
#             19: 4000, 20: 4000,  # WEEKEND
#             21: 0, 22: 0,  # BREAK
#             23: 4000, 24: 5000, 25: 6000, 26: 7000, 27: 6000, 28: 5000, 29: 4000  # Moderate Peak
#         }
#         self.bus_amount = {
#             6: 30, 7: 60, 8: 60, 9: 30,  # RUSH HOURS
#             10: 0, 11: 0,  # BREAK
#             12: 40,  # PEAK
#             13: 0, 14: 0,  # BREAK
#             15: 40, 16: 40,  # MID DAY
#             17: 0, 18: 0,  # BREAK
#             19: 0, 20: 0,  # WEEKEND
#             21: 0, 22: 0,  # BREAK
#             23: 30, 24: 40, 25: 50, 26: 60, 27: 50, 28: 40, 29: 30  # Moderate Peak
#         }
#         self.hour_len = 1800
#     def __str__(self):
#         return "Scenarios"
#
#
# class DailyDemand(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 6163, 7: 6450, 8: 7053, 9: 6443, 10: 6287, 11: 5800, 12: 6266, 13: 5428,
#                            14: 5661, 15: 4644, 16: 4937, 17: 5668, 18: 5184, 19: 5126}
#         self.bus_amount = {6: 62, 7: 37, 8: 19, 9: 31, 10: 26, 11: 25, 12: 17, 13: 31,
#                            14: 44, 15: 30, 16: 24, 17: 28, 18: 25, 19: 16}
#
#         self.hour_len = 3600
#
#     def __str__(self):
#         return "Daily"
#
# class Daily2Demand(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 6686, 7: 6881, 8: 7387, 9: 6895, 10: 6870, 11: 6414, 12: 6897, 13: 5980,
#                            14: 6098, 15: 4906, 16: 5203, 17: 5921, 18: 5435, 19: 5354}
#         self.bus_amount = {6: 62, 7: 37, 8: 19, 9: 31, 10: 26, 11: 25, 12: 17, 13: 31,
#                            14: 44, 15: 30, 16: 24, 17: 28, 18: 25, 19: 16}
#
#         self.hour_len = 3600
#
#     def __str__(self):
#         return "Daily2"

# class DemandToy1000(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 1000}
#         self.bus_amount = {6: 10}
#
#         self.hour_len = 3600
#         self.toy = True
#
#     def __str__(self):
#         return "Toy1000"
#
# class DemandToy2000(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 2000}
#         self.bus_amount = {6: 20}
#
#         self.hour_len = 3600
#         self.toy = True
#
#     def __str__(self):
#         return "Toy2000"
#
# class DemandToy3000(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 3000}
#         self.bus_amount = {6: 30}
#
#         self.hour_len = 3600
#         self.toy = True
#
#     def __str__(self):
#         return "Toy3000"
#
# class DemandToy4000(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 4000}
#         self.bus_amount = {6: 40}
#
#         self.hour_len = 3600
#         self.toy = True
#
#     def __str__(self):
#         return "Toy4000"
#
# class DemandToy5000(Demand):
#     def __init__(self):
#         super().__init__()
#         self.veh_amount = {6: 5000}
#         self.bus_amount = {6: 50}
#
#         self.hour_len = 3600
#         self.toy = True
#
#     def __str__(self):
#         return "Toy5000"
#
class DemandToy6000(Demand):
    def __init__(self):
        super().__init__()
        self.veh_amount = {6: 6000}
        self.bus_amount = {6: 60}

        self.hour_len = 3600
        self.toy = True

    def __str__(self):
        return "Toy6000"

class DemandToy7000(Demand):
    def __init__(self):
        super().__init__()
        self.veh_amount = {6: 7000}
        self.bus_amount = {6: 70}

        self.hour_len = 3600
        self.toy = True

    def __str__(self):
        return "Toy7000"

class DemandToy8000(Demand):
    def __init__(self):
        super().__init__()
        self.veh_amount = {6: 8000}
        self.bus_amount = {6: 80}

        self.hour_len = 3600
        self.toy = True

    def __str__(self):
        return "Toy8000"
