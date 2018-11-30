#!/usr/bin/python
import json
import pprint
import signal
import sys
import time

import argparse
from flask import Flask
from flask import request
from connections import GxcConnections


def signal_handler(signum, frame):
    print('You pressed Ctrl+C!')
    connectionObj.logout()
    connectionObj.close()
    sys.exit(0)


# setup signal processing handler
signal.signal(signal.SIGINT, signal_handler)

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Do something.")
parser.add_argument('-i', '--ocs_ip', type=str, default='[RESEARCH_NETWORK_PREFIX].88', required=False, help="IP address of OCS")
parser.add_argument('-p', '--ocs_port', type=int, default=10034, required=False, help="Port of OCS")
parser.add_argument('-I', '--api_ip', type=str, default='0.0.0.0', required=False, help="IP address of API")
parser.add_argument('-P', '--api_port', type=int, default=8080, required=False, help="Port address of API")
parser.add_argument('-u', '--username', type=str, default='[OCS_USERNAME]', required=False, help="Username for login")
parser.add_argument('-w', '--password', type=str, default='[OCS_PASSWORD]', required=False, help="Password for login")
parser.add_argument('-c', '--cluster_config', type=str, default='../conf/cluster_conf.json', required=False,
                    help="Path to cluster configuration")
args = parser.parse_args()
connectionObj = GxcConnections(args)


@app.route('/')
def api_root():
    return 'Welcome'


@app.route('/fiber/ent_crs', methods=['POST'])
def api_fiber_ent_crs():
    if request.headers['Content-Type'] == 'application/json':
        # print request.data
        # print request.json
        inport_list = request.json["inport"]
        ourport_list = request.json["outport"]
        async = request.json['async'] if 'async' in request.json else False
        start_time = time.time()
        connectionObj.ent_crs_fiber(inport_list, ourport_list, async=async)
        print (time.time() - start_time) * 1000, 'ms'
    else:
        raise Exception('spam', 'eggs')
    return "\n"


@app.route('/fiber/ent_crs_all', methods=['POST'])
def api_fiber_ent_crs_all():
    if request.headers['Content-Type'] == 'application/json':
        connectionObj.ent_crs_fiber_all()
    else:
        raise Exception('spam', 'eggs')
    return "\n"


@app.route('/fiber/del_crs', methods=['POST'])
def api_fiber_del_crs():
    if request.headers['Content-Type'] == 'application/json':
        # print request.data
        inport_list = request.json["inport"]
        ourport_list = request.json["outport"]
        connectionObj.dlt_crs_fiber(inport_list, ourport_list)
    else:
        raise Exception('spam', 'eggs')
    return "\n"


@app.route('/fiber/del_crs_all', methods=['POST'])
def api_fiber_del_crs_all():
    if request.headers['Content-Type'] == 'application/json':
        connectionObj.dlt_crs_fiber_all()
    else:
        raise Exception('spam', 'eggs')
    return "\n"


def config_initial_connections(args):
    # load the cluster configuration
    file = open(args.cluster_config)
    cluster_config = json.load(file)
    file.close()

    low_power_ports = range(cluster_config['ocs']['duplex_10G']['starting'],
                            cluster_config['ocs']['duplex_10G']['starting']
                            + cluster_config['ocs']['duplex_10G']['num'])
    high_power_ports = range(cluster_config['ocs']['duplex_40G']['starting'],
                             cluster_config['ocs']['duplex_40G']['starting']
                             + cluster_config['ocs']['duplex_40G']['num'])

    splitter = cluster_config['ocs']['splitters'][0]['starting']
    fanout = cluster_config['ocs']['splitters'][0]['fanout']
    splitter_ports = range(splitter, splitter + len(high_power_ports) * fanout, fanout)
    feeder_src_ports = [a['source'] for a in cluster_config['ocs']['feeders']]
    feeder_dst_ports = [a['destination'] for a in cluster_config['ocs']['feeders']]
    relay_ports = [port for port in range(cluster_config['ocs']['relay']["starting"],
                                          cluster_config['ocs']['relay']["starting"] + sum(
                                              [a["num"] for a in cluster_config['eps']['relay']]))]

    # 10GbE transceiver self-loop
    connectionObj.ent_crs_fiber(low_power_ports, low_power_ports)
    # 40GbE transceiver self-loop
    connectionObj.ent_crs_fiber(high_power_ports, splitter_ports)
    connectionObj.ent_crs_fiber(splitter_ports, high_power_ports)
    # 10GbE feeders
    connectionObj.ent_crs_fiber(feeder_src_ports, feeder_dst_ports)
    connectionObj.ent_crs_fiber(feeder_dst_ports, feeder_src_ports)
    # 10GbE relays
    connectionObj.ent_crs_fiber(relay_ports, relay_ports)


def initialization(args):
    connectionObj.dlt_crs_fiber_all()
    # connectionObj.ed_param('PowerMonitoringPeriod', 20)
    config_initial_connections(args)


def main():
    # setup initial OCS circuit configuration
    initialization(args)

    # start server
    app.run(host=args.api_ip, port=args.api_port, debug=False)


if __name__ == '__main__':
    main()
