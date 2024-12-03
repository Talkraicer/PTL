from Demands.demand_profiles import Demand


class DemandToy(Demand):

    def __init__(self, av_rate: float, amount: int):
        super().__init__(av_rate=av_rate)
        self.amount = amount
        self.veh_amount = {6: amount}
        self.bus_amount = {6: amount // 100}

        self.hour_len = 3600
        self.toy = True

    def __str__(self):
        return f"Toy_{self.amount}"
