import sumolib


def get_first_junction(network_file):
    # retrive using sumolib the leftmost junction
    net = sumolib.net.readNet(network_file)
    junctions = net.getNodes()
    junctions = sorted(junctions, key=lambda x: x.getShape()[0][0])
    return junctions[0].getID()


def get_last_junction(network_file):
    # retrive using sumolib the rightmost junction
    net = sumolib.net.readNet(network_file)
    junctions = net.getNodes()
    junctions = sorted(junctions, key=lambda x: x.getShape()[0][0])
    return junctions[-1].getID()


def get_first_edge_lanenum(network_file):
    # retrive using sumolib the leftmost edge and return its number of lanes
    net = sumolib.net.readNet(network_file)
    edges = net.getEdges()
    edges = sorted(edges, key=lambda x: x.getShape()[0][0])
    return edges[0].getLaneNumber()


def get_num_ramps(network_file):
    # retrive using sumolib the number of ramps - ramps are junctions starting with 'i'
    net = sumolib.net.readNet(network_file)
    edges = net.getEdges()
    return len([e for e in edges if e.getID().startswith('Ei')])

def get_PTL_lanes(network_file):
    # retrive using sumolib the number of ramps - ramps are junctions starting with 'i'
    net = sumolib.net.readNet(network_file)
    edges = net.getEdges()
    lanes_list = [l for e in edges for l in e.getLanes()]
    return [l.getID() for l in lanes_list if l.allows("passenger") == False]

if __name__ == '__main__':
    network_file = "SUMOconfig/network_crowded.net.xml"
    print(get_first_junction(network_file))
    print(get_last_junction(network_file))
    print(get_first_edge_lanenum(network_file))
    print(get_num_ramps(network_file))
    print(get_PTL_lanes(network_file))