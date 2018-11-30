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
# import logging
import sys

sys.path.insert(0, '/home/[SERVER_USERNAME]/github/republic_manager/')
import socket
import struct

from ryu.base import app_manager
from ryu.controller import dpset
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from switch_controller.quanta.common import SystemConfig, RuleTempleate
from switch_controller.quanta.ofdpa.config_parser import ConfigParser
from switch_controller.switch_measurement.common import load_switch_measurement_config


# from ofdpa.config_parser import ConfigParser
# from ofdpa.mods import Mods


# ryu_loggers = logging.Logger.manager.loggerDict
#
#
# def ryu_loggers_on(on):
#     for key in ryu_loggers.keys():
#         ryu_logger = logging.getLogger(key)
#         ryu_logger.propagate = on
#
#
# LOG = logging.getLogger('ofdpa')
#
# # LOG.setLevel(logging.DEBUG)
# LOG.setLevel(logging.INFO)
#
# fmt = logging.Formatter("[%(levelname)s]\t%(message)s")
#
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# ch.setFormatter(fmt)
#
# fh = logging.FileHandler('./log_ofdpa_broadcast.log', 'w')
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(fmt)
# LOG.addHandler(fh)



class OfdpaTe(app_manager.RyuApp):
    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # CONFIG_FILE = 'config/ofdpa_te.json'

    def __init__(self, *args, **kwargs):
        super(OfdpaTe, self).__init__(*args, **kwargs)

        # load controller argument
        CONF = load_switch_measurement_config()
        self.sender = CONF.sender
        self.receiver = CONF.receiver
        self.cluster_configuration = CONF.cluster_configuration
        self.rule_template_directory = CONF.rule_template_directory
        self.transceiver_speed = CONF.transceiver_speed

        self.sys_conf = ConfigParser.get_config(self.cluster_configuration)
        # pprint.pprint(sys_conf)
        self.cs = SystemConfig(self.sys_conf, self.transceiver_speed)
        self.rt = RuleTempleate(self.rule_template_directory)

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        # LOG.info("=============================================================")
        # LOG.info("EventDP")
        # LOG.info("Datapath Id: %i - 0x%x", ev.dp.id, ev.dp.id)
        # LOG.info("Datapath Address: %s", ev.dp.address[0])
        # LOG.info("=============================================================")
        if ev.enter:
            self.install_static_rules(ev.dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def handler_packet_in(self, ev):
        # LOG.info("=============================================================")
        # LOG.info("EventOFPPacketIn")
        # LOG.info("Datapath Id: %i - 0x%x", ev.dp.id, ev.dp.id)
        # LOG.info("Event PacketIn: %s", ev)
        # LOG.info("=============================================================")
        pass

    def install_static_rules(self, dp):
        dpid = dp.id
        cs = self.cs
        rt = self.rt
        # GROUP & VLAN ENTRIES for all rules @ TORs
        if 4 < dpid <= 5:
            lr_offset_ = (dpid - 1) * cs.n_lrack  # global offset, this physical ToR starts from the ith logical ToR
            ip_offset_ = lr_offset_ * cs.n_server  # global offset, this physical ToR starts from the ith server
            port_offset_ = 0
            # LOG.info("TOR installation setup: " + "logical rack no (" + str(lr_offset_) + "), " + "core port no(" + str(
            # port_offset_) + ")")

            for lr in range(cs.n_lrack):  # lr'th logical ToR within physical ToR
                # rack info
                vlan_id = cs.lr_ + lr_offset_

                # core port RULES (vlan, group)
                for cc in range(cs.n_server / cs.over_subscription):
                    core_port_id = cc + cs.port_core + lr * cs.n_server + cs.n_lrack * cs.n_server  # port # connecting to the core
                    # going to core
                    rt.create_group_l2_interface(dp, rt.config_group_l2_interface, vlan_id, core_port_id)
                    # vlan from core
                    rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, vlan_id, core_port_id)
                    print "core port |", "\tvlan #: ", vlan_id, "\tcore port #: ", core_port_id

                # ocs port rules (vlan, group)
                for ocs_ in range(cs.n_ocs):
                    ocs_port_id = cs.port_ocs + lr * cs.n_ocs + ocs_
                    print "ocs | ", "\tswitch ocs port: ", ocs_port_id

                    # going to ocs from logical rack
                    rt.create_group_l2_interface(dp, rt.config_group_l2_interface, vlan_id, ocs_port_id)
                    # vlan from ocs
                    rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, vlan_id, ocs_port_id)
                    # group for multicasting to OCS and ToR @ ToR
                    # rt.create_group_l2_multicast(dp, rt.config_group_l2_multicast_arp,
                    #                              rt.config_group_l2_multicast_arp_bucket, vlan_id, lr, cs.n_server,
                    #                              ocs_port_id)

                core_port_id_eps_test = (cs.port + cs.n_server * cs.n_lrack) + cs.n_server * lr
                core_port_id_ocs_test = cs.port_ocs + lr * cs.n_ocs
                # server port RULES
                flood_server_port = []
                for ss in range(cs.n_server):  # port_offset_'th server in lr'th ToR
                    # server info
                    server_port_id = cs.port + port_offset_
                    server_ip_addr = socket.inet_ntoa(struct.pack('!L', cs.ip_long + ip_offset_))
                    # server_ip_10_addr = socket.inet_ntoa(struct.pack('!L', cs.ip_10_long + ip_offset_))
                    flood_server_port.append(server_port_id)

                    # core info

                    core_port_id = server_port_id + cs.n_lrack * cs.n_server - (
                        (server_port_id + cs.n_lrack * cs.n_server - cs.port) % cs.over_subscription)
                    print "server port | ", "\tvlan #: ", vlan_id, "\t", server_ip_addr, "\tserver port #: ", server_port_id, "\tcore port #: ", core_port_id
                    # print "server port | ", "\tvlan #: ", vlan_id, "\t", server_ip_10_addr, "\tserver port #: ", server_port_id, "\tcore port #: ", core_port_id
                    # going to server
                    rt.create_group_l2_interface(dp, rt.config_group_l2_interface, vlan_id, server_port_id)
                    # vlan from server
                    rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, vlan_id, server_port_id)

                    # acl going to server
                    rt.create_acl_unicast(dp, rt.config_acl_unicast, vlan_id, server_ip_addr, server_port_id,
                                          cs.default_queue)
                    # rt.create_acl_unicast(dp, rt.config_acl_unicast, vlan_id, server_ip_10_addr, server_port_id,
                    #                       cs.default_queue)
                    # acl going to core @ ToR
                    rt.create_acl_unicast_low(dp, rt.config_acl_unicast_low, server_port_id, vlan_id, server_ip_addr,
                                              core_port_id, cs.default_queue)
                    # rt.create_acl_unicast_low(dp, rt.config_acl_unicast_low, server_port_id, vlan_id, server_ip_10_addr,
                    #                           core_port_id, cs.default_queue)

                    # arp going to core
                    rt.create_acl_arp(dp, rt.config_acl_arp, server_port_id, vlan_id, core_port_id,
                                      cs.default_queue)
                    # arp going to servers
                    if cs.over_subscription == 1:
                        rt.create_acl_arp(dp, rt.config_acl_arp, core_port_id, vlan_id, server_port_id,
                                          cs.default_queue)

                    if ip_offset_ == self.sender:
                        # for the OCS switching time measurement
                        rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, vlan_id, server_port_id,
                                                       core_port_id_ocs_test, '0x1989', cs.default_queue)
                        print "[sender_ocs_test] | ", "\tvlan #: ", vlan_id, "\tinport: ", server_port_id, "\toutport: ", core_port_id_ocs_test

                        # for the EPS rule update time measurement
                        rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, vlan_id, server_port_id,
                                                       core_port_id_eps_test, '0x1994', cs.default_queue)
                        print "[sender_eps_test] | ", "\tvlan #: ", vlan_id, "\tinport: ", server_port_id, "\toutport: ", core_port_id_eps_test

                    if ip_offset_ == self.receiver:
                        # for the OCS switching time measurement
                        rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, vlan_id,
                                                       core_port_id_ocs_test, server_port_id, '0x1989',
                                                       cs.default_queue)
                        print "[receiver_ocs_test] | ", "\tvlan #: ", vlan_id, "\tinport: ", core_port_id_ocs_test, "\toutport: ", server_port_id
                        rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, vlan_id,
                                                       core_port_id_ocs_test + 1, server_port_id, '0x1989',
                                                       cs.default_queue)
                        print "[receiver_ocs_test] | ", "\tvlan #: ", vlan_id, "\tinport: ", core_port_id_ocs_test + 1, "\toutport: ", server_port_id

                        # for the EPS rule update time measurement
                        rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, vlan_id,
                                                       core_port_id_eps_test, server_port_id, '0x1994',
                                                       cs.default_queue)
                        print "[receiver_eps_test] | ", "\tvlan #: ", vlan_id, "\tinport: ", core_port_id_eps_test, "\toutport: ", server_port_id
                        rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, vlan_id,
                                                       core_port_id_eps_test + 1, server_port_id, '0x1994',
                                                       cs.default_queue)
                        print "[receiver_eps_test] | ", "\tvlan #: ", vlan_id, "\tinport: ", core_port_id_eps_test + 1, "\toutport: ", server_port_id

                    ip_offset_ += 1
                    port_offset_ += 1

                if cs.over_subscription > 1:
                    print "arp | ", "\tvlan id: ", vlan_id, "\tports: ", flood_server_port, "\tgroup rule id: ", cs.arp_flood_id + vlan_id
                    rt.create_group_l2_flood(dp, rt.config_group_l2_multicast_arp,
                                             rt.config_group_l2_multicast_arp_bucket,
                                             vlan_id, flood_server_port, cs.arp_flood_id + vlan_id)
                    rt.create_acl_arp_flood(dp, rt.config_acl_arp_multicast, vlan_id, cs.default_queue,
                                            cs.arp_flood_id + vlan_id)

                lr_offset_ += 1
        #
        # # GROUP & VLAN ENTRIES for all rules @ Core
        # elif dpid == 0:
        #     ip_offset_ = 0
        #     # core port RULES (vlan, group)
        #     for cc in range(0, cs.n_prack * cs.n_lrack * cs.n_server / cs.over_subscription):
        #         core_port_id = cs.over_subscription * cc + 1
        #         # going to core
        #         rt.create_group_l2_interface(dp, rt.config_group_l2_interface, cs.core_vlan, core_port_id)
        #         # vlan from core
        #         rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, cs.core_vlan, core_port_id)
        #         print "core port vlan/group |", "\tvlan #: ", cs.core_vlan, "\tcore port #: ", core_port_id
        #
        #     for pc_ in range(0, cs.n_prack * cs.n_lrack * cs.n_server):  # loop through all the core ports
        #         core_port_ = cs.port_core + pc_ - (
        #             (cs.port_core + pc_ - cs.port_core) % cs.over_subscription)  # physical port number
        #         # [group] going out of core
        #         # rt.create_group_l2_interface(dp, config, cs.core_vlan, core_port_)
        #         # [vlan] coming to the core
        #         # rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, cs.core_vlan, core_port_)
        #
        #         print "core | ", "\tvlan: ", cs.core_vlan, "\tcore port #: ", core_port_, "\t", socket.inet_ntoa(
        #             struct.pack('!L', cs.ip_long + ip_offset_))
        #         # print "core | ", "\tvlan: ", cs.core_vlan, "\tcore port #: ", core_port_, "\t", socket.inet_ntoa(
        #         #     struct.pack('!L', cs.ip_10_long + ip_offset_))
        #         # [acl] unicast going out of core to ToRs
        #         rt.create_acl_unicast(dp, rt.config_acl_unicast, cs.core_vlan,
        #                               socket.inet_ntoa(struct.pack('!L', cs.ip_long + ip_offset_)), core_port_,
        #                               cs.default_queue)
        #         # rt.create_acl_unicast(dp, rt.config_acl_unicast, cs.core_vlan,
        #         #                       socket.inet_ntoa(struct.pack('!L', cs.ip_10_long + ip_offset_)), core_port_,
        #         #                       cs.default_queue)
        #         ip_offset_ += 1
        #
        #     # set update the rule for the gateway
        #     for pi_ in cs.gateway_port_ip:
        #         # [group]
        #         rt.create_group_l2_interface(dp, rt.config_group_l2_interface, cs.core_vlan, pi_[0])
        #         # [vlan]
        #         rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, cs.core_vlan, pi_[0])
        #
        #         print "core gateway | ", "\tvlan: ", cs.core_vlan, "\tcore port #: ", pi_[0], "\t", pi_[1]
        #         # [acl]
        #         rt.create_acl_unicast(dp, rt.config_acl_unicast, cs.core_vlan, pi_[1], pi_[0], cs.default_queue)
        #         rt.create_acl_unicast(dp, rt.config_acl_unicast, cs.core_vlan, pi_[2], pi_[0], cs.default_queue)
        #
        #     print "default rule: ", "\tport: ", cs.gateway_port_ip[1][0]
        #     rt.create_acl_unicast_low_wildcard(dp, rt.config_acl_unicast_low_wildcard, cs.core_vlan,
        #                                        cs.gateway_port_ip[1][0],
        #                                        cs.default_queue)
        #
        #     # [group] rule flood arp packets @ core
        #     core_port_list = list(range(cs.port_core + 0, cs.port_core + cs.n_prack * cs.n_lrack * cs.n_server))[
        #                      0::cs.over_subscription]
        #     for a in cs.gateway_port_ip:
        #         core_port_list.append(a[0])
        #     print "core arp: ", "\t", core_port_list
        #     rt.create_group_l2_flood(dp, rt.config_group_l2_multicast_arp,
        #                              rt.config_group_l2_multicast_arp_bucket,
        #                              cs.core_vlan, core_port_list, cs.arp_flood_id,
        #                              gateway_port_ip=cs.gateway_port_ip)
        #     # [acl] rule flood arp packets @ core
        #     rt.create_acl_arp_flood(dp, rt.config_acl_arp_multicast, cs.core_vlan, cs.default_queue,
        #                             cs.arp_flood_id)

        else:
            pass

        return
