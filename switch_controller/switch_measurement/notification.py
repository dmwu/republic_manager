#!/usr/bin/python
import sys

import time

sys.path.insert(0, '/home/[SERVER_USERNAME]/github/republic_manager/')
import signal
import sys
import time
import os

import argparse
from flask import Flask
from flask import request

from switch_controller.switch_measurement.common import get_time_of_day

# setup signal processing handler


app = Flask(__name__)

parser = argparse.ArgumentParser(description="Do something.")
parser.add_argument('-i', '--ip', type=str, default='0.0.0.0', required=False, help="IP address of controller")
parser.add_argument('-p', '--port', type=int, default=10033, required=False, help="Port listening to")
parser.add_argument('-d', '--directory', type=str, default='./switching_record/', required=False,
                    help="Directory to output")
parser.add_argument('-f', '--filename', type=str, default='./switching_time.csv', required=False,
                    help="Filename of output")
args = parser.parse_args()

if not os.path.exists(args.directory):
    os.makedirs(args.directory)
file_output = open(args.directory + '/' + args.filename, 'w')


def signal_handler(signum, frame):
    print('You pressed Ctrl+C!')
    file_output.flush()
    file_output.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@app.route('/')
def api_root():
    return 'Welcome'


@app.route('/nofity/record', methods=['POST'])
def api_fiber_ent_crs():
    sec, usec = get_time_of_day()
    if request.headers['Content-Type'] == 'application/json':
        if ("sec" in request.json and "usec" in request.json):
            controller_sec = request.json["sec"]
            controller_usec = request.json["usec"]
            file_output.write("%d, %d, %d, %d\n" % (sec, usec, controller_sec, controller_usec))
        else:
            file_output.write("%d, %d\n" % (sec, usec))
    else:
        raise Exception('spam', 'eggs')
    return "\n"


def main():
    # start server
    print args.ip, args.port
    app.run(host=args.ip, port=args.port, debug=False)


if __name__ == '__main__':
    main()
