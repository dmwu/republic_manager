def gen_relay(relays_eps_l, relays_ocs):
    ocs_starting = relays_ocs["starting"]
    ocs_offset = ocs_starting

    ret = []
    for rd in range(0, len(relays_eps_l)):
        for idx in range(relays_eps_l[rd]["num"]):
            sps = {}
            sps["dpid"] = relays_eps_l[rd]["dpid"]
            sps["eps_port"] = relays_eps_l[rd]["starting"] + idx
            sps["ocs_port"] = ocs_offset
            ocs_offset += 1
            ret.append(sps)

    return ret
