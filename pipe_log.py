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

def broadcast_client(host, port, postdata):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    send_bytes = json.dumps(postdata).encode()
    #print("Sending lines...")
    sock.sendto(send_bytes, (host, port))

def send_to_queue(broadcast_queue, lines):
    broadcast_queue.put(lines)

def get_from_queue(broadcast_queue, host, port):
    while True:
        postdata = broadcast_queue.get(timeout=10000.0)
        if len(postdata):
            broadcast_client(host, port, postdata)

def trail_log(broadcast_queue):
    for line in sys.stdin:
        lines = line.rstrip()
        send_to_queue(broadcast_queue, lines)

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description='Log line shipper for piping from docker-compose logs.'
    )
    PARSER.add_argument('-host',
        metavar='port', type=str, default='127.0.0.1',
        help='The log server public IP where we ship to'
    )
    PARSER.add_argument('-port',
        metavar='-port', type=int, default=5222,
        help='The log server port where we ship to'
    )

    args = PARSER.parse_args()

    broadcast_queue = Queue()

    send_to_queue_thread = threading.Thread(
        target=trail_log, args = (broadcast_queue,)
    )

    broadcast_to_receiver_thread = threading.Thread(
        target=get_from_queue,
        args = (broadcast_queue, args.host, args.port)
    )

    send_to_queue_thread.start()

    broadcast_to_receiver_thread.start()
