#!/usr/bin/python
import ConfigParser
import argparse
import os
import re
import socket
from os import path, access, R_OK

# extract the TL1 root path
# TL1_ROOT is set at the time of installation
# tl1_root_path=os.environ['TL1_ROOT'];
tl1_root_path = os.getcwd()


# sys.path.append(tl1_root_path)
# sys.path.append(tl1_root_path + "/scripts")
# sys.path.append(tl1_root_path + "/config")

def check_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    # print os.path.abspath(x)
    if not os.path.exists(x):
        raise argparse.ArgumentError(x, "{0} does not exist".format(x))
    return x


def special_string(v):
    fields = v.split(".")
    # Raise a value error for any part of the string
    # that doesn't match your specification. Make as many
    # checks as you need. I've only included a couple here
    # as examples.
    if len(fields) != 3 and len(fields) != 1:
        raise argparse.ArgumentTypeError("Port Number should be in NPID or x.y.z format")
    if len(fields) == 3:  # port id format
        expr = '[1-6]\.[1-8]\.[1-8]'
        m = re.match(expr, v)
        if m:
            return m.group()
        else:
            msg = "Invalid Port:" + v + " has to be in this range [1-6].[1-8].[1-8]"
            raise argparse.ArgumentTypeError(msg)
    elif len(fields) == 1:  # NPID format
        port = int(v)
        if port <= 0 or port >= 384:
            msg = "Invalid Port:" + v + " has to be 1<= port <= 384 "
            raise argparse.ArgumentTypeError(msg)
        else:
            return port


def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1
    except socket.error:
        return 0


def ip_string(v):
    fields = v.split(".")
    if len(fields) != 4 and len(fields) != 1:
        raise argparse.ArgumentTypeError("Invalid IP address or hostname ")
    if len(fields) == 4:  # ip in dotted
        try:
            socket.inet_aton(v)
        except:
            msg = "Invalid IP:" + v
            raise argparse.ArgumentTypeError(msg)
        else:
            return v
    elif len(fields) == 1:  # hostname
        found = hostname_resolves(v)
        if found:
            return v
        else:
            msg = "Unable to resolve hostname:", v
            raise argparse.ArgumentTypeError(msg)


class Options:
    def __init__(self):
        self.testtype = ""
        self.inportsfile = ""
        self.outportsfile = ""
        self.inport = "1"
        self.outport = "1"
        self.targetip = ""
        self.targetport = ""
        self.username = ""
        self.password = ""
        self.deleteall = ""
        self.concurrency = ""

        self.parser = None
        self.results = None

        self.add_options()

    def add_options(self):
        # Parse any conf_file specification
        # We make this parser with add_help=False so that
        # it doesn't parse -h and print help.
        conf_parser = argparse.ArgumentParser(
            description=__doc__,  # printed with -h/--help
            # Don't mess with format of description
            formatter_class=argparse.RawDescriptionHelpFormatter,
            # Turn off help, so we print all options in response to -h
            add_help=False
        )

        # configuration file name
        config_file = tl1_root_path + "/config" + "/config.txt"
        # Or the user may specify another
        conf_parser.add_argument("-c", "--config", help="config file",
                                 metavar="FILE", default=config_file)

        args, remaining_argv = conf_parser.parse_known_args()
        # args.config is now either the default or the user specified config
        config = ConfigParser.SafeConfigParser()
        # print "command line specified:", remaining_argv
        # print 'args:', args

        # read the config file
        if path.isfile(args.config) and access(args.config, R_OK):
            # The file exists and can be read so greb defaults from it
            config.read([args.config])
            try:
                defaults = dict(config.items("Defaults"))
            except:  # default conf
                print "Unable to find sections in Config file:" + config_file
                defaults = {'target': '[INTERNAL_NETWORK_PREFIX].0.2',
                            'username': '',
                            'password': '',
                            'loglevel': 'ERROR',
                            'report': '',
                            'ports': '272',
                            'loopback': '',
                            'test': '1XN',
                            'concurrency': '4',
                            'input_ports': 'inports272.txt',
                            'output_ports': 'inports272.txt'}
                raise Exception()

        else:  # default conf
            # The file doesn't exist or can't be read so use the defaults
            print('Config file %s is missing or is not readable - using defaults' %
                  args.config)
            defaults = {'target': '[INTERNAL_NETWORK_PREFIX].0.2',
                        'username': '',
                        'password': '',
                        'loglevel': 'ERROR',
                        'report': '',
                        'ports': '272',
                        'loopback': '',
                        'test': '1XN',
                        'concurrency': '4',
                        'input_ports': 'inports272.txt',
                        'output_ports': 'inports272.txt'}

        # Here, defaults contains the configs

        # Parse rest of arguments
        # The user can override any argument configured by either the default or 
        # config file with a command line argument
        # Don't suppress add_help here so it will handle -h

        # Inherit options from config_parser, a new parser
        self.parser = argparse.ArgumentParser(parents=[conf_parser])
        self.parser.set_defaults(**defaults)

        self.parser.add_argument("-T", "--target", help="target ip address", dest='target', type=ip_string)
        self.parser.add_argument("-P", "--targetport", help="target port", dest="targetport", default='10034')
        self.parser.add_argument("-u", "--username", help="username", dest='username')
        self.parser.add_argument("-p", "--password", help="password", dest='password')
        self.parser.add_argument("--ports", help="ports")
        self.parser.add_argument("--loopback", help="loopback connection test", action='store_true')
        self.parser.add_argument("--deleteall", help="deleteall connections", action='store_true')
        self.parser.add_argument('--test', dest='test',
                                 choices=['1XN', 'NX1', '1XNX1', '4XN', 'NX4', 'loopback', 'unibulk', 'bibulk', 'fullbulk', 'stress'],
                                 help='Test Type=1XN, NX1, loopback, unibulk, bibulk, fullbulk, stress')
        self.parser.add_argument('--version', action='version', version='%(prog)s 1.0')
        self.parser.add_argument('--input_ports', dest='input_ports', type=check_file, help='Input Ports File , Npid or pid format')
        self.parser.add_argument('--output_ports', dest='output_ports', type=check_file, help='Output Ports File , Npid or pid format')
        self.parser.add_argument('--iport', dest='inport', default='1', type=special_string, help='Input Port, Npid or pid format, for the 1XN')
        self.parser.add_argument('--oport', dest='outport', default='1', type=special_string, help='Output Port, Npid or pid format, for the NX1')
        self.parser.add_argument("--concurrency", help="number of connections at one time")

        print remaining_argv
        self.results = self.parser.parse_args(remaining_argv)

        self.handle_options()

    def handle_options(self):
        # print self.parser.parse_args()
        #       try :
        #               self.results=self.parser.parse_args();
        #       except IOError, e:
        #               print str(e);
        #               sys.exit();

        self.testtype = self.results.test
        self.inportsfile = self.results.input_ports
        self.outportsfile = self.results.output_ports
        self.targetip = self.results.target
        self.targetport = self.results.targetport
        self.username = self.results.username
        self.password = self.results.password
        self.inport = self.results.inport
        self.outport = self.results.outport
        self.deleteall = self.results.deleteall
        self.concurrency = self.results.concurrency

        if self.deleteall:
            print 'Proceeding to delete all connections...'

        print "************** Options **************"
        print "Target IP:\t", self.targetip
        print "Target Port:\t", self.targetport
        print "Username:\t", self.username
        print "Password:\t", self.password
        print "In Ports file:\t", self.inportsfile
        print "Out Ports file:\t", self.outportsfile
        print "In Port:\t", self.inport
        print "Out Port:\t", self.outport
        print "Delete All:\t", self.deleteall
        print "*********** Options END *************"

    def get_serverip(self):
        return self.targetip

    def get_serverport(self):
        return self.targetport

    def get_testtype(self):
        return self.testtype

    def get_inport(self):
        return self.inport

    def get_outport(self):
        return self.outport

    def get_inportsfile(self):
        return self.inportsfile

    def get_outportsfile(self):
        return self.outportsfile

    def get_deleteall(self):
        return self.deleteall

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password
