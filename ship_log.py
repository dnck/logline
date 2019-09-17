import argparse
import time
import threading
import socket
import json
import sys

if sys.version_info.major > 2:
    from queue import Queue
else:
    from Queue import Queue

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
        postdata = broadcast_queue.get(timeout=10000.0)
        if postdata:
            _send_datagram(host, port, postdata, node_name)

def _send_datagram(host, port, postdata, node_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(
        json.dumps(node_name+postdata).encode(),
        (host, port)
    )

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description='Log line shipper.'
    )
    PARSER.add_argument('-fname',
        metavar='fname', type=str, default='',
        help='Full path and filename of the log to tail and ship to server'
    )
    PARSER.add_argument('-host',
        metavar='port', type=str, default='127.0.0.1',
        help='The log server public IP where we ship to'
    )
    PARSER.add_argument('-port',
        metavar='port', type=int, default=5222,
        help='The log server port where we ship to'
    )
    PARSER.add_argument('-node_name',
        metavar='node_name', type=str, default='',
        help='The name of the node to prepend to the log lines'
    )

    args = PARSER.parse_args()

    if not (args.node_name == ""):
        args.node_name = args.node_name + " | "

    broadcast_queue = Queue()

    send_to_queue_thread = threading.Thread(
        target=trail_log, args = (broadcast_queue, args.fname,)
    )

    broadcast_to_receiver_thread = threading.Thread(
        target=get_from_queue,
        args = (broadcast_queue, args.host, args.port, args.node_name)
    )

    send_to_queue_thread.start()

    broadcast_to_receiver_thread.start()
