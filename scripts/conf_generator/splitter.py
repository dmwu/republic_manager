import json
import pprint


def gen_splitter(splitters_l):
    """

    :param radix: fanout of splitteres
    :param n_splitter: number of splitters at each fanout
    :param port: staring port on ocs
    :return: dictionary of splitters
    """

    ret = {}
    for rd in range(0, len(splitters_l)):
        sps = []
        port_offset = splitters_l[rd]["starting"]
        for ns in range(0, splitters_l[rd]["num"]):
            sp = {}
            sp["in"] = port_offset
            sp["out"] = []
            for o in range(0, splitters_l[rd]["fanout"]):
                sp["out"].append(port_offset)
                port_offset += 1
            sps.append(sp)

            # ret.append(
            #     {"ip": socket.inet_ntoa(struct.pack('!L', ip_long + ip_offset)),
            #      "tor": dpid + pr,
            #      "port": port + port_offset})
            # ip_offset += 1
            # port_offset += 1
        ret[splitters_l[rd]["fanout"]] = sps
    return ret


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    results = gen_splitter(radix=(2, 4, 8, 16, 32), n_splitter=(2, 2, 3, 4, 2), port=41)
    pp.pprint(results)

    with open('splitter.json', 'w') as outfile:
        json.dump(results, outfile, sort_keys=True, indent=2, ensure_ascii=False)
