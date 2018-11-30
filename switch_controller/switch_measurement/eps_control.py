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
import os
import time

sys.path.insert(0, '/home/[SERVER_USERNAME]/github/republic_manager/')
import socket
import struct
from switch_controller.switch_measurement.common import *

from ryu.base import app_manager
from ryu.controller import dpset
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from switch_controller.quanta.common import SystemConfig, RuleTempleate
from switch_controller.quanta.ofdpa.config_parser import ConfigParser
from switch_controller.switch_measurement.common import load_switch_measurement_config


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
        self.num_reconfig = CONF.num_reconfig
        self.reconfig_interval = CONF.reconfig_interval
        self.control_output_directory = CONF.control_output_directory
        self.control_output_filename = CONF.control_output_filename

        self.sys_conf = ConfigParser.get_config(self.cluster_configuration)
        # pprint.pprint(sys_conf)
        self.cs = SystemConfig(self.sys_conf, self.transceiver_speed)
        self.rt = RuleTempleate(self.rule_template_directory)

        if not os.path.exists(self.control_output_directory):
            os.makedirs(self.control_output_directory)
        self.file_output = open(self.control_output_directory + '/' + self.control_output_filename + '-eps.csv', 'w')

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        if ev.enter:
            self.install_static_rules(ev.dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def handler_packet_in(self, ev):
        pass

    def install_static_rules(self, dp):
        dpid = dp.id
        cs = self.cs
        rt = self.rt

        # GROUP & VLAN ENTRIES for all rules @ TORs
        if dpid == 0:
            ip_offset_ = 0
            # core port RULES (vlan, group)
            for cc in range(0, cs.n_prack * cs.n_lrack * cs.n_server / cs.over_subscription):
                core_port_id = cs.over_subscription * cc + 1
                # going to core
                rt.create_group_l2_interface(dp, rt.config_group_l2_interface, cs.core_vlan, core_port_id)
                # vlan from core
                rt.create_vlan(dp, rt.config_vlan_tagged, rt.config_vlan_untagged, cs.core_vlan, core_port_id)
                print "core port vlan/group |", "\tvlan #: ", cs.core_vlan, "\tcore port #: ", core_port_id

            # get in port
            # dpid_sender = self.sender / (cs.n_server * cs.n_lrack)
            logical_rack_sender = self.sender / cs.n_server * cs.n_server + 1

            # get out ports
            # dpid_receiver = self.receiver / (cs.n_server * cs.n_lrack)
            logical_rack_receiver = self.receiver / cs.n_server * cs.n_server + 1

            for i in range(self.num_reconfig):
                # start_time = time.time()
                # print switching_notify(convert_node_to_ip(self.sender), self.notify_port), (time.time() - start_time) * 1000, 'ms'

                sec, usec = get_time_of_day()
                self.file_output.write("%d, %d\n" % (sec, usec))
                start_time = time.time()
                rt.create_acl_unicast_eth_port(dp, rt.config_acl_unicast_eth_port, cs.core_vlan,
                                               logical_rack_sender, logical_rack_receiver + (i % 2), '0x1994',
                                               cs.default_queue)

                print (time.time() - start_time) * 1000, 'ms', "[dynamic rule] | ", "\tvlan #: ", \
                    cs.core_vlan, "\tinport: ", logical_rack_sender, "\toutport: ", logical_rack_receiver + (i % 2)
                time.sleep(self.reconfig_interval)
                self.file_output.flush()
            self.file_output.flush()
            self.file_output.close()

        else:
            pass

        return
