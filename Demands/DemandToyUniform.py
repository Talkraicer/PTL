from Demands.demand_profiles import Demand


class DemandToyUniform(Demand):
    ranges = [1000, 2000, 3000, 4000, 5000]

    def __init__(self, amount):
        super().__init__()
        self.amount = amount
        self.veh_amount = {6: amount}
        self.bus_amount = {6: amount//100}
        self.prob_pass_av = {1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.2}

        self.hour_len = 3600
        self.toy = True

    def __str__(self):
        return f"ToyUniform{self.amount}"
