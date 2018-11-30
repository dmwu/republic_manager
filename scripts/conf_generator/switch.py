import json
import pprint


def gen_switch(n_lrack=2, n_prack=5, n_plink=8, n_llink=2, p_port=24, c_port=11, lrid=1, dpid=55960):
    """

    :param n_lrack: number of logical racks
    :param n_prack: number of physical racks
    :param n_plink: number of physical ocs links per physical rack
    :param n_llink: number of physical ocs links per logical rack
    :param p_port: starting port on tor
    :param c_port: starting port on ocs
    :param dpid: starting dpid
    :return: dictionary of switch
    """
    ret = []
    assert n_plink >= n_llink * n_lrack
    lr_offset = 0
    c_port_offset = 0

    for pr in range(0, n_prack):
        p_port_offset = 0
        for lr in range(0, n_lrack):
            for llr in range(0, n_llink):
                ret.append(
                    {"tor_phy": dpid + pr,
                     "tor_log": lrid + lr_offset,
                     "port_tor": p_port + p_port_offset,
                     "port_ocs": c_port + c_port_offset + lr * n_llink + llr})
                p_port_offset += 1
            lr_offset += 1
        c_port_offset += n_plink
    return ret


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    results = gen_switch(3, 4, 20, 60, 55900)
    pp.pprint(results)

    with open('switch.json', 'w') as outfile:
        json.dump(results, outfile, sort_keys=True, indent=2, ensure_ascii=False)
