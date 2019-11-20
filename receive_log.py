# -*- coding: utf-8 *-*
"""
A simple UDP server that writes loglines to file.

You should firewall this server!

On Linux OS, this is simple with sbin/iptables. E.g.

    sudo iptables -A INPUT -p udp --dport 6222 -s 192.168.60.9 -j ACCEPT
    sudo iptables -A INPUT -p udp --dport 6222 -j DROP

The above would only accept udp packets received on port 6222 from IP
192.168.60.9. Adapt to your circumstances. Note that this won't prevent
attacks where someone spoofs their own IP. But, they would then need to know
the IP that you're accepting traffic from. So, best keep that secret as well.
"""
import argparse
import socket
import sys
import threading
import json

from queue import Queue

from prometheus_exporter import results_manager
from alert_utilities import telegram_notifier

MAX_BYTES = 65535

LINE_QUEUE = Queue()

LOGGER = results_manager.LogManager(
                                    level="debug",
                                    output="file",#is saved in the ./var/log
                                    filename="server.log"# as this filename
                                    )

class LineWriter(threading.Thread):
    def __init__(self, name, thread_id, fname):
        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.fname = fname
        LOGGER.info("Starting {}".format(self.name))

    def run(self):
        while True:
            try:
                logline = LINE_QUEUE.get(timeout=120.0)#seconds
                with open(self.fname, "a") as f:
                    f.write(logline+'\n')
            except:
                LOGGER.info("Exiting {}".format(self.name))
                sys.exit(1)

class LogServer(threading.Thread):
    def __init__(self, name, thread_id, host, port):
        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.host = host
        self.port = port
        LOGGER.info("Starting {}".format(self.name))

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(120.0)
        sock.bind((self.host, self.port))
        print('Server listening at {}'.format(sock.getsockname()))
        while True:
            try:
                received_bytes, address = sock.recvfrom(MAX_BYTES)
                client_data = json.loads(received_bytes.decode())
                LINE_QUEUE.put(client_data)
            except:
                LOGGER.info("Exiting {}".format(self.name))
                sys.exit(1)


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description='Log server.'
    )
    PARSER.add_argument('-host',
                        metavar='host',
                        type=str,
                        default='127.0.0.1',
                        help='The log server public IP'
                        )
    PARSER.add_argument('-port',
                        metavar='port',
                        type=int,
                        default=5222,
                        help='The port where we listen'
                        )
    PARSER.add_argument('-fname',
                        metavar='fname',
                        type=str,
                        default="/home/ubuntu/logline/logs/testnet.log",
                        help='Full path to central log file.'
                        )

    ARGS = PARSER.parse_args()

    SERVER = LogServer(
        "LogServer_{}".format(ARGS.port), 1, ARGS.host, ARGS.port
    )
    LINE_WRITER = LineWriter(
        "LineWriter_{}".format(ARGS.port), 2, ARGS.fname
    )

    #Start new Threads
    SERVER.start()
    LINE_WRITER.start()

    SERVER.join()
    LINE_WRITER.join()

    NOTIFIER.emit(
        "ALERT! Log Server -p {} stopped receiving log lines!".format(
            ARGS.port
        )
    )
