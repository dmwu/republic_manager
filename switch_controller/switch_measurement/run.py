#!/usr/bin/python
import json
import os
import socket
import sys
import pprint
import numpy as np
from sys import platform
import matplotlib.pyplot as plt
import struct

measurement = ['ocs', 'eps']
ocs_concurrent = [10, 30, 50, 70]

plt.switch_backend('agg')


def draw_boxplot(x, y, xlabel, ylabel, grid=False, ylim=None, name=""):
    fig = plt.figure(figsize=(4, 3))
    ax = fig.add_subplot(111)
    bp = ax.boxplot(y, patch_artist=True)
    for flier in bp['fliers']:
        flier.set(marker='x', color='k', alpha=0.6)
    ax.set_xticklabels([str(a) for a in x])
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.set_ylim(bottom=0)
    if ylim is not None:
        ax.set_ylim(top=ylim)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    fig.tight_layout()
    if len(name) == 0:
        plt.show()
    else:
        plt.savefig(name + '.eps', format='eps')


FirstPath = ""
if platform == "linux" or platform == "linux2":
    FirstPath = "home"
elif platform == "darwin":
    FirstPath = "Users"
# print FirstPath

sys.path.insert(0, '/%s/[SERVER_USERNAME]/github/republic_manager/' % FirstPath)

import subprocess
import time

import switch_controller.switch_measurement.common as cmmn

remote_server_username = '[SERVER_USERNAME]'
remote_server_root_username = '[ROOT_USERNAME]'
ip_controller = '[RESEARCH_NETWORK_PREFIX].152'
eps_ip_base = '[RESEARCH_NETWORK_PREFIX].202'
base_directory = '/home/[SERVER_USERNAME]/github/'
repository_name = 'republic_manager'
working_directory = '%s/%s/' % (base_directory, repository_name)
cmd_config_path = "%s/switch_controller/switch_measurement/switch_measurement.json"

cmd_remove_code_fmt = 'cd %s; ' \
                      'rm -rf %s' % (base_directory, repository_name)

cmd_get_code_fmt = 'cd %s; ' \
                   'git clone \"https://github.com/sunxiaoye0116/%s.git\"; ' \
                   'cd %s; ' \
                   'git checkout -b master --track origin/master' % (
                       base_directory, repository_name, working_directory)

cmd_update_code_fmt = 'cd %s; ' \
                      'git reset --hard; ' \
                      'git pull \"https://github.com/sunxiaoye0116/%s.git\" master' % (
                          working_directory, repository_name)

cmd_start_ocs_ctrl = "cd %s; screen -d -m ./switch_controller/glimmerglass/glimmerglass_controller.py" % working_directory
cmd_start_eps_ctrl = "cd %s; screen -d -m ryu-manager --ofp-tcp-listen-port 6633 ./switch_controller/switch_measurement/eps_config.py" % working_directory
cmd_start_ocs_sw = "\"cd %s; screen -d -m ./switch_controller/switch_measurement/ocs_control.py --experiment_config %s\"" % (
    working_directory, cmd_config_path % (working_directory))
cmd_start_eps_sw = "\"cd %s; screen -d -m ryu-manager --ofp-tcp-listen-port 6633 ./switch_controller/switch_measurement/eps_control.py\"" % working_directory

cmd_compile_tx_fmt = "cd %s/switch_controller/switch_measurement/eclipse/switch_measurement/Debug_%s/; make clean; screen -d -m make"
cmd_start_receiver_fmt = "\"cd %s/switch_controller/switch_measurement/eclipse/switch_measurement/Debug_receiver/; screen -d -m ./switch_measurement_receiver -f eth3 -t %s %s\""
cmd_start_sender_fmt = "\"cd %s/switch_controller/switch_measurement/eclipse/switch_measurement/Debug_sender/; screen -d -m ./switch_measurement_sender -f eth3 -i 50 -t %s\""

cmd_kill_program_fmt = "ps aux | grep %s | grep -v grep | awk '{print $2}' | xargs kill"
cmd_disable_linkscan_fmt = "(echo open %s;sleep %d;echo %s;sleep %d;echo %s;sleep %d;echo %s;sleep %d;echo exit;) | telnet"

exp_config = cmmn.load_switch_measurement_config()


def start_experiment(exp_name='ocs'):
    # start receiver program
    cmd_tmp = "ssh %s@%s %s" % (
        remote_server_root_username, ip_receiver,
        cmd_start_receiver_fmt % (working_directory, '0x1989' if exp_name == 'ocs' else '0x1994', '1'))
    # print cmd_tmp
    ssh = subprocess.Popen(cmd_tmp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ssh.stdout.readlines(), ssh.stderr.readlines()
    time.sleep(1)

    # start OCS switching controller
    cmd_tmp = "ssh %s@%s %s" % (
        remote_server_username, ip_sender, cmd_start_ocs_sw if exp_name == 'ocs' else cmd_start_eps_sw)
    # print cmd_tmp
    ssh = subprocess.Popen(cmd_tmp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ssh.stdout.readlines(), ssh.stderr.readlines()
    time.sleep(5)

    # start sender program
    cmd_tmp = "ssh %s@%s %s" % (
        remote_server_root_username, ip_sender,
        cmd_start_sender_fmt % (working_directory, '0x1989' if exp_name == 'ocs' else '0x1994'))
    # print cmd_tmp
    ssh = subprocess.Popen(cmd_tmp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ssh.stdout.readlines(), ssh.stderr.readlines()
    time.sleep(1)

    # monitor the length of output file, if timeout, terminate everthing
    delay_filename = '%s/%s/%s-%s.csv' % (
        working_directory, exp_config['control_output_directory'], exp_config['control_output_filename'], exp_name)
    time_filename = '%s/%s/%s_%s.csv' % (
        working_directory, 'switch_controller/switch_measurement/eclipse/switch_measurement/Debug_receiver/', '1',
        'eth3')
    # print delay_filename
    # print time_filename

    filesize_tmp = '0'
    filesize_tmp_ = '-1'
    while filesize_tmp != filesize_tmp_:
        time.sleep(10)
        filesize_tmp = filesize_tmp_
        cmd_tmp = "ssh %s@%s %s" % (remote_server_root_username, ip_sender, 'ls -la ' + delay_filename)
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        alltmp = ssh.stdout.readlines()
        # print alltmp
        filesize_tmp_ = alltmp[0].split()[4]
        # print filesize_tmp_


def kill_programs(machines=[]):
    for ip_address in machines:
        cmd_tmp = "ssh %s@%s %s" % (
            remote_server_root_username, ip_address, cmd_kill_program_fmt % 'switch_measurement_sender')
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()

        cmd_tmp = "ssh %s@%s %s" % (remote_server_root_username, ip_address, cmd_kill_program_fmt % 'python')
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()

        cmd_tmp = "ssh %s@%s %s" % (
            remote_server_root_username, ip_address, cmd_kill_program_fmt % 'switch_measurement_receiver')
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()


def download_programs(machines=[]):
    for ip_address in machines:
        cmd_tmp = "ssh %s@%s %s" % (remote_server_username, ip_address, cmd_remove_code_fmt)
        # print cmd_tmp
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()

        cmd_tmp = "ssh %s@%s %s" % (remote_server_username, ip_address, cmd_get_code_fmt)
        # print cmd_tmp
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()


def compile_programs(machines=[]):
    for ip_address in machines:
        cmd_tmp = "ssh %s@%s %s" % (
            remote_server_username, ip_address, cmd_compile_tx_fmt % (working_directory, 'sender'))
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()

        cmd_tmp = "ssh %s@%s %s" % (
            remote_server_username, ip_address, cmd_compile_tx_fmt % (working_directory, 'receiver'))
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()


def disable_linkscan(epss=[]):
    for EPSedge in epss:
        cmd_tmp = cmd_disable_linkscan_fmt % (
            socket.inet_ntoa(struct.pack('!L', struct.unpack("!L", socket.inet_aton(eps_ip_base))[0] + EPSedge)), 1,
            '[EPS_USERNAME]', 1, '[EPS_PASSWORD]', 1, '/mnt/application/client_drivshell linkscan disable', 1)
        ssh = subprocess.Popen(cmd_tmp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print ssh.stdout.readlines()
        print ssh.stderr.readlines()


def transfer_config(machines=[]):
    for ip_address in machines:
        cmd_tmp = "scp %s %s@%s:%s" % (cmd_config_path % working_directory, remote_server_username, ip_address,
                                       cmd_config_path % working_directory)
        ssh = subprocess.Popen(cmd_tmp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ssh.stdout.readlines(), ssh.stderr.readlines()


def analyze_results(exp_name='ocs'):
    delay_filename = '%s/%s/%s-%s.csv' % (
        working_directory, exp_config['control_output_directory'], exp_config['control_output_filename'], exp_name)
    time_filename = '%s/%s/%s_%s.csv' % (
        working_directory, 'switch_controller/switch_measurement/eclipse/switch_measurement/Debug_receiver/', '1',
        'eth3')
    # analyze results
    cmd_tmp = "ssh %s@%s %s" % (remote_server_root_username, ip_sender, 'cat ' + delay_filename)
    ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    delays = ssh.stdout.readlines()
    # print ssh.stderr.readlines()

    cmd_tmp = "ssh %s@%s %s" % (remote_server_root_username, ip_receiver, 'cat ' + time_filename)
    ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    times = ssh.stdout.readlines()
    # print ssh.stderr.readlines()
    #
    # pprint.pprint(delays)
    # pprint.pprint(times)

    change_time = [0.0 + int(a.split(',')[2]) + int(a.split(',')[3]) * 1.0 / 1000000 for a in times if
                   a.split(',')[0] == 's']
    finish_time = [0.0 + int(a.split(',')[2]) + int(a.split(',')[3]) * 1.0 / 1000000 for a in times if
                   a.split(',')[0] == 'e']
    command_time = [0.0 + int(d.strip().split(',')[0]) + int(d.strip().split(',')[1]) * 1.0 / 1000000 for d in delays]

    # pprint.pprint(command_time)
    # pprint.pprint(change_time)
    # pprint.pprint(finish_time)

    align = 0
    for i in range(len(command_time)):
        if change_time[0] - command_time[i] < 1.0:
            align = i
            break
    # print align
    command_time = command_time[align:align + len(change_time)]
    # print len(command_time), len(change_time), len(finish_time)

    software_delay = [1000.0 * (change_time[i] - command_time[i]) for i in range(len(command_time))]
    hardware_delay = [1000.0 * (finish_time[i] - change_time[i]) for i in range(len(command_time))]

    return software_delay, hardware_delay


ip_sender = cmmn.convert_node_to_ip(exp_config.sender)
ip_receiver = cmmn.convert_node_to_ip(exp_config.receiver)
ocs_results = []
eps_results = []

# reboot EPSes, including the related edge EPSes and the core EPS
EPSedge_l = []
EPSID_core = 0
EPSID_edge_sender = exp_config.sender / 8 + 1
EPSID_edge_receiver = exp_config.receiver / 8 + 1
EPSedge_l.append(EPSID_edge_sender)
if EPSID_edge_sender != EPSID_edge_receiver:
    EPSedge_l.append(EPSID_edge_receiver)
raw_input(
    "Reboot core EPS %s and edge EPS %s by typing \"reboot\" in the management console\nPress any key to continue..." % (
        EPSID_core, EPSedge_l))
raw_input("On core EPS %s, set <controller ip> to %s, and save the change\nPress any key to continue..." % (
    EPSID_core, cmmn.convert_node_to_ip(exp_config.sender)))

# # kill all python and switch_measurement program on sender, receiver, controller
kill_programs(machines=[ip_sender, ip_receiver, ip_controller])

# # get file on remote servers (sender, receiver)
download_programs(machines=[ip_sender, ip_receiver])

# # compile sender and receiver
compile_programs(machines=[ip_sender, ip_receiver])

time.sleep(3)

# start EPS controller that configures initial setting of EPS
cmd_tmp = "ssh %s@%s %s" % (remote_server_username, ip_controller, cmd_start_eps_ctrl)
ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# print ssh.stdout.readlines(), ssh.stderr.readlines()

for exp_name in measurement:
    if exp_name == 'ocs':

        # start OCS controller that configure initial setting of OCS
        cmd_tmp = "ssh %s@%s %s" % (remote_server_username, ip_controller, cmd_start_ocs_ctrl)
        ssh = subprocess.Popen(cmd_tmp.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print ssh.stdout.readlines(), ssh.stderr.readlines()

        # please disable link scan...
        # raw_input(
        #     "Disable link scan on edge EPS %s(command: /mnt/application/client_drivshell linkscan disable)\nPress any key to continue..." % (
        #         EPSedge_l))

        disable_linkscan(EPSedge_l)

        for cc in ocs_concurrent:
            exp_config_json = {"num_concurrent": cc}
            with open(cmd_config_path % working_directory, 'w') as fp:
                json.dump(exp_config_json, fp)
            time.sleep(1)
            transfer_config(machines=[ip_sender, ip_receiver, ip_controller])
            # load configure file on servers
            time.sleep(1)
            start_experiment(exp_name='ocs')
            time.sleep(1)
            kill_programs(machines=[ip_sender, ip_receiver])
            time.sleep(1)
            sd, hd = analyze_results(exp_name='ocs')
            time.sleep(1)
            ocs_results.append((sd, hd))
            print "device: %s," % exp_name, "concurrency: %d," % cc, "software delay (avg): %0.3f ms," % (
                sum(sd) / len(sd)), "hardware delay (median): %0.3f ms" % (np.median(np.array(hd)))
    elif exp_name == 'eps':
        time.sleep(1)
        start_experiment(exp_name='eps')
        time.sleep(1)
        kill_programs(machines=[ip_sender, ip_receiver])
        time.sleep(1)
        sd, hd = analyze_results(exp_name='eps')
        time.sleep(1)
        eps_results.append((hd, sd))
        print "device: %s," % exp_name, "software delay (avg): %0.3f ms," % (
            sum(sd) / len(sd)), "hardware delay (median): %0.3f ms" % (
            np.median(np.array(hd)))

kill_programs(machines=[ip_sender, ip_receiver, ip_controller])

# pprint.pprint(ocs_results)
# pprint.pprint(eps_results)
software_delay = []
hardware_delay = []
for sd, hd in ocs_results:
    # print sd, hd
    software_delay.append(sd)
    hardware_delay.append(hd)
draw_boxplot(ocs_concurrent, software_delay, 'Number of concurrent connection reconfigurations',
             'OCS software delay ($m$s)', grid=True, name="./ocs_soft")
draw_boxplot(ocs_concurrent, hardware_delay, 'Number of concurrent connection reconfigurations',
             'OCS hardware delay ($m$s)', grid=True, name="./ocs_hard")
draw_boxplot([""], eps_results[0][0], '',
             'EPS software delay ($m$s)', ylim=1.5, name="./eps_soft")
draw_boxplot([""], eps_results[0][1], '',
             'EPS hardware delay ($m$s)', ylim=1.5, name="./eps_hard")
