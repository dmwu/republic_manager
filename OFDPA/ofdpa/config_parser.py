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
#
#
import json
#
class ConfigParser():

        def __init__(self, *args, **kwargs):
            super(ConfigParser, self).__init__(*args, **kwargs)

        @staticmethod
        def get_working_set(filename):
            #
            #print "=================> filename %s" % filename
            main_config_file = open(filename)
            main_config = json.load(main_config_file)
            #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            #print "=================> main_config %s" % main_config
            #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            main_config_file.close()
            #
            #print "=================> main_config[config_directory] %s" %main_config["config_directory"]
            #print "=================> main_config[working_set] %s" %main_config["working_set"]   
            
            working_set_name = main_config["config_directory"]
            #print "=================> working_set_name %s" %working_set_name
            working_set_name += '/'
            working_set_name += main_config["working_set"]
            #print "=================> working_set_name %s" %working_set_name
            #
            print "------------------------------------------------------------"
            print "working set %s" % working_set_name
            print "------------------------------------------------------------"
            working_set_file = open(working_set_name)
            working_set = json.load(working_set_file)
            working_set_file.close()
            print "=================> working_set %s" % working_set
            return main_config["config_directory"], working_set["working_set"]

        @staticmethod
        def get_config(filename):
            #
            config_file = open(filename)
            config = json.load(config_file)
            config_file.close()
            return config
        
        @staticmethod
        def get_config_type(config):
            return config.keys()

        @staticmethod
        def get_flow_mod(config):
            return config["flow_mod"]

        @staticmethod
        def get_group_mod(config):
            return config["group_mod"]


        @staticmethod
        def get_matches(config):
            return config["match"]
        
        @staticmethod
        def get_instr_config(config):
            return config["instructions"]

        @staticmethod
        def get_buckets_config(config):
            return config["buckets"]

        '''
        @staticmethod
        def get_actions(config):
            return action_config
        
        @staticmethod
        def get_instructions(config):
            return instruction_config
        '''




        '''
        get flow probably better put in the flow constructor due
        a lot of one range parameters
        '''
