# *********************************************************************
#
# (C) Copyright Broadcom Corporation 2013-2014
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# *********************************************************************
# import ConfigParser
#   This is a script intended
#   to use by Ryu OpenFlow controller
#
import copy
import json
import logging
import pprint
import socket
import struct
from ryu.base import app_manager
from ryu.controller import dpset
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

from ofdpa.config_parser import ConfigParser
from ofdpa.mods import Mods

ryu_loggers = logging.Logger.manager.loggerDict


def ryu_loggers_on(on):
    for key in ryu_loggers.keys():
        ryu_logger = logging.getLogger(key)
        ryu_logger.propagate = on


LOG = logging.getLogger('ofdpa')

# LOG.setLevel(logging.DEBUG)
LOG.setLevel(logging.INFO)

fmt = logging.Formatter("[%(levelname)s]\t%(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(fmt)
# LOG.addHandler(ch)

fh = logging.FileHandler('./log_ofdpa_broadcast.log', 'w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
LOG.addHandler(fh)


class OfdpaTe(app_manager.RyuApp):
    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    CONFIG_FILE = './quanta/config/ofdpa_te.json'

    def __init__(self, *args, **kwargs):
        super(OfdpaTe, self).__init__(*args, **kwargs)
        # get the "dpid" of the controller
        # wsapi_port = self.CONF.get('wsapi_port')
        # ofp_tcp_listen_port = self.CONF.get('ofp_tcp_listen_port')
        # assert (wsapi_port % 10) == (ofp_tcp_listen_port % 10)
        # self.dpid = wsapi_port % 10

        # load configuration
        conf_dir = "../conf/"
        conf_filename = "cluster_conf.json"
        with open(conf_dir + conf_filename) as file:
            self.conf_dict = json.load(file)
        pprint.pprint(self.conf_dict)

        # output_path = "../../conf/"
        # config = cp.RawConfigParser()
        # config.read(output_path + './cluster_system.conf')

        # self.n_prack = config.getint("Quantity", "n_prack")  # number of physical rack
        # self.n_lrack = config.getint("Quantity", "n_lrack")  # number of logical rack on a physical rack
        # self.n_plink = config.getint("Quantity", "n_plink")  # number of physical link to core switch on a physical rack
        # self.n_llink = config.getint("Quantity", "n_llink")  # number of logical link to core switch on a logical rack
        # self.n_server = config.getint("Quantity", "n_server")  # number of server on a physical rack
        # assert (self.n_server % self.n_lrack == 0)
        # self.n_server /= self.n_lrack  # number of server on a logical rack
        #
        # self.starting_ip = str(config.get("Connectivity", "starting_ip"))  # starting ip of the servers
        # self.starting_dpid = config.getint("Connectivity", "starting_dpid")  # starting physical rack id
        # self.starting_tor = config.getint("Connectivity", "starting_tor")  # starting logical rack id
        # self.starting_port_server = config.getint("Connectivity", "starting_port_server")  # starting port on physical rack to the servers
        # self.starting_port_tx = config.getint("Connectivity", "starting_port_tx")  # strating port on physical rack to the ocs
        # self.over_subscription = config.getint("Connectivity", "over_subscription")

        # conf = OrderedDict()
        # conf["n_prack"] = self.n_prack
        # conf["n_lrack"] = self.n_lrack
        # conf["n_plink"] = self.n_plink
        # conf["n_llink"] = self.n_llink
        # conf["n_server"] = self.n_server
        # conf["starting_ip"] = self.starting_ip
        # conf["starting_dpid"] = self.starting_dpid
        # conf["starting_tor"] = self.starting_tor
        # conf["starting_port_server"] = self.starting_port_server
        # conf["starting_port_tx"] = self.starting_port_tx
        # for k, v in conf.iteritems():
        #     print k + ":\t", v

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        LOG.info("=============================================================")
        LOG.info("EventDP")
        LOG.info("Datapath Id: %i - 0x%x", ev.dp.id, ev.dp.id)
        LOG.info("Datapath Address: %s", ev.dp.address[0])
        LOG.info("=============================================================")
        if ev.enter:
            self.build_packets(ev.dp, ev.dp.id)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        LOG.info("=============================================================")
        LOG.info("Event PacketIn: %s", ev)
        LOG.info("=============================================================")

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

    def create_group_l2_interface(self, dp, template, vlan, port):
        group_l2_interface = copy.deepcopy(template)
        group_l2_interface['group_mod']['_name'] += "%03x%04x" % (vlan, port)
        group_l2_interface['group_mod']['group_id'] += "%03x%04x" % (vlan, port)
        group_l2_interface['group_mod']['buckets'][0]['actions'][0]['output']['port'] += str(port)
        self.install_group_mod(dp, group_l2_interface)
        return

    def create_vlan(self, dp, template_tagged, template_untagged, vlan, port):
        vlan_tagged = copy.deepcopy(template_tagged)
        vlan_tagged['flow_mod']['_name'] += str(vlan) + "_" + str(port)
        vlan_tagged['flow_mod']['match']['in_port'] += str(port)
        vlan_tagged['flow_mod']['match']['vlan_vid'] += str(vlan)
        self.install_flow_mod(dp, vlan_tagged)

        vlan_untagged = copy.deepcopy(template_untagged)
        vlan_untagged['flow_mod']['_name'] += str(vlan) + "_" + str(port)
        vlan_untagged['flow_mod']['match']['in_port'] += str(port)
        vlan_untagged['flow_mod']['instructions'][0]['apply'][0]['actions'][0]['set_field']['vlan_vid'] += str(vlan)
        self.install_flow_mod(dp, vlan_untagged)
        return

    def create_acl_unicast(self, dp, template, vlan, ip, port, queue):
        acl_unicast = copy.deepcopy(template)
        acl_unicast['flow_mod']['_name'] += str(port)
        acl_unicast['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast['flow_mod']['match']['ipv4_dst'] += ip
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        self.install_flow_mod(dp, acl_unicast)
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
        self.install_flow_mod(dp, acl_unicast_low)
        return

    def create_acl_unicast_low_wildcard(self, dp, template, vlan, port, queue):
        acl_unicast_low = copy.deepcopy(template)
        acl_unicast_low['flow_mod']['_name'] += str(port)
        acl_unicast_low['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast_low['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast_low['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        self.install_flow_mod(dp, acl_unicast_low)
        return

    def create_acl_unicast_low_port(self, dp, template, vlan, inport, port, queue):
        acl_unicast = copy.deepcopy(template)
        acl_unicast['flow_mod']['_name'] += str(port)
        acl_unicast['flow_mod']['match']['in_port'] += str(inport)
        acl_unicast['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        self.install_flow_mod(dp, acl_unicast)
        return

    def create_acl_arp(self, dp, template, in_port, vlan, port, queue):
        acl_arp = copy.deepcopy(template)
        acl_arp['flow_mod']['_name'] += str(port)
        acl_arp['flow_mod']['match']['in_port'] += str(in_port)
        acl_arp['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (
            vlan, port)
        self.install_flow_mod(dp, acl_arp)
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
        self.install_group_mod(dp, group_l2_multicast_arp)
        return

    def create_acl_arp_flood(self, dp, template, vlan, queue, id):
        acl_arp = copy.deepcopy(template)
        acl_arp['flow_mod']['_name'] += str(vlan)
        acl_arp['flow_mod']['match']['vlan_vid'] += str(vlan)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(queue)
        acl_arp['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%03x%04x" % (vlan, id)
        self.install_flow_mod(dp, acl_arp)
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
                self.install_group_mod(dp, group_l2_multicast)

            # group with ocs
            bucket = copy.deepcopy(template_bucket)
            bucket['actions'][0]['group']['group_id'] += "%03x%04x" % (vlan, ocs_port)
            group_l2_multicast_ocs['group_mod']['buckets'].append(bucket)
            # TODO: add the multiple ocs links feature per lr here
            group_l2_multicast_ocs['group_mod']['_name'] += "%03x%04x" % (vlan, group_id + 2 ** (n_server))
            group_l2_multicast_ocs['group_mod']['group_id'] += "%03x%04x" % (vlan, group_id + 2 ** (n_server))
            self.install_group_mod(dp, group_l2_multicast_ocs)
        return

    def build_packets(self, dp, dpid):
        config_dir, _ = ConfigParser.get_working_set(self.CONFIG_FILE)

        # network config
        n_prack = self.conf_dict['eps']['phy']['num']  # number of [physical ToRs]
        n_lrack = self.conf_dict['eps']['log']['num_per_phy']  # number of [logical ToRs] on each [physical ToR]
        n_server = self.conf_dict['node']['num_per_phy'] / n_lrack  # number of [servers] on each [logical ToR]
        over_subscription = self.conf_dict['eps']['oversubscription']
        n_ocs = self.conf_dict['eps']['duplex_10G']['num_per_log']  # number of [ocs links] on each [logical ToR]
        assert (n_server % over_subscription) == 0

        # connectivity
        port = self.conf_dict['node']['starting']  # starting port number on [each physical rack]
        port_ocs = self.conf_dict['eps']['duplex_10G'][
            'starting']  # starting port (connecting to ocs) number on [each physical rack]
        lr_ = self.conf_dict['eps']['log']['vlanid_starting']  # starting logical rack number in the [entire network]
        ip = self.conf_dict['node']['starting_ip']  # staring ip address of [all servers]
        ip_10 = "[RESEARCH_NETWORK_PREFIX].111"
        port_core = 1  # starting port number on [core]

        # constants
        core_vlan = self.conf_dict['core']['vlanid']  # vlan number of the core
        arp_flood_id = self.conf_dict['apr_flood_groupid']  # group_id for the arp flood entry
        default_queue = self.conf_dict['queue_priority']['default']  # default queue
        # high_queue = 4  # high priority queue
        gateway_port_ip = [(self.conf_dict['gateway'][idx]['port'], self.conf_dict['gateway'][idx]['ip'],
                            self.conf_dict['gateway'][idx]['ip_10']) for idx in
                           range(len(self.conf_dict['gateway']))]

        ip_long = struct.unpack("!L", socket.inet_aton(ip))[0]
        ip_10_long = struct.unpack("!L", socket.inet_aton(ip_10))[0]

        template_group_l2_interface_filename = "%s/%s.json" % (config_dir, "template_group_l2_interface")
        config = ConfigParser.get_config(template_group_l2_interface_filename)
        template_vlan_tagged_filename = "%s/%s.json" % (config_dir, "template_vlan_tagged")
        config_vlan_tagged = ConfigParser.get_config(template_vlan_tagged_filename)
        template_vlan_untagged_filename = "%s/%s.json" % (config_dir, "template_vlan_untagged")
        config_vlan_untagged = ConfigParser.get_config(template_vlan_untagged_filename)
        template_acl_unicast_filename = "%s/%s.json" % (config_dir, "template_acl_unicast")
        config_acl_unicast = ConfigParser.get_config(template_acl_unicast_filename)
        template_acl_unicast_low_filename = "%s/%s.json" % (config_dir, "template_acl_unicast_low")
        config_acl_unicast_low = ConfigParser.get_config(template_acl_unicast_low_filename)
        template_acl_unicast_low_wildcard_filename = "%s/%s.json" % (config_dir, "template_acl_unicast_low_wildcard")
        config_acl_unicast_low_wildcard = ConfigParser.get_config(template_acl_unicast_low_wildcard_filename)
        template_acl_unicast_low_port_filename = "%s/%s.json" % (config_dir, "template_acl_unicast_low_port")
        config_acl_unicast_low_port = ConfigParser.get_config(template_acl_unicast_low_port_filename)
        template_acl_arp_filename = "%s/%s.json" % (config_dir, "template_acl_arp")
        config_acl_arp = ConfigParser.get_config(template_acl_arp_filename)
        template_group_l2_multicast_arp_filename = "%s/%s.json" % (config_dir, "template_group_l2_multicast")
        config_group_l2_multicast_arp = ConfigParser.get_config(template_group_l2_multicast_arp_filename)
        template_group_l2_multicast_bucket_arp_filename = "%s/%s.json" % (
            config_dir, "template_group_l2_multicast_bucket")
        config_group_l2_multicast_arp_bucket = ConfigParser.get_config(template_group_l2_multicast_bucket_arp_filename)
        template_acl_arp_multicast_filename = "%s/%s.json" % (config_dir, "template_acl_arp_multicast")
        config_acl_arp_multicast = ConfigParser.get_config(template_acl_arp_multicast_filename)

        # GROUP & VLAN ENTRIES for all rules @ TORs
        if 0 < dpid <= 5:
            lr_offset_ = (dpid - 1) * n_lrack
            port_offset_ = 0
            ip_offset_ = (dpid - 1) * n_lrack * n_server
            LOG.info("TOR installation setup: " + "logical rack no (" + str(lr_offset_) + "), " + "core port no(" + str(
                port_offset_) + ")")

            for lr in range(0, n_lrack):  # lr'th logical ToR in physical ToR
                # rack info
                vlan_id = lr_ + lr_offset_

                # core port RULES (vlan, group)
                for cc in range(0, n_server / over_subscription):
                    core_port_id = cc + port_core + lr * n_server + n_lrack * n_server  # port # connecting to the core
                    # going to core
                    self.create_group_l2_interface(dp, config, vlan_id, core_port_id)
                    # vlan from core
                    self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, vlan_id, core_port_id)
                    print "core port |", "\tvlan #: ", vlan_id, "\tcore port #: ", core_port_id

                # server port RULES
                flood_server_port = []
                for ss in range(0, n_server):  # ss'th server in lr'th ToR
                    # server info
                    server_port_id = port + port_offset_
                    server_ip_addr = socket.inet_ntoa(struct.pack('!L', ip_long + ip_offset_))
                    server_ip_10_addr = socket.inet_ntoa(struct.pack('!L', ip_10_long + ip_offset_))
                    flood_server_port.append(server_port_id)

                    # core info
                    core_port_id = server_port_id + n_lrack * n_server - (
                        (server_port_id + n_lrack * n_server - port) % over_subscription)
                    print "server port | ", "\tvlan #: ", vlan_id, "\t", server_ip_addr, "\tserver port #: ", server_port_id, "\tcore port #: ", core_port_id
                    print "server port | ", "\tvlan #: ", vlan_id, "\t", server_ip_10_addr, "\tserver port #: ", server_port_id, "\tcore port #: ", core_port_id
                    # going to server
                    self.create_group_l2_interface(dp, config, vlan_id, server_port_id)
                    # vlan from server
                    self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, vlan_id, server_port_id)

                    # acl going to server
                    self.create_acl_unicast(dp, config_acl_unicast, vlan_id, server_ip_addr, server_port_id,
                                            default_queue)
                    self.create_acl_unicast(dp, config_acl_unicast, vlan_id, server_ip_10_addr, server_port_id,
                                            default_queue)
                    # acl going to core @ ToR
                    self.create_acl_unicast_low(dp, config_acl_unicast_low, server_port_id, vlan_id, server_ip_addr,
                                                core_port_id, default_queue)
                    self.create_acl_unicast_low(dp, config_acl_unicast_low, server_port_id, vlan_id, server_ip_10_addr,
                                                core_port_id, default_queue)

                    # arp going to core
                    self.create_acl_arp(dp, config_acl_arp, server_port_id, vlan_id, core_port_id, default_queue)
                    # arp going to servers
                    if over_subscription == 1:
                        self.create_acl_arp(dp, config_acl_arp, core_port_id, vlan_id, server_port_id, default_queue)

                    ip_offset_ += 1
                    port_offset_ += 1

                if over_subscription > 1:
                    print "arp | ", "\tvlan id: ", vlan_id, "\tports: ", flood_server_port, "\tgroup rule id: ", arp_flood_id + vlan_id
                    self.create_group_l2_flood(dp, config_group_l2_multicast_arp, config_group_l2_multicast_arp_bucket,
                                               vlan_id, flood_server_port, arp_flood_id + vlan_id)
                    self.create_acl_arp_flood(dp, config_acl_arp_multicast, vlan_id, default_queue,
                                              arp_flood_id + vlan_id)

                # ocs port rules (vlan, group)
                for ocs_ in range(0, n_ocs):
                    ocs_port_id = port_ocs + lr * n_ocs + ocs_
                    print "ocs | ", "\tswitch ocs port: ", ocs_port_id

                    # going to ocs from logical rack
                    self.create_group_l2_interface(dp, config, vlan_id, ocs_port_id)
                    # vlan from ocs
                    self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, vlan_id, ocs_port_id)
                    # group for multicasting to OCS and ToR @ ToR
                    self.create_group_l2_multicast(dp, config_group_l2_multicast_arp,
                                                   config_group_l2_multicast_arp_bucket, vlan_id, lr, n_server,
                                                   ocs_port_id)
                lr_offset_ += 1

        # GROUP & VLAN ENTRIES for all rules @ Core
        elif dpid == 0:
            ip_offset_ = 0
            # core port RULES (vlan, group)
            for cc in range(0, n_prack * n_lrack * n_server / over_subscription):
                core_port_id = over_subscription * cc + 1
                # going to core
                self.create_group_l2_interface(dp, config, core_vlan, core_port_id)
                # vlan from core
                self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, core_vlan, core_port_id)
                print "core port vlan/group |", "\tvlan #: ", core_vlan, "\tcore port #: ", core_port_id

            for pc_ in range(0, n_prack * n_lrack * n_server):  # loop through all the core ports
                core_port_ = port_core + pc_ - (
                    (port_core + pc_ - port_core) % over_subscription)  # physical port number
                # [group] going out of core
                # self.create_group_l2_interface(dp, config, core_vlan, core_port_)
                # [vlan] coming to the core
                # self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, core_vlan, core_port_)

                print "core | ", "\tvlan: ", core_vlan, "\tcore port #: ", core_port_, "\t", socket.inet_ntoa(
                    struct.pack('!L', ip_long + ip_offset_))
                print "core | ", "\tvlan: ", core_vlan, "\tcore port #: ", core_port_, "\t", socket.inet_ntoa(
                    struct.pack('!L', ip_10_long + ip_offset_))
                # [acl] unicast going out of core to ToRs
                self.create_acl_unicast(dp, config_acl_unicast, core_vlan,
                                        socket.inet_ntoa(struct.pack('!L', ip_long + ip_offset_)), core_port_,
                                        default_queue)
                self.create_acl_unicast(dp, config_acl_unicast, core_vlan,
                                        socket.inet_ntoa(struct.pack('!L', ip_10_long + ip_offset_)), core_port_,
                                        default_queue)
                ip_offset_ += 1

            # set update the rule for the gateway
            for pi_ in gateway_port_ip:
                # [group]
                self.create_group_l2_interface(dp, config, core_vlan, pi_[0])
                # [vlan]
                self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, core_vlan, pi_[0])

                print "core gateway | ", "\tvlan: ", core_vlan, "\tcore port #: ", pi_[0], "\t", pi_[1]
                # [acl]
                self.create_acl_unicast(dp, config_acl_unicast, core_vlan, pi_[1], pi_[0], default_queue)
                self.create_acl_unicast(dp, config_acl_unicast, core_vlan, pi_[2], pi_[0], default_queue)

            print "default rule: ", "\tport: ", gateway_port_ip[1][0]
            self.create_acl_unicast_low_wildcard(dp, config_acl_unicast_low_wildcard, core_vlan, gateway_port_ip[1][0],
                                                 default_queue)

            # [group] rule flood arp packets @ core
            core_port_list = list(range(port_core + 0, port_core + n_prack * n_lrack * n_server))[0::over_subscription]
            for a in gateway_port_ip:
                core_port_list.append(a[0])
            print "core arp: ", "\t", core_port_list
            self.create_group_l2_flood(dp, config_group_l2_multicast_arp, config_group_l2_multicast_arp_bucket,
                                       core_vlan, core_port_list, arp_flood_id, gateway_port_ip=gateway_port_ip)
            # [acl] rule flood arp packets @ core
            self.create_acl_arp_flood(dp, config_acl_arp_multicast, core_vlan, default_queue, arp_flood_id)

        else:
            pass

        if 'relay' in self.conf_dict['eps']:
            for r_d in self.conf_dict['eps']['relay']:
                if r_d['dpid'] == dpid:
                    print "install relay on dpid %d" % dpid
                    for relay_port in range(r_d['starting'], r_d['starting'] + r_d['num']):
                        # [group]
                        self.create_group_l2_interface(dp, config, r_d['vlanid'], relay_port)
                        # [vlan]
                        self.create_vlan(dp, config_vlan_tagged, config_vlan_untagged, r_d['vlanid'], relay_port)
                        print 'relay |\tvlan: %d, port: %d' % (r_d['vlanid'], relay_port)
                        self.create_acl_unicast_low_port(dp, config_acl_unicast_low_port, r_d['vlanid'], relay_port,
                                                         relay_port, default_queue)

        return


if __name__ == '__main__':
    pass
