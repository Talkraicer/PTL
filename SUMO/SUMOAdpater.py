import traci
import numpy as np
import os
from xml.etree import ElementTree as ET
from SUMO.demand_profiles import *


class SUMOAdapter:
    def __init__(self, demand_profile: Demand, seed: int, av_rate: float,
                 route_temp: str = "route_template.rou.xml", net_file: str = "network.net.xml",
                 cfg_temp: str = "config_template.sumocfg",
                 template_folder="SUMOconfig", output_folder="outputs", gui=False, lane_num=4, ramps_num=3):
        curdir = os.path.dirname(os.path.abspath(__file__))
        self.template_folder = os.path.join(curdir, template_folder)
        self.output_folder = os.path.join(curdir, output_folder, str(av_rate), str(seed))
        self.av_rate = av_rate
        self.seed = seed
        os.makedirs(self.output_folder, exist_ok=True)
        self.lane_num = lane_num
        self.ramps_num = ramps_num
        self.network_file = os.path.join(self.template_folder, net_file)
        self.route_template = os.path.join(self.template_folder, route_temp)
        self.config_template = os.path.join(self.template_folder, cfg_temp)
        self.gui = gui
        self.demand_profile = demand_profile
        self.config_folder = os.path.join(self.template_folder, demand_profile.__str__(), str(seed))
        os.makedirs(self.config_folder, exist_ok=True)
        self.route_file = os.path.join(self.config_folder, f"av_{av_rate}.rou.xml")
        self.config_file = os.path.join(self.config_folder, f"av_{av_rate}.sumocfg")

    def allow_vehicles(self, edge="all", veh_type="all", min_num_pass=0):
        veh_ids = traci.vehicle.getIDList() if edge == "all" else traci.edge.getLastStepVehicleIDs(edge)
        if veh_type != "all":
            veh_ids = [veh for veh in veh_ids if traci.vehicle.getTypeID(veh).startswith(veh_type)]
        else:
            veh_ids = [veh for veh in veh_ids if not traci.vehicle.getTypeID(veh).startswith("Bus")]
        if min_num_pass > 0:
            veh_ids = [veh for veh in veh_ids if int(traci.vehicle.getTypeID(veh).split("_")[1][0]) >= min_num_pass]

        for veh_id in veh_ids:
            traci.vehicle.setVehicleClass(veh_id, "private")

    def get_state_dict(self, t):
        state_dict = {}
        state_dict["t"] = t

        return state_dict

    def step(self, t):
        traci.simulationStep(t)

    def isFinish(self):
        return traci.simulation.getMinExpectedNumber() <= 0

    def close(self):
        traci.close()

    def init_simulation(self, output_file="output.xml"):
        self.output_file = os.path.join(self.output_folder, output_file)
        if not os.path.exists(self.route_file):
            self._create_route_file()
        else:
            print(f"Route file {self.route_file} already exists")
        if not os.path.exists(self.config_file):
            self._create_config_file()
        else:
            print(f"Config file {self.config_file} already exists")
        self._init_sumo(self.config_file, self.output_file)

    def _create_vType_dist(self, root):
        # Set vTypeDistribution to contain the probabilities of each vehicle type and the number of passengers
        av_prob = self.av_rate
        hdv_prob = 1 - av_prob
        for vTypeDist in root.findall('vTypeDistribution'):
            vTypeDist.text += '\t'
            if vTypeDist.attrib['id'] == 'vehicleDist':
                for k, v in self.demand_profile.prob_pass_av.items():
                    prob = round(av_prob * v, 5)
                    elem = ET.Element('vType', id=f'AV_{k}', color='blue', probability=str(prob), vClass='evehicle')
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)
                for k, v in self.demand_profile.prob_pass_hd.items():
                    prob = round(hdv_prob * v, 5)
                    elem = ET.Element('vType', id=f'HD_{k}', color='red', probability=str(prob), vClass='passenger')
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)
            elif vTypeDist.attrib['id'] == 'busDist':
                for k, v in self.demand_profile.prob_pass_bus.items():
                    elem = ET.Element('vType', id=f'Bus_{k}', probability=str(v), vClass='bus')
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)

    def _append_flow(self, root, hour, in_j, out_j, prob,
                     depart_speed="max", type_dist="vehicleDist", depart_lane=None):
        flow_id = f'flow_{type_dist}_{hour}_{in_j}_{out_j}' if depart_lane is None else f'flow_{type_dist}_{hour}_{in_j}_{out_j}_{depart_lane}'
        flow = ET.Element('flow', id=flow_id, type=type_dist,
                          begin=str((hour - 6) * self.demand_profile.hour_len),
                          fromJunction=in_j, toJunction=out_j, end=str((hour - 5) * self.demand_profile.hour_len),
                          probability=f"{prob}", departSpeed=depart_speed)
        if depart_lane is not None:
            flow.set('departLane', str(depart_lane))
        flow.tail = '\n\t'
        root.append(flow)

    def _create_route_file(self):
        tree = ET.parse(self.route_template)
        root = tree.getroot()

        self._create_vType_dist(root)

        in_junc = "J0"
        out_junc = "J9"
        in_ramps = [f'i{i}' for i in range(1, self.ramps_num + 1)]
        out_ramps = [f'o{i}' for i in range(1, self.ramps_num + 1)]

        np.random.seed(self.seed)
        in_probs = np.random.uniform(0, 0.2, self.ramps_num)
        out_probs = np.random.uniform(0, 0.2, self.ramps_num)
        for hour, hour_demand in self.demand_profile.veh_amount.items():
            total_arrival_prob = hour_demand / 3600
            bus_veh_prop = self.demand_profile.bus_amount[hour] / hour_demand
            taken = 0
            for i, (in_ramp, in_prob) in enumerate(zip(in_ramps, in_probs)):
                left_in = 1
                # In ramps to Out ramps
                for j, (out_ramp, out_prob) in enumerate(zip(out_ramps, out_probs)):
                    if i > j:
                        continue
                    prob = in_prob * out_prob
                    left_in -= out_prob
                    flow_prob = total_arrival_prob * prob
                    if total_arrival_prob * self.demand_profile.hour_len > 1:
                        self._append_flow(root, hour, in_ramp, out_ramp, flow_prob)
                        if total_arrival_prob * bus_veh_prop > 0:
                            self._append_flow(root, hour, in_ramp, out_ramp, flow_prob * bus_veh_prop,
                                              type_dist="busDist")
                    else:
                        print(f'hour {hour} in_ramp {in_ramp} out_ramp {out_ramp} prob {flow_prob}')
                # In ramps to Out junction
                self._append_flow(root, hour, in_ramp, out_junc, total_arrival_prob * in_prob * left_in)
                if total_arrival_prob * in_prob * left_in * bus_veh_prop > 0:
                    self._append_flow(root, hour, in_ramp, out_junc,
                                      total_arrival_prob * in_prob * left_in * bus_veh_prop,
                                      type_dist="busDist")
            # In junction to Out ramps
            for out_ramp, out_prob in zip(out_ramps, out_probs):
                taken += out_prob
                for lane in range(self.lane_num):
                    flow_prob = total_arrival_prob * out_prob / self.lane_num
                    self._append_flow(root, hour, in_junc, out_ramp, flow_prob, depart_lane=lane)
                    if total_arrival_prob * bus_veh_prop > 0:
                        self._append_flow(root, hour, in_junc, out_ramp, flow_prob * bus_veh_prop,
                                          depart_lane=lane, type_dist="busDist")

            # In junction to Out junction
            in_out_prob = 1 - taken
            assert in_out_prob >= 0
            for lane in range(self.lane_num):
                flow_prob = total_arrival_prob * in_out_prob / self.lane_num
                self._append_flow(root, hour, in_junc, out_junc, flow_prob, depart_lane=lane)
                if total_arrival_prob * bus_veh_prop > 0:
                    self._append_flow(root, hour, in_junc, out_junc, flow_prob * bus_veh_prop,
                                      depart_lane=lane, type_dist="busDist")

        # Save the changes back to the file
        # os.makedirs(f"{ROOT}/rou_files_{EXP_NAME}/{demand}/{seed}", exist_ok=True)
        tree.write(self.route_file)
        # tree.write(f'{ROOT}/rou_files_{EXP_NAME}/{demand}/{seed}/{EXP_NAME}.rou.xml')

    def _create_config_file(self):
        # Load and parse the XML file
        tree = ET.parse(self.config_template)
        root = tree.getroot()

        # set route file
        route_file_pointer = root.find("input").find('route-files')
        route_file_pointer.set('value', self.route_file)

        # set net file
        net_file_pointer = root.find("input").find('net-file')
        net_file_pointer.set('value', self.network_file)

        # set seed
        seed_element_pointer = root.find("random_number").find('seed')
        seed_element_pointer.set('value', str(self.seed))

        tree.write(self.config_file)

    def _init_sumo(self, config_file, results_folder=None):
        sumo_binary = self._get_sumo_entrypoint()
        sumo_cmd = [sumo_binary, "-c", self.config_file]
        sumo_cmd += ["--tripinfo-output", self.output_file]
        print(sumo_cmd)
        traci.start(sumo_cmd)

    def _get_sumo_entrypoint(self):
        if 'SUMO_HOME' in os.environ:
            sumo_path = os.environ['SUMO_HOME']
            # check operational system - if it is windows, use sumo.exe if linux/macos, use sumo
            if os.name == 'nt':
                sumo_binary = os.path.join(sumo_path, 'bin', 'sumo-gui.exe') if self.gui else \
                    os.path.join(sumo_path, 'bin', 'sumo.exe')
            else:
                sumo_binary = os.path.join(sumo_path, 'bin', 'sumo-gui') if self.gui else \
                    os.path.join(sumo_path, 'bin', 'sumo')
        else:
            raise Exception("please declare environment variable 'SUMO_HOME'")
        return sumo_binary


if __name__ == '__main__':
    adapter_daily = SUMOAdapter(DailyDemand(), 42, 0.5, gui=True)
    adapter_daily.init_simulation("test.xml")
    adapter_daily.run_for_timesteps(65000)
