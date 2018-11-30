from ryu import cfg
import time
import json
import requests


def load_switch_measurement_config(configure_file="./switch_controller/switch_measurement/switch_measurement.json"):
    CONF = cfg.CONF
    CONF.register_opts([
        cfg.StrOpt('cluster_configuration', default="./conf/cluster_conf.json"),
        cfg.StrOpt('rule_template_directory', default="./switch_controller/quanta/config/te_test/"),
        cfg.IntOpt('sender', default=36),
        cfg.IntOpt('receiver', default=32),
        cfg.IntOpt('transceiver_speed', default=10),
        cfg.IntOpt('num_reconfig', default=50),
        cfg.IntOpt('reconfig_interval', default=3),
        # cfg.IntOpt('notify_port', default=10033),
        cfg.IntOpt('num_concurrent', default=20),
        cfg.StrOpt('control_output_directory', default='./switch_controller/switch_measurement/switching_record/'),
        cfg.StrOpt('control_output_filename', default='./switching_time'),
        # cfg.StrOpt('testing_switch', default='eps')
    ])
    CONF_file = json.load(open(configure_file))

    for config in CONF_file.keys():
        CONF.__setattr__(config, CONF_file[config])

    return CONF


def convert_node_to_ip(node, prefix="[RESEARCH_NETWORK_PREFIX]."):
    suffix = int(node) + 111
    return prefix + str(suffix)


def get_time_of_day():
    record_time = time.time()
    sec = int(record_time)
    usec = int((record_time % 1) * 1000 * 1000)
    return sec, usec


def switching_notify(ip, port):
    record_url_fmt = 'http://%s:%d/nofity/record'
    record_request_fmt = '{\"sec\":%d,\"usec\":%d}'
    sec, usec = get_time_of_day()
    record_url = record_url_fmt % (ip, port)
    record_request = record_request_fmt % (sec, usec)
    return requests.post(record_url, json=json.loads(record_request))


cnd = load_switch_measurement_config()
