import json
import socket
import struct


def gen_server(n_server=4, n_lrack=2, n_prack=5, ip="[INTERNAL_NETWORK_PREFIX].30.101", port=1, lrid=1, dpid=55960):
    """

    :param n_server: number of servers per logical ToR
    :param n_lrack: number of logical ToRs per physical ToR
    :param n_prack: number of physical per logical ToRs
    :param ip: starting server ip
    :param port: starting port number on physical rack
    :param dpid: starting dpid
    :return: the dictionary of server connectivity
    """
    ret = []

    ip_long = struct.unpack("!L", socket.inet_aton(ip))[0]

    ip_offset = 0
    lr_offset = 0
    for pr in range(0, n_prack):
        port_offset = 0
        for lr in range(0, n_lrack):
            for ss in range(0, n_server):
                ret.append(
                    {"ip": socket.inet_ntoa(struct.pack('!L', ip_long + ip_offset)),
                     "tor_phy": dpid + pr,
                     "tor_log": lrid + lr_offset,
                     "port": port + port_offset,
                     "rack_idx": ss})
                ip_offset += 1
                port_offset += 1
            lr_offset += 1
    return ret


if __name__ == "__main__":
    # pp = pprint.PrettyPrinter(indent=2)
    results = gen_server(2, 4, 1, "[INTERNAL_NETWORK_PREFIX].40.51", 10, 55500)
    # pp.pprint(results)

    with open('server.json', 'w') as outfile:
        json.dump(results, outfile, sort_keys=True, indent=2, ensure_ascii=False)
