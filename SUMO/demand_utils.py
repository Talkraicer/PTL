from xml.etree import ElementTree as ET
def create_vType_dist(root, veh_kinds, min_num_pass, av_rate, demand_profile, endToEnd=False):
    if veh_kinds is None:
        veh_kinds = []
    if min_num_pass is None:
        min_num_pass = 6
    # Set vTypeDistribution to contain the probabilities of each vehicle type and the number of passengers
    av_prob = av_rate
    hdv_prob = 1 - av_prob
    for vTypeDist in root.findall('vTypeDistribution'):
        vTypeDist.text += '\t'
        if vTypeDist.attrib['id'].startswith('vehicleDist'):
            for k, v in demand_profile.prob_pass_hd.items():
                prob = round(hdv_prob * v, 5)
                if prob == 0:
                    continue
                veh_class = "private" if int(k) >= min_num_pass and "HD" in veh_kinds else 'passenger'
                type_id = f"HD_{k}" if vTypeDist.attrib['id'] == 'vehicleDist' else f"HD_{k}_endToEnd"
                elem = ET.Element('vType', id=type_id, color='red', probability=str(prob), vClass=veh_class)
                elem.tail = '\n\t\t'
                vTypeDist.append(elem)
            for k, v in demand_profile.prob_pass_av.items():
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
            for k, v in demand_profile.prob_pass_bus.items():
                if v == 0:
                    continue
                elem = ET.Element('vType', id=f'Bus_{k}', probability=str(v), vClass='bus')
                elem.tail = '\n\t\t'
                vTypeDist.append(elem)