import json
from pprint import pprint

from conf_generator.feeder import gen_feeder
from conf_generator.relay import gen_relay
from conf_generator.server import gen_server
from conf_generator.splitter import gen_splitter
from conf_generator.switch import gen_switch

if __name__ == "__main__":
    # splitter_radix = (2, 4, 8, 16, 32)
    # splitter_number = (0, 16, 0, 0, 0)

    # output_path = "../conf/"
    # config = ConfigParser.RawConfigParser()
    # config.read(output_path + './cluster_system.conf')

    conf_dir = "../conf/"
    output_dir = "../conf/"
    conf_filename = "cluster_conf.json"
    with open(conf_dir + conf_filename) as file:
        conf_dict = json.load(file)
    pprint(conf_dict)

    n_prack = conf_dict['eps']['phy']['num']
    n_lrack = conf_dict['eps']['log']['num_per_phy']
    n_plink = conf_dict['eps']['duplex_10G']['num']
    n_llink = conf_dict['eps']['duplex_10G']['num_per_log']
    n_server = conf_dict['node']['num_per_phy']
    assert (n_server % n_lrack == 0)
    n_server /= n_lrack  # number of servers on a logical tor

    starting_ip = conf_dict['node']['starting_ip']
    starting_dpid = conf_dict['eps']['phy']['dpid_starting']
    starting_tor = conf_dict['eps']['log']['vlanid_starting']
    starting_port_server = conf_dict['node']['starting']
    starting_port_ocs = conf_dict['ocs']['duplex_10G']['starting']
    starting_port_tx = conf_dict['eps']['duplex_10G']['starting']

    # n_helper = config.getint("Quantity", "n_helper")
    # starting_port_splitter = config.getint("Connectivity", "starting_port_splitter")
    # starting_helper_ocs = config.getint("Connectivity", "starting_helper_ocs")

    # n_prack = config.getint("Quantity", "n_prack")
    # n_lrack = config.getint("Quantity", "n_lrack")
    # n_plink = config.getint("Quantity", "n_plink")
    # n_llink = config.getint("Quantity", "n_llink")
    # n_server = config.getint("Quantity", "n_server")  # number of servers on a physical tor
    # n_helper = config.getint("Quantity", "n_helper")
    # assert (n_server % n_lrack == 0)
    # n_server /= n_lrack  # number of servers on a logical tor
    #
    # starting_helper_ocs = config.getint("Connectivity", "starting_helper_ocs")
    # starting_ip = str(config.get("Connectivity", "starting_ip"))
    # starting_dpid = config.getint("Connectivity", "starting_dpid")
    # starting_tor = config.getint("Connectivity", "starting_tor")
    # starting_port_server = config.getint("Connectivity", "starting_port_server")
    # starting_port_splitter = config.getint("Connectivity", "starting_port_splitter")
    # starting_port_ocs = config.getint("Connectivity", "starting_port_ocs")
    # starting_port_tx = config.getint("Connectivity", "starting_port_tx")

    # conf = OrderedDict()
    # conf["n_prack"] = n_prack
    # conf["n_lrack"] = n_lrack
    # conf["n_plink"] = n_plink
    # conf["n_llink"] = n_llink
    # conf["n_server"] = n_server
    # conf["n_helper"] = n_helper
    # conf["splitter_radix"] = splitter_radix
    # conf["splitter_number"] = splitter_number
    # conf["starting_helper_ocs"] = starting_helper_ocs
    # conf["starting_ip"] = starting_ip
    # conf["starting_dpid"] = starting_dpid
    # conf["starting_tor"] = starting_tor
    # conf["starting_port_server"] = starting_port_server
    # conf["starting_port_splitter"] = starting_port_splitter
    # conf["starting_port_ocs"] = starting_port_ocs
    # conf["starting_port_tx"] = starting_port_tx
    #
    # for k, v in conf.iteritems():
    #     print k + ":\t", v

    servers = gen_server(n_server=n_server, n_lrack=n_lrack, n_prack=n_prack, ip=starting_ip, port=starting_port_server, lrid=starting_tor, dpid=starting_dpid)
    switches = gen_switch(n_lrack=n_lrack, n_prack=n_prack, n_plink=n_plink, n_llink=n_llink, p_port=starting_port_tx, c_port=starting_port_ocs, lrid=starting_tor, dpid=starting_dpid)
    splitters = gen_splitter(conf_dict["ocs"]["splitters"])
    feeders = gen_feeder(conf_dict["ocs"]["feeders"])
    relays = gen_relay(conf_dict["eps"]["relay"], conf_dict["ocs"]["relay"])

    with open(output_dir + 'server.json', 'w') as outfile:
        json.dump(servers, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open(output_dir + 'switch.json', 'w') as outfile:
        json.dump(switches, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open(output_dir + 'splitter.json', 'w') as outfile:
        json.dump(splitters, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open(output_dir + 'feeder.json', 'w') as outfile:
        json.dump(feeders, outfile, sort_keys=True, indent=2, ensure_ascii=False)
    with open(output_dir + 'relay.json', 'w') as outfile:
        json.dump(relays, outfile, sort_keys=True, indent=2, ensure_ascii=False)
