import argparse
import time
import threading
import socket
import json
import os
import sys
import datetime

from alert_utilities import telegram_notifier

from prometheus_exporter import results_manager

if sys.version_info.major > 2:
    from queue import Queue
else:
    from Queue import Queue


class LogShipper:

    def __init__(self, log_dir, host, port, node_name):

        self.logger = results_manager.LogManager(level="debug", output="file",
                                                 filename="shipper.log"
                                                )
        self.notifier = telegram_notifier.NotificationHandler()
        self.host = host
        self.port = port
        self.node_name = "{} | ".format(node_name)
        self.broadcast_queue = Queue()
        self.log_dir = log_dir
        self.log_file = self.observe_dir()
        self.new_log_file = self.observe_dir()


    def trail_log(self):
        with open(self.log_file, 'r') as fname:
            fname.seek(0,2) # Go to the end of the file
            while True:
                line = fname.readline()
                if not line:
                    self.new_log_file = self.observe_dir()
                    if self.log_file  == self.new_log_file:
                        time.sleep(0.1) # Sleep briefly
                        continue
                    else:
                        # the thread will stop, and we need to restart it
                        self.log_file = self.new_log_file
                        return None
                line = line.rstrip()
                self.broadcast_queue.put(line)


    def send_datagram(self):
        while True:
            try:
                postdata = self.broadcast_queue.get(timeout=120.0)
            except Exception:
                self.logger.debug(
                    "There were no lines in the broadcast queue!"
                    )
                self.notifier.emit(
                    "ALERT!! {} has stopped shipping log lines!".format(self.node_name.replace(" | ", ""))
                    )
                trail_log_thread = threading.Thread(target=self.trail_log)
                trail_log_thread.start()
            if postdata:
                self._send_datagram(postdata)


    def _send_datagram(self, postdata):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(self.encode_logline(postdata), (self.host, self.port))

    def encode_logline(self, postdata):
        return json.dumps(self.node_name+postdata).encode()


    def observe_dir(self):
        """
        Watch the log directory for changes.

        If there's a new log file, stop shipping from the old log,
        and start shipping from the new log.

        If there's no change, don't do anything.
        """
        # the current log filenames
        current_log_files = [
            os.path.join(os.path.abspath(self.log_dir), i)
            for i in os.listdir(self.log_dir)
            if i.endswith(".log")
        ]
        # the modification times of the logs
        f_mod_times = {os.stat(i).st_mtime: i for i in current_log_files}
        # newest file
        new_file_key = max(list(f_mod_times.keys()))
        return f_mod_times[new_file_key]


if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description='Log line shipper.'
    )
    PARSER.add_argument('log_dir',
        metavar='log_dir', type=str, default='',
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

    ARGS = PARSER.parse_args()

    shipper = LogShipper(ARGS.log_dir, ARGS.host, ARGS.port, ARGS.node_name)

    trail_log_thread = threading.Thread(target=shipper.trail_log)

    send_log_line_thread = threading.Thread(target=shipper.send_datagram)

    trail_log_thread.start()

    send_log_line_thread.start()
