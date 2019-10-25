# -*- coding: utf-8 *-*
"""
A log shipper that tails a file and sends new lines to the log server.
"""
import argparse
import threading
import socket
import os
import time
import sys
import json

from queue import Queue

from prometheus_exporter import results_manager

from alert_utilities import telegram_notifier


BROADCAST_QUEUE = Queue()
STOP_SIGNAL = Queue()

logger = results_manager.LogManager(level="debug", output="file",
                                         filename="shipper.log")


class LogTailer(threading.Thread):
    """
    Class to manage a thread that tails the newest log file in the log dir.
    If the log file changes, then this class will grab a hold of it, and
    start tailing it, and sending the lines into a shared queue.
    The threaded sister class LineShipper grabs messages from the shared queue
    and sends them to the central server. If the LineShipper puts a message in
    the shared STOP_SIGNAL queue, then this class (LogTailer) will shut down.
    A notification of the shutdown is sent to telegram.
    """
    def __init__(self, name, thread_id, log_dir):
        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.log_dir = log_dir

    def run(self):
        """
        This method implements the run logic of the thread.
        """
        logger.info("Tailing logfile.")
        fname, LOG_FILE_0 = self.tail()
        sleep_time = 1.0
        while True:
            line = fname.readline()
            if not line:
                # check for new log file
                fname, LOG_FILE_1 = self.tail()
                if LOG_FILE_0 != LOG_FILE_1:
                    LOG_FILE_0 = LOG_FILE_1
                else: # sleep for a bit if there was not a log file change
                    time.sleep(sleep_time)
                    if STOP_SIGNAL.empty():
                        continue
                    else:
                        logger.info("Stopped tailing.")
                        sys.exit(1)
            else:
                line = line.rstrip()
                BROADCAST_QUEUE.put(line)

    def tail(self):
        LOG_FILE = self.get_log_file()
        fname = open(LOG_FILE, "r")
        fname.seek(0, 2)  # Go to the end of the file
        return fname, LOG_FILE

    def get_log_file(self):
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
        if len(current_log_files) > 0:
            # the modification times of the logs
            f_mod_times = {os.stat(i).st_mtime: i for i in current_log_files}
            # newest file
            new_file_key = max(list(f_mod_times.keys()))
            return f_mod_times[new_file_key]
        else:
            logger.info("No log files found. Shutting down.")
        sys.exit(1)  # will throw a horrible error when the file isn't there


class LineShipper(threading.Thread):
    """
    Class to handle sending loglines from the shared queue to the server.
    If no lines are in the queue for a default of 1 hour, then this threaded
    class will shutdown and send a shutdown signal to its sister class,
    the LogTailer. Loglines from the queue are appended with a identifier,
    node_name like so, 'node_node | LOGLINE'.
    """
    def __init__(self, name, thread_id, host, port):
        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.host = host
        self.port = port
        self.node_name = "{} | ".format(name)

    def run(self):
        logger.info("Shipping loglines.")
        while True:
            try:
                postdata = BROADCAST_QUEUE.get(timeout=60*60)
                if postdata:
                    self._send_datagram(postdata)
            except Exception as e:
                print(e)
                STOP_SIGNAL.put(True)
                logger.info("Stopped shipping.")
                sys.exit(1)

    def _send_datagram(self, postdata):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(self._encode_logline(postdata), (self.host, self.port))
        # print("Sent data {}".format(self._encode_logline(postdata)))

    def _encode_logline(self, postdata):
        return json.dumps(self.node_name + postdata).encode()


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser(description="Log line shipper.")
    PARSER.add_argument(
        "log_dir",
        metavar="log_dir",
        type=str,
        help="Full path and filename of the log to tail and ship to server",
    )
    PARSER.add_argument(
        "-host",
        metavar="port",
        type=str,
        default="127.0.0.1",
        help="The log server public IP where we ship to",
    )
    PARSER.add_argument(
        "-port",
        metavar="port",
        type=int,
        default=5222,
        help="The log server port where we ship to",
    )
    PARSER.add_argument(
        "-node_name",
        metavar="node_name",
        type=str,
        default="default",
        help="The name of the node to prepend to the log lines",
    )

    ARGS = PARSER.parse_args()
    NOTIFIER = telegram_notifier.NotificationHandler()

    # Create new threads
    TAIL = LogTailer("LogTailer", 1, ARGS.log_dir)
    SHIP = LineShipper(ARGS.node_name, 2, ARGS.host, ARGS.port)

    # Start new Threads
    TAIL.start()
    SHIP.start()

    SHIP.join()
    #logger.info("Finished ship thread.")
    TAIL.join()
    #logger.info("Finished tail thread.")
    #logger.info("Exiting program.")
    NOTIFIER.emit(
        "ALERT! {} stopped shipping log lines!".format(ARGS.node_name)
    )
