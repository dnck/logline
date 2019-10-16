import argparse
import time
import threading
import socket
import json
import os
import sys
import datetime

from dotenv import load_dotenv

from alert_utilities import telegram_notifier

if sys.version_info.major > 2:
    from queue import Queue
else:
    from Queue import Queue


PY_DIRNAME, PY_FILENAME = os.path.split(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(PY_DIRNAME)
ENV_FILE = os.path.join(PROJECT_ROOT_DIR, ".env")
load_dotenv(dotenv_path=ENV_FILE)

LOG_DIRECTORY = os.environ.get("LOG_DIRECTORY")
RECEIVER_HOST = os.environ.get("RECEIVER_HOST")
RECEIVER_PORT = os.environ.get("RECEIVER_PORT")
NODE_NAME = os.environ.get("NODE_NAME")

notifier = telegram_notifier.NotificationHandler()


def trail_log(broadcast_queue, fname):
    with open(fname, 'r') as fname:
        fname.seek(0,2) # Go to the end of the file
        while True:
            line = fname.readline()
            if not line:
                time.sleep(0.1) # Sleep briefly
                continue
            line = line.rstrip()
            broadcast_queue.put(line)


def send_datagram(broadcast_queue, host, port, node_name):
    while True:
        try:
            postdata = broadcast_queue.get(timeout=120.0)
        except Queue.Empty:
            notifier.emit(
                "ALERT!! {} has stopped shipping log lines!".format(node_name)
                )
        if postdata:
            _send_datagram(host, port, postdata, node_name)


def _send_datagram(host, port, postdata, node_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(
        json.dumps(node_name+" | "+postdata).encode(),
        (host, port)
    )


def dtobj_from_str(time_string):
    """Get a datetime object from an appropriately formatted string."""
    dt_obj = datetime.datetime.strptime(
        time_string, "%Y-%m-%d-%H-%M-%S"
    )
    return dt_obj


if __name__ == '__main__':

    log_files = {
        dtobj_from_str(s.split("log-")[1][:19]): \
            s for s in os.listdir(LOG_DIRECTORY)
    }
    sorted_log_files = sorted(list(log_files.keys()))
    fname = os.path.join(LOG_DIRECTORY, log_files[sorted_log_files[-1]])

    broadcast_queue = Queue()

    send_to_queue_thread = threading.Thread(
        target=trail_log, args = (broadcast_queue, fname,)
    )

    broadcast_to_receiver_thread = threading.Thread(
        target=send_datagram,
        args = (broadcast_queue, RECEIVER_HOST, RECEIVER_PORT, NODE_NAME,)
    )

    send_to_queue_thread.start()

    broadcast_to_receiver_thread.start()
