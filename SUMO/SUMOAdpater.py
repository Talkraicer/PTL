import traci
import numpy as np
import os
from xml.etree import ElementTree as ET
from SUMO.demand_profiles import *
from SUMO.netfile_utils import *
import shutil
class SUMOAdapter:
    def __init__(self, demand_profile: Demand, seed: int, av_rate: float,
                 route_temp: str = "route_template.rou.xml", net_file: str = "network.net.xml",
                 cfg_temp: str = "config_template.sumocfg", add_temp: str = "additional_template.add.xml",
                 template_folder="SUMOconfig", output_folder="outputs", gui=False):
        curdir = os.path.dirname(os.path.abspath(__file__))
        self.template_folder = os.path.join(curdir, template_folder)

        self.av_rate = av_rate
        self.seed = seed

        self.network_file = os.path.join(self.template_folder, net_file)
        # Parsing the net file:
        self.lane_num = get_first_edge_lanenum(self.network_file)
        self.ramps_num = get_num_ramps(self.network_file)
        self.route_template = os.path.join(self.template_folder, route_temp)
        self.config_template = os.path.join(self.template_folder, cfg_temp)
        self.additional_template = os.path.join(self.template_folder, add_temp)
        self.gui = gui
        self.demand_profile = demand_profile
        net_name = net_file.split(".")[0]

        self.config_folder = os.path.join(self.template_folder, net_name)
        os.makedirs(self.config_folder, exist_ok=True)
        self.output_folder = os.path.join(curdir, output_folder, net_name, demand_profile.__str__(), str(av_rate), str(seed))
        os.makedirs(self.output_folder, exist_ok=True)

        # put a copy of the network file in the output folder
        shutil.copyfile(self.network_file, os.path.join(curdir, output_folder, net_name, net_file))


    def allow_vehicles(self, edge: str = "all", veh_types=None, min_num_pass=0):
        if veh_types is None:
            veh_types = ["AV", "HD"]

        veh_ids = traci.vehicle.getIDList() if edge == "all" else traci.edge.getLastStepVehicleIDs(edge)

        for veh_id in veh_ids:
            veh_type = traci.vehicle.getTypeID(veh_id)
            num_pass = int(veh_type.split("_")[1][0])
            if veh_type.startswith("Bus"):
                continue
            if veh_type not in veh_types:
                continue
            if num_pass >= min_num_pass:
                traci.vehicle.setVehicleClass(veh_id, "private")




    def get_state_dict(self, t):
        state_dict = {"t": t}
        PTL_lane_ids = get_PTL_lanes(self.network_file)
        state_dict["veh_ids_in_PTL"] = [veh_id for lane in PTL_lane_ids for veh_id in
                                        traci.lane.getLastStepVehicleIDs(lane)]
        state_dict["num_vehs_in_PTL"] = len(state_dict["veh_ids_in_PTL"])
        state_dict["num_total_vehs"] = len(traci.vehicle.getIDList())
        # get mean vehicles speed
        state_dict["mean_speed"] = np.mean([traci.vehicle.getSpeed(vehID) for vehID in traci.vehicle.getIDList()]) \
            if state_dict["num_total_vehs"] > 0 else 0
        state_dict["mean_speed_in_PTL"] = np.mean(
            [traci.vehicle.getSpeed(vehID) for vehID in state_dict["veh_ids_in_PTL"]]) \
            if state_dict["num_vehs_in_PTL"] > 0 else 0

        return state_dict

    def step(self, t):
        traci.simulationStep(t)

    def isFinish(self):
        return traci.simulation.getMinExpectedNumber() <= 0

    def close(self):
        traci.close()

    def init_simulation(self, policy):
        self.policy_name = policy.__str__()
        exp_config_folder = os.path.join(self.config_folder, self.demand_profile.__str__(), str(self.seed),
                                     self.policy_name)
        os.makedirs(exp_config_folder, exist_ok=True)
        self.route_file = os.path.join(exp_config_folder, f"av_{self.av_rate}.rou.xml")
        self.config_file = os.path.join(exp_config_folder, f"av_{self.av_rate}.sumocfg")
        self.additional_file = os.path.join(exp_config_folder, f"av_{self.av_rate}.add.xml")

        if self.demand_profile.toy:
            self._create_toy_rou_file(policy.min_num_pass, policy.veh_kinds)
        else:
            self._create_route_file(policy.veh_kinds, policy.min_num_pass, policy.endToEnd)
        self._create_additional_file()
        self._create_config_file()
        self._init_sumo()

    def _create_additional_file(self, period=60):
        tree = ET.parse(self.additional_template)
        root = tree.getroot()
        root.text = '\n\t'

        # create lanes tracker
        lanes_path = os.path.join(self.output_folder, f"{self.policy_name}_lanes.xml")
        elem = ET.Element("laneData", id="lane_data", freq=str(period), file=lanes_path)
        elem.tail = '\n\t'
        root.append(elem)

        tree.write(self.additional_file)

    def _create_vType_dist(self, root, veh_kinds, min_num_pass, endToEnd=False):
        if veh_kinds is None:
            veh_kinds = []
        if min_num_pass is None:
            min_num_pass = 6
        # Set vTypeDistribution to contain the probabilities of each vehicle type and the number of passengers
        av_prob = self.av_rate
        hdv_prob = 1 - av_prob
        for vTypeDist in root.findall('vTypeDistribution'):
            vTypeDist.text += '\t'
            if vTypeDist.attrib['id'].startswith('vehicleDist'):
                for k, v in self.demand_profile.prob_pass_hd.items():
                    prob = round(hdv_prob * v, 5)
                    if prob == 0:
                        continue
                    veh_class = "private" if int(k) >= min_num_pass and "HD" in veh_kinds else 'passenger'
                    type_id = f"HD_{k}" if vTypeDist.attrib['id'] == 'vehicleDist' else f"HD_{k}_endToEnd"
                    elem = ET.Element('vType', id=type_id, color='red', probability=str(prob), vClass=veh_class)
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)
                for k, v in self.demand_profile.prob_pass_av.items():
                    prob = round(av_prob * v, 5)
                    if prob == 0:
                        continue
                    if vTypeDist.attrib['id'] == 'vehicleDist':
                        veh_class = "private" if int(
                            k) >= min_num_pass and "AV" in veh_kinds and not endToEnd else 'evehicle'
                        type_id = f"AV_{k}"
                    else:
                        veh_class = "private" if int(k) >= min_num_pass and "AV" in veh_kinds else 'evehicle'
                        type_id = f"AV_{k}_endToEnd"
                    elem = ET.Element('vType', id=type_id, color='blue', probability=str(prob), vClass=veh_class)
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)

            elif vTypeDist.attrib['id'] == 'busDist':
                for k, v in self.demand_profile.prob_pass_bus.items():
                    if v == 0:
                        continue
                    elem = ET.Element('vType', id=f'Bus_{k}', probability=str(v), vClass='bus')
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)

    def _append_flow(self, root, hour, in_j, out_j, prob, type_dist="vehicleDist", depart_lane=None, poisson = False):

        flow_id = f'flow_{type_dist}_{hour}_{in_j}_{out_j}' if depart_lane is None else f'flow_{type_dist}_{hour}_{in_j}_{out_j}_{depart_lane}'
        flow = ET.Element('flow', id=flow_id, type=type_dist,
                          begin=str((hour - 6) * self.demand_profile.hour_len),
                          fromJunction=in_j, toJunction=out_j, end=str((hour - 5) * self.demand_profile.hour_len),
                          departSpeed=self.demand_profile.enter_speed)
        if poisson:
            flow.set("period", f"exp({prob})")
        else:
            flow.set('probability', str(prob))
        if depart_lane is not None:
            flow.set('departLane', str(depart_lane))
        flow.tail = '\n\t'
        root.append(flow)

    def _create_route_file(self, veh_kinds=None, min_num_pass=None, endToEnd=False):
        tree = ET.parse(self.route_template)
        root = tree.getroot()

        self._create_vType_dist(root, veh_kinds, min_num_pass, endToEnd)

        in_junc = get_first_junction(self.network_file)
        out_junc = get_last_junction(self.network_file)
        in_ramps = [f'i{i}' for i in range(1, self.ramps_num + 1)]
        out_ramps = [f'o{i}' for i in range(1, self.ramps_num + 1)]

        np.random.seed(self.seed)
        in_probs = np.random.uniform(0, 0.2, self.ramps_num)
        out_probs = np.random.uniform(0, 0.2, self.ramps_num)
        for hour, hour_demand in self.demand_profile.veh_amount.items():
            if hour_demand == 0:
                continue
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
                self._append_flow(root, hour, in_junc, out_junc, flow_prob, depart_lane=lane,
                                  type_dist="vehicleDist_endToEnd")

                if total_arrival_prob * bus_veh_prop > 0:
                    self._append_flow(root, hour, in_junc, out_junc, flow_prob * bus_veh_prop,
                                      depart_lane=lane, type_dist="busDist")

        # Save the changes back to the file
        # os.makedirs(f"{ROOT}/rou_files_{EXP_NAME}/{demand}/{seed}", exist_ok=True)
        tree.write(self.route_file)
        # tree.write(f'{ROOT}/rou_files_{EXP_NAME}/{demand}/{seed}/{EXP_NAME}.rou.xml')

    def _create_toy_vType_dist(self, root, ptl_dist, non_ptl_dist):
        # Set vTypeDistribution to contain the probabilities of each vehicle type and the number of passengers
        for vTypeDist in root.findall('vTypeDistribution'):
            vTypeDist.text += '\t'
            if vTypeDist.attrib['id'].startswith('PTLDist'):
                if sum(ptl_dist.values()) == 0:
                    root.remove(vTypeDist)
                    continue
                for veh_type, prob in ptl_dist.items():
                    if prob == 0:
                        continue
                    veh_class = "private"
                    elem = ET.Element('vType', id=veh_type, color='blue', probability=str(prob), vClass=veh_class)
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)
            elif vTypeDist.attrib['id'].startswith('NOPTLDist'):
                if sum(non_ptl_dist.values()) == 0:
                    root.remove(vTypeDist)
                    continue
                for veh_type, prob in non_ptl_dist.items():
                    if prob == 0:
                        continue
                    veh_class = "passenger"
                    elem = ET.Element('vType', id=veh_type, color='red', probability=str(prob), vClass=veh_class)
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)

            elif vTypeDist.attrib['id'] == 'busDist':
                for k, v in self.demand_profile.prob_pass_bus.items():
                    if v == 0:
                        continue
                    elem = ET.Element('vType', id=f'Bus_{k}', probability=str(v), vClass='bus')
                    elem.tail = '\n\t\t'
                    vTypeDist.append(elem)

    def _create_toy_rou_file(self, min_num_pass=None, veh_kinds = None):
        self.route_template = self.route_template.replace("route_template", "toy_route_template")
        tree = ET.parse(self.route_template)
        root = tree.getroot()

        # get the ptl and non-ptl lanes
        in_lanes = get_first_edge_lanes(self.network_file)
        in_ptl_lane_indices = [l.getIndex() for l in in_lanes if is_PTL_Lane(l)]
        not_ptl_lanes_indices = [l.getIndex() for l in in_lanes if not is_PTL_Lane(l)]

        if min_num_pass is None:
            min_num_pass = 6

        # handle the vehicle distribution
        hdv_prop = 1 - self.av_rate
        total_dist = {
            f"HD_{k}": v*hdv_prop for k, v in self.demand_profile.prob_pass_hd.items()
        }
        total_dist.update({
            f"AV_{k}": v*self.av_rate for k, v in self.demand_profile.prob_pass_av.items()
        })

        ptl_dist = {k: v for k, v in total_dist.items()
                    if int(k.split("_")[1]) >= min_num_pass
                    and k.split("_")[0] in veh_kinds}
        ptl_prop = sum(ptl_dist.values())
        non_ptl_dist = {k: v for k, v in total_dist.items()
                        if k not in ptl_dist}
        non_ptl_prop = sum(non_ptl_dist.values())

        ptl_dist = normalize_dict(ptl_dist)
        non_ptl_dist = normalize_dict(non_ptl_dist)

        self._create_toy_vType_dist(root, ptl_dist, non_ptl_dist)

        in_junc = get_first_junction(self.network_file)
        out_junc = get_last_junction(self.network_file)

        for hour, hour_demand in self.demand_profile.veh_amount.items():
            if hour_demand == 0:
                continue
            total_arrival_prob = hour_demand / 3600
            bus_veh_prop = self.demand_profile.bus_amount[hour] / hour_demand

            for lane in in_ptl_lane_indices:
                flow_prob = total_arrival_prob * ptl_prop / len(in_ptl_lane_indices)
                if flow_prob > 0:
                    self._append_flow(root, hour, in_junc, out_junc, flow_prob, depart_lane=lane,
                                      type_dist="PTLDist", poisson=True)
                if total_arrival_prob * bus_veh_prop > 0:
                    self._append_flow(root, hour, in_junc, out_junc, total_arrival_prob * bus_veh_prop/ len(in_ptl_lane_indices),
                                      depart_lane=lane, type_dist="busDist")
            if total_arrival_prob * non_ptl_prop > 0:
                for lane in not_ptl_lanes_indices:
                    flow_prob = total_arrival_prob * non_ptl_prop / len(not_ptl_lanes_indices)
                    self._append_flow(root, hour, in_junc, out_junc, flow_prob, depart_lane=lane,
                                      type_dist="NOPTLDist", poisson=True)
        # Save the changes back to the file
        tree.write(self.route_file)

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

        # set additional file
        additional_file_pointer = root.find("input").find('additional-files')
        additional_file_pointer.set('value', self.additional_file)

        # set tripinfo file
        tripinfo_file_pointer = root.find("output").find('tripinfo-output')
        tripinfo_output_path = os.path.join(self.output_folder, self.policy_name + "_tripinfo.xml")
        tripinfo_file_pointer.set('value', tripinfo_output_path)

        # set seed
        seed_element_pointer = root.find("random_number").find('seed')
        seed_element_pointer.set('value', str(self.seed))

        tree.write(self.config_file)

    def _init_sumo(self):
        sumo_binary = self._get_sumo_entrypoint()
        sumo_cmd = [sumo_binary, "-c", self.config_file]
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
    adapter_daily = SUMOAdapter(DemandToy1000(), 42, 0, net_file="network_toy.net.xml")
