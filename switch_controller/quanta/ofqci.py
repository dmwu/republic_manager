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
#import ConfigParser
#   This is a script intended
#   to use by Ryu OpenFlow controller
#
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser
#
from ofdpa.config_parser import ConfigParser
from ofdpa.mods import Mods
#
import sys
#
class OfdpaQci(app_manager.RyuApp):

    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    

    def __init__(self, *args, **kwargs):
        super(OfdpaQci, self).__init__(*args, **kwargs)
      
    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        print "=Event DP="
        print "dpid: %i" % ev.dp.id
        self.build_packets(ev.dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        print "=Event PacketIn="

    def build_packets(self, dp):

        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        req = ofp_parser.OFPQueueGetConfigRequest(dp, 2)

        cookie = cookie_mask = 0
        table_id = 60
        idle_timeout = hard_timeout = 0
        priority = 32768
        buffer_id = ofp.OFP_NO_BUFFER

        match = ofp_parser.OFPMatch(
        	in_port=1,
        	eth_type=0x800)

        match.set_vlan_vid(0)
        match.set_vlan_vid_masked(0,0xfff)
        
        #actions = [ofp_parser.OFPActionOutput(4, 0)]
        actions = [ofp_parser.OFPActionGroup(0xa0001)]

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS,
                                                 actions)]
                                                 
        req = ofp_parser.OFPFlowMod(dp, cookie, cookie_mask,
                                    table_id, ofp.OFPFC_ADD,
                                    idle_timeout, hard_timeout,
                                    priority, buffer_id,
                                    ofp.OFPP_ANY, ofp.OFPG_ANY,
                                    ofp.OFPFF_SEND_FLOW_REM,
                                    match, inst)
       
        dp.send_msg(req)
        print "message sent"
        
