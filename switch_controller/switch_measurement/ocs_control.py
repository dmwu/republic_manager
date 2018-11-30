#!/usr/bin/python
import sys
import os
import time

import signal

sys.path.insert(0, '/home/[SERVER_USERNAME]/github/republic_manager/')
import argparse
import copy
import json
from random import shuffle

import requests

from switch_controller.switch_measurement.common import *

ocs_url_fmt = 'http://%s:%d/fiber/ent_crs'
ocs_request_fmt = '{\"inport\":[%s],\"outport\":[%s]}'  # ,\"async\":%s}'


# file_output = None
#
#
# def signal_handler(signum, frame):
#     print('You pressed Ctrl+C!')
#     global file_output
#     file_output.flush()
#     file_output.close()
#     sys.exit(0)
#
#
# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


def get_ocs_port(node, cluster_configuration, experiment_config):
    switch_offset = node / cluster_configuration['node']['num_per_phy']  # ith switch in the cluster
    logical_rack_offset_within_switch = (node % cluster_configuration['node']['num_per_phy']) / (
        cluster_configuration['node']['num_per_phy'] / cluster_configuration['eps']['log'][
            'num_per_phy'])  # ith logical rack in the physical switch
    n_ocs = cluster_configuration['eps']['duplex_%dG' % experiment_config.transceiver_speed][
        'num_per_log']  # number of ocs port given to each logical rack
    ocs_starting = cluster_configuration['ocs']['duplex_%dG' % experiment_config.transceiver_speed][
        'starting']  # starting port number on ocs
    ocs_offset_within_switch = switch_offset * \
                               cluster_configuration['eps']['duplex_%dG' % experiment_config.transceiver_speed][
                                   'num']  # starting port number of ocs for the physical rack

    return ocs_starting + logical_rack_offset_within_switch * n_ocs + ocs_offset_within_switch


def run_experiment(args):
    experiment_config = load_switch_measurement_config(args.experiment_config)

    config_file = open(experiment_config.cluster_configuration)
    cluster_configuration = json.load(config_file)
    config_file.close()

    # global file_output
    if not os.path.exists(experiment_config.control_output_directory):
        os.makedirs(experiment_config.control_output_directory)
    file_output = open(
        experiment_config.control_output_directory + '/' + experiment_config.control_output_filename + '-ocs.csv', 'w')

    # get target ocs port (port going from/to the sender and the receiver)
    sender_port = get_ocs_port(experiment_config.sender, cluster_configuration, experiment_config)
    receiver_port_0 = get_ocs_port(experiment_config.receiver, cluster_configuration, experiment_config)
    receiver_port_1 = receiver_port_0 + 1  # get_ocs_port(experiment_config.receiver2, cluster_configuration, experiment_config)
    # receiver_port_0 = get_ocs_port(experiment_config.receiver1, cluster_configuration, experiment_config)
    # receiver_port_1 = get_ocs_port(experiment_config.receiver2, cluster_configuration, experiment_config)
    receiver_port = [receiver_port_0, receiver_port_1]

    # get other ports (port that are concurrently set up)
    ports = [i + 1 for i in range(192)]
    ports.remove(sender_port)
    ports.remove(receiver_port_0)
    ports.remove(receiver_port_1)
    ports.remove(args.spareport)
    ports.remove(args.spareport + 1)

    ocs_url = ocs_url_fmt % (args.api_ip, args.api_port)
    # ocs_request = ocs_request_fmt % (','.join([str(receiver_port[1])]), ','.join([str(sender_port)]))
    ocs_request = ocs_request_fmt % (
        ','.join([str(receiver_port[1]), str(args.spareport + 1), str(receiver_port[0])]),
        ','.join([str(args.spareport + 1), str(sender_port), str(args.spareport)]))
    requests.post(ocs_url, json=json.loads(ocs_request))

    # config ocs
    for i in range(experiment_config.num_reconfig):
        port_tmp = copy.copy(ports)
        shuffle(port_tmp)
        inport_l_concurrent = port_tmp[:experiment_config.num_concurrent - 2]
        inport_l_concurrent.append(sender_port)
        # inport_l_concurrent.append(receiver_port[i % 2])
        # inport_l_concurrent.append(receiver_port[(i + 1) % 2])

        # inport_l_concurrent.append(receiver_port[0])

        inport_l_concurrent.append(args.spareport)

        port_tmp = copy.copy(ports)
        shuffle(port_tmp)
        outport_l_concurrent = port_tmp[:experiment_config.num_concurrent - 2]
        outport_l_concurrent.append(receiver_port[i % 2])
        # outport_l_concurrent.append(receiver_port[(i + 1) % 2])
        # outport_l_concurrent.append(sender_port)

        # outport_l_concurrent.append(receiver_port[(i + 1) % 2])

        outport_l_concurrent.append(receiver_port[(i + 1) % 2])

        inport = [str(a) for a in inport_l_concurrent]
        outport = [str(a) for a in outport_l_concurrent]
        ocs_request = ocs_request_fmt % (','.join(inport), ','.join(outport))  # , 'true')
        # start_time = time.time()
        # print switching_notify(convert_node_to_ip(experiment_config.sender), args.notify_port), (
        #
        #                                                                  time.time() - start_time) * 1000, 'ms'
        sec, usec = get_time_of_day()
        file_output.write("%d, %d\n" % (sec, usec))
        file_output.flush()
        start_time = time.time()
        print requests.post(ocs_url, json=json.loads(ocs_request)), (time.time() - start_time) * 1000, 'ms'
        time.sleep(experiment_config.reconfig_interval)
    file_output.close()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="Do something.")
    parser.add_argument('-I', '--api_ip', type=str, default='[RESEARCH_NETWORK_PREFIX].152', required=False, help="IP address of API")
    parser.add_argument('-P', '--api_port', type=int, default=8080, required=False, help="Port of API")
    # parser.add_argument('-n', '--notify_port', type=int, default=10033, required=False, help="Port of notify")
    parser.add_argument('-e', '--experiment_config', type=str, default='../../ryu/ofdpa/switch_measurement.conf',
                        required=False, help="Path to experiment configuration")
    parser.add_argument('-s', '--spareport', type=int, default=177, required=False,
                        help="Spare port on OCS")
    args = parser.parse_args()

    # configure the ocs
    run_experiment(args)
    pass


if __name__ == '__main__':
    main()
