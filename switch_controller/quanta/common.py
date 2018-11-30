import copy
import socket
import struct

from ofdpa.config_parser import ConfigParser
from ofdpa.mods import Mods


class RuleTempleate():
    def __init__(self, template_dir):
        self.config_group_l2_interface = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_group_l2_interface"))
        self.config_vlan_tagged = ConfigParser.get_config("%s/%s.json" % (template_dir, "template_vlan_tagged"))
        self.config_vlan_untagged = ConfigParser.get_config("%s/%s.json" % (template_dir, "template_vlan_untagged"))
        self.config_acl_unicast = ConfigParser.get_config("%s/%s.json" % (template_dir, "template_acl_unicast"))
        self.config_acl_unicast_low = ConfigParser.get_config("%s/%s.json" % (template_dir, "template_acl_unicast_low"))
        self.config_acl_unicast_low_wildcard = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_acl_unicast_low_wildcard"))
        self.config_acl_unicast_low_port = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_acl_unicast_low_port"))
        self.config_acl_arp = ConfigParser.get_config("%s/%s.json" % (template_dir, "template_acl_arp"))
        self.config_group_l2_multicast_arp = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_group_l2_multicast"))
        self.config_group_l2_multicast_arp_bucket = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_group_l2_multicast_bucket"))
        self.config_acl_arp_multicast = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_acl_arp_multicast"))
        self.config_acl_unicast_eth_port = ConfigParser.get_config(
            "%s/%s.json" % (template_dir, "template_acl_unicast_eth_port"))

    @staticmethod
    def install_group_mod(dp, config):
        for type_ in ConfigParser.get_config_type(config):
            if type_ == "group_mod":
                mod_config = ConfigParser.get_group_mod(config)
                mod = Mods.create_group_mod(dp, mod_config)
                dp.send_msg(mod)
                return mod
            else:
                raise Exception("Wrong type", type_)
        return None

    @staticmethod
    def install_flow_mod(dp, config):
        for type_ in ConfigParser.get_config_type(config):
            if type_ == "flow_mod":
                mod_config = ConfigParser.get_flow_mod(config)
                mod = Mods.create_flow_mod(dp, mod_config)
                dp.send_msg(mod)
                return mod
            else:
                raise Exception("Wrong type", type_)
        return None

    def create_acl_unicast_eth_port(self, dp, template, vlan, inport, port, eth, queue):
        acl_unicast_eth_port = copy.deepcopy(template)
        acl_unicast_eth_port['flow_mod']['_name'] += str(port)
        acl_unicast_eth_port['flow_mod']['match']['eth_type'] += eth
        acl_unicast_eth_port['flow_mod']['match']['in_port'] += str(inport)
        acl_unicast_eth_port['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast_eth_port['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(
            queue)
        acl_unicast_eth_port['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group'][
            'group_id'] += "%03x%04x" % (vlan, port)
        RuleTempleate.install_flow_mod(dp, acl_unicast_eth_port)
        return

    def create_group_l2_interface(self, dp, template, vlan, port):
        group_l2_interface = copy.deepcopy(template)
        group_l2_interface['group_mod']['_name'] += "%03x%04x" % (vlan, port)
        group_l2_interface['group_mod']['group_id'] += "%03x%04x" % (vlan, port)
        group_l2_interface['group_mod']['buckets'][0]['actions'][0]['output']['port'] += str(port)
        RuleTempleate.install_group_mod(dp, group_l2_interface)
        return

    def create_vlan(self, dp, template_tagged, template_untagged, vlan, port):
        vlan_tagged = copy.deepcopy(template_tagged)
        vlan_tagged['flow_mod']['_name'] += str(vlan) + "_" + str(port)
        vlan_tagged['flow_mod']['match']['in_port'] += str(port)
        vlan_tagged['flow_mod']['match']['vlan_vid'] += str(vlan)
        RuleTempleate.install_flow_mod(dp, vlan_tagged)

        vlan_untagged = copy.deepcopy(template_untagged)
        vlan_untagged['flow_mod']['_name'] += str(vlan) + "_" + str(port)
        vlan_untagged['flow_mod']['match']['in_port'] += str(port)
        vlan_untagged['flow_mod']['instructions'][0]['apply'][0]['actions'][0]['set_field']['vlan_vid'] += str(vlan)
        RuleTempleate.install_flow_mod(dp, vlan_untagged)
        return

    def create_acl_unicast(self, dp, template, vlan, ip, port, queue):
        acl_unicast = copy.deepcopy(template)
        acl_unicast['flow_mod']['_name'] += str(port)
        acl_unicast['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast['flow_mod']['match']['ipv4_dst'] += ip
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        RuleTempleate.install_flow_mod(dp, acl_unicast)
        return

    def create_acl_unicast_low(self, dp, template, in_port, vlan, ip, port, queue):
        acl_unicast_low = copy.deepcopy(template)
        acl_unicast_low['flow_mod']['_name'] += str(port)
        acl_unicast_low['flow_mod']['match']['in_port'] += str(in_port)
        acl_unicast_low['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast_low['flow_mod']['match']['ipv4_src'] += ip
        acl_unicast_low['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast_low['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        RuleTempleate.install_flow_mod(dp, acl_unicast_low)
        return

    def create_acl_unicast_low_wildcard(self, dp, template, vlan, port, queue):
        acl_unicast_low = copy.deepcopy(template)
        acl_unicast_low['flow_mod']['_name'] += str(port)
        acl_unicast_low['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast_low['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast_low['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        RuleTempleate.install_flow_mod(dp, acl_unicast_low)
        return

    def create_acl_unicast_low_port(self, dp, template, vlan, inport, port, queue):
        acl_unicast = copy.deepcopy(template)
        acl_unicast['flow_mod']['_name'] += str(port)
        acl_unicast['flow_mod']['match']['in_port'] += str(inport)
        acl_unicast['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        RuleTempleate.install_flow_mod(dp, acl_unicast)
        return

    def create_acl_arp(self, dp, template, in_port, vlan, port, queue):
        acl_arp = copy.deepcopy(template)
        acl_arp['flow_mod']['_name'] += str(port)
        acl_arp['flow_mod']['match']['in_port'] += str(in_port)
        acl_arp['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        RuleTempleate.install_flow_mod(dp, acl_arp)
        return

    def create_group_l2_flood(self, dp, template, template_bucket, vlan, ports, gid, gateway_port_ip=None):
        group_l2_multicast_arp = copy.deepcopy(template)
        group_l2_multicast_arp['group_mod']['_name'] += "%03x%04x" % (vlan, gid)
        group_l2_multicast_arp['group_mod']['group_id'] += "%03x%04x" % (vlan, gid)
        if gateway_port_ip is not None:
            for pi_ in gateway_port_ip:
                ports.append(pi_[0])
                # print ports
        for pp in ports:
            bucket = copy.deepcopy(template_bucket)
            bucket['actions'][0]['group']['group_id'] += "%03x%04x" % (vlan, pp)
            group_l2_multicast_arp['group_mod']['buckets'].append(bucket)
        RuleTempleate.install_group_mod(dp, group_l2_multicast_arp)
        return

    def create_acl_arp_flood(self, dp, template, vlan, queue, id):
        acl_arp = copy.deepcopy(template)
        acl_arp['flow_mod']['_name'] += str(vlan)
        acl_arp['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (vlan, id)
        RuleTempleate.install_flow_mod(dp, acl_arp)
        return

    def create_group_l2_multicast(self, dp, template, template_bucket, vlan, lr, n_server, ocs_port):
        for group_id in range(0, (2 ** n_server)):
            group_l2_multicast = copy.deepcopy(template)

            # group without ocs
            for port_offset in range(1, n_server + 1):
                if (group_id >> (port_offset - 1)) % 2 == 1:
                    bucket = copy.deepcopy(template_bucket)
                    bucket['actions'][0]['group']['group_id'] += "%03x%04x" % (vlan, port_offset + lr * n_server)
                    group_l2_multicast['group_mod']['buckets'].append(bucket)

            group_l2_multicast_ocs = copy.deepcopy(group_l2_multicast)
            group_l2_multicast['group_mod']['_name'] += "%03x%04x" % (vlan, group_id)
            group_l2_multicast['group_mod']['group_id'] += "%03x%04x" % (vlan, group_id)
            if group_id != 0:
                RuleTempleate.install_group_mod(dp, group_l2_multicast)

            # group with ocs
            bucket = copy.deepcopy(template_bucket)
            bucket['actions'][0]['group']['group_id'] += "%03x%04x" % (vlan, ocs_port)
            group_l2_multicast_ocs['group_mod']['buckets'].append(bucket)
            # TODO: add the multiple ocs links feature per lr here
            group_l2_multicast_ocs['group_mod']['_name'] += "%03x%04x" % (vlan, group_id + 2 ** (n_server))
            group_l2_multicast_ocs['group_mod']['group_id'] += "%03x%04x" % (vlan, group_id + 2 ** (n_server))
            RuleTempleate.install_group_mod(dp, group_l2_multicast_ocs)
        return


class SystemConfig():
    def __init__(self, cluster_conf, rate=10):
        # network config
        self.n_prack = cluster_conf['eps']['phy']['num']  # number of [physical ToRs]
        self.n_lrack = cluster_conf['eps']['log']['num_per_phy']  # number of [logical ToRs] on each [physical ToR]
        self.n_server = cluster_conf['node']['num_per_phy'] / self.n_lrack  # number of [servers] on each [logical ToR]
        self.over_subscription = cluster_conf['eps']['oversubscription']
        self.n_ocs = cluster_conf['eps']['duplex_%dG' % rate]['num_per_log']  # number of [ocs links] on each [logical ToR]
        assert (self.n_server % self.over_subscription) == 0

        # connectivity
        self.port = cluster_conf['node']['starting']  # starting port number on [each physical rack]
        self.port_ocs = cluster_conf['eps']['duplex_%dG' % rate][
            'starting']  # starting port (connecting to ocs) number on [each physical rack]
        self.lr_ = cluster_conf['eps']['log']['vlanid_starting']  # starting logical rack number in the [entire network]
        self.ip = cluster_conf['node']['starting_ip']  # staring ip address of [all servers]
        self.ip_10 = "[RESEARCH_NETWORK_PREFIX].111"
        self.port_core = 1  # starting port number on [core]

        # constants
        self.core_vlan = cluster_conf['core']['vlanid']  # vlan number of the core
        self.arp_flood_id = cluster_conf['apr_flood_groupid']  # group_id for the arp flood entry
        self.default_queue = cluster_conf['queue_priority']['default']  # default queue
        # high_queue = 4  # high priority queue
        self.gateway_port_ip = [(cluster_conf['gateway'][idx]['port'], cluster_conf['gateway'][idx]['ip'],
                                 cluster_conf['gateway'][idx]['ip_10']) for idx in
                                range(len(cluster_conf['gateway']))]

        self.ip_long = struct.unpack("!L", socket.inet_aton(self.ip))[0]
        self.ip_10_long = struct.unpack("!L", socket.inet_aton(self.ip_10))[0]


if __name__ == '__main__':
    pass
