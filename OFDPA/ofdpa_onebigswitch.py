#*********************************************************************
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
#*********************************************************************
import ConfigParser
#   This is a script intended
#   to use by Ryu OpenFlow controller
#
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
#
from ofdpa.config_parser import ConfigParser
from ofdpa.mods import Mods
#
import sys
import copy
import time

# from sender import sender

#
class OfdpaTe(app_manager.RyuApp):

    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    CONFIG_FILE = 'config/ofdpa_test.json'

    def __init__(self, *args, **kwargs):
        super(OfdpaTe, self).__init__(*args, **kwargs)
      
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        print "=Event DP="
        print "dpid: %i" % ev.dp.id
        if ev.enter:
            self.build_packets(ev.dp)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        print "------------------------------------------------------------"
        print "=Event PacketIn="
        print "------------------------------------------------------------"

    def build_packets(self, dp):
        #
        config_dir, working_set = ConfigParser.get_working_set(self.CONFIG_FILE)
        #
        # mod_config_list = []

        # self.ctrl_send = sender()


        '''add unicast group entry'''
        num_ports = 48

        unicast_group_entry_t = 'template_unicast_group_entry.json'
        full_filename = config_dir + '/' + unicast_group_entry_t
        config = ConfigParser.get_config(full_filename)
        for port in range(1, num_ports + 1):
            unicast_group = copy.deepcopy(config)
            unicast_group['group_mod']['_name'] += "%04x" % port
            unicast_group['group_mod']['group_id'] += "%04x" % port
            unicast_group['group_mod']['buckets'][0]['actions'][0]['output']['port'] += str(port)
            for type in ConfigParser.get_config_type(unicast_group):
                if (type == "group_mod"):
                    mod_config = ConfigParser.get_group_mod(unicast_group)
                    mod = Mods.create_group_mod(dp, mod_config)            
                else:
                    raise Exception("Wrong type", type)
            print unicast_group
            dp.send_msg(mod)


        ''' add vlan (un)tagged entry '''
        vlan_tagged_entry_t = 'template_vlan_tagged_entry.json'
        full_filename = config_dir + '/' + vlan_tagged_entry_t
        config = ConfigParser.get_config(full_filename)
        vlan_untagged_entry_t = 'template_vlan_untagged_entry.json'
        full_filename_untagged = config_dir + '/' + vlan_untagged_entry_t
        config_untagged = ConfigParser.get_config(full_filename_untagged)        
        for port in range(1, num_ports + 1):
            vlan_tagged = copy.deepcopy(config)
            vlan_tagged['flow_mod']['_name'] += str(port)
            vlan_tagged['flow_mod']['match']['in_port'] += str(port)
            for type in ConfigParser.get_config_type(vlan_tagged):
                if (type == "flow_mod"):
                    mod_config = ConfigParser.get_flow_mod(vlan_tagged)
                    mod = Mods.create_flow_mod(dp, mod_config)            
                else:
                    raise Exception("Wrong type", type)
            # print vlan_tagged
            dp.send_msg(mod)
            vlan_untagged = copy.deepcopy(config_untagged)
            vlan_untagged['flow_mod']['_name'] += str(port)
            vlan_untagged['flow_mod']['match']['in_port'] += str(port)
            for type in ConfigParser.get_config_type(vlan_untagged):
                if (type == "flow_mod"):
                    mod_config_untagged = ConfigParser.get_flow_mod(vlan_untagged)
                    mod_untagged = Mods.create_flow_mod(dp, mod_config_untagged)            
                else:
                    raise Exception("Wrong type", type)
            # print vlan_untagged
            dp.send_msg(mod_untagged)

        ''' add acl unicast entry '''
        acl_unicast_entry_t = 'template_acl_unicast_entry.json'
        full_filename = config_dir + '/' + acl_unicast_entry_t
        config = ConfigParser.get_config(full_filename)
        for port in range(1, num_ports + 1):
            acl_unicast = copy.deepcopy(config)
            acl_unicast['flow_mod']['_name'] += str(port)
            acl_unicast['flow_mod']['match']['ipv4_dst'] += str(port + 110)
            acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][0]['set_queue']['queue_id'] += str(0)
            acl_unicast['flow_mod']['instructions'][0]['write'][0]['actions'][1]['group']['group_id'] += "%04x" % port
            # print "--------------------------"
            # print acl_unicast
            for type in ConfigParser.get_config_type(acl_unicast):
                if (type == "flow_mod"):
                    mod_config = ConfigParser.get_flow_mod(acl_unicast)
                    mod = Mods.create_flow_mod(dp, mod_config)            
                else:
                    raise Exception("Wrong type", type)
            # print acl_unicast
            dp.send_msg(mod)


        for filename in working_set:
            #
            full_filename = config_dir + '/' + filename
            #
            config = ConfigParser.get_config(full_filename)
            # print "------------------------------------------------------------"
            # print "processing file: %s" %  full_filename
            # print "config: %s" % config
            # print config['group_mod']['group_id']
            # print config['group_mod']['buckets'][0]['actions'][0]['output']['port']
            # print "------------------------------------------------------------"            
            #
            # print ConfigParser.get_config_type(config)
            for type in ConfigParser.get_config_type(config):
                #
                if (type == "flow_mod"):
                    mod_config = ConfigParser.get_flow_mod(config)
                    mod = Mods.create_flow_mod(dp, mod_config)
                    #
                elif (type == "group_mod"):
                    #
                    mod_config = ConfigParser.get_group_mod(config)
                    mod = Mods.create_group_mod(dp, mod_config)
                # time.sleep(.3)

            # print "mod len: %i" % sys.getsizeof(mod)
            dp.send_msg(mod)
            # print "message sent"


            # mod_config_list.append(mod_config)



        # print mod_config_list[6]
        # print mod_config_list[7]

        # for i in range (1,10):
        #     time.sleep(3)
        #     print mod_config_list[6]
        #     # self.ctrl_send.send_one()
        #     mod = Mods.create_flow_mod(dp, mod_config_list[6])
        #     dp.send_msg(mod)
        #     print "message sent"

        #     time.sleep(3)
        #     print mod_config_list[7]
        #     # self.ctrl_send.send_one()
        #     mod = Mods.create_flow_mod(dp, mod_config_list[7])
        #     dp.send_msg(mod)
        #     print "message sent"
