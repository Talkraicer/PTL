from Demands.demand_profiles import Demand
class DemandToy(Demand):
    ranges = [1000, 2000, 3000, 4000, 5000]
    def __init__(self, amount):
        super().__init__()
        self.amount = amount
        self.veh_amount = {6: amount}
        self.bus_amount = {6: amount}

        self.hour_len = 3600
        self.toy = True

    def __str__(self):
        return f"Toy{self.amount}"
