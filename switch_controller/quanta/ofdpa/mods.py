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
#
#
#
from buckets import Buckets
from config_parser import ConfigParser
from instructions import Instructions
from matches import Matches
from utils import Utils


#
class Mods():
    def __init__(self, *args, **kwargs):
        super(Mods, self).__init__(*args, **kwargs)

    @staticmethod
    def create_flow_mod(dp, config):
        #
        matches_config = ConfigParser.get_matches(config)
        matches = Matches.create_matches(dp, matches_config)
        #
        instr_config = ConfigParser.get_instr_config(config)
        instructions = None
        if instr_config is not None:
            instructions = Instructions.create_instructions(dp, instr_config)
        #

        priority = ConfigParser.get_priority(config)

        mod = dp.ofproto_parser.OFPFlowMod(
            dp,
            cookie=0,
            cookie_mask=0,
            table_id=Utils.get_table(config["table"]),
            command=Utils.get_mod_command(dp, config["cmd"]),
            idle_timeout=0,
            hard_timeout=0,
            priority=priority,
            buffer_id=0,
            out_port=Utils.get_mod_port(dp, config["port"]) if "port" in config else 0,
            out_group=Utils.get_mod_group(dp, config["group"]) if "group" in config else 0,
            flags=0,
            match=matches,
            instructions=instructions
        )
        return mod

    @staticmethod
    def create_group_mod(dp, config):
        #
        buckets_config = ConfigParser.get_buckets_config(config)
        buckets = Buckets.create_buckets(dp, buckets_config)
        #

        mod = dp.ofproto_parser.OFPGroupMod(
            dp,
            Utils.get_mod_command(dp, config["cmd"]),
            Utils.get_mod_type(dp, config["type"]),
            Utils.get_mod_group(dp, config["group_id"]),
            buckets
        )
        return mod
