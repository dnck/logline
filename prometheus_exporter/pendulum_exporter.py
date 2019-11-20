# -*- coding: utf-8 *-*
"""
A Prometheues exporter for the Helix Network pendulum
node application logs.
"""
import argparse
import results_manager
import time
import threading
import sys
import re

from prometheus_client import start_http_server, Gauge

from context import telegram_notifier

from queue import Queue

NODE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9._]+")

API_REQUEST_METRICS = [
    '{}_addNeighbors', '{}_getNodeInfo', '{}_attachToTangle',
    '{}_broadcastTransactions', '{}_getBalances', '{}_getInclusionStates',
    '{}_getNeighbors', '{}_getNodeAPIConfiguration', '{}_getTips',
    '{}_getTransactionsToApprove', '{}_getTransactionStrings',
    '{}_interruptAttachingToTangle', '{}_removeNeighbors',
    '{}_storeTransactions', '{}_getMissingTransactions', '{}_checkConsistency',
    '{}_wereAddressesSpentFrom', '{}_findTransactions'
]

X_CLASS_METRICS = [
    '{}_toProcess', '{}_toBroadcast', '{}_toRequest', '{}_toReply',
    '{}_totalTransactions', '{}_tailsTraversed', '{}_solid', '{}_nonSolid',
    '{}_dnsCheck', '{}_milestoneValid', '{}_solidMilestoneChange',
    '{}_syncCheck', '{}_nodeStoredTx', '{}_apiStoredTx',
    '{}_invalidTimestamp', "{}_inconsistentBalance", "{}_broadcastedTx",
    "{}_receivedTxvm"
]

STOP_SIGNAL = Queue()

EXPORTER_QUEUE = Queue()


class LogTailer(threading.Thread):
    """
    """
    def __init__(self, name, thread_id, fname, logger):
        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.fname = fname
        self.log = logger

    def run(self):
        """
        This method implements the run logic of the thread.
        """
        self.log.info("Tailing logfile.")
        log_file = self.tail()
        sleep_time = 1.0
        while True:
            line = log_file.readline()
            if not line and STOP_SIGNAL.empty():
                continue
            else:#logtailer received a stop signal from the exporter.
                self.log.info("Stopped tailing.")
                sys.exit(1)
            line = line.strip()
            EXPORTER_QUEUE.put(line)

    def tail(self):
        log_file = open(self.fname, "r")
        log_file.seek(0, 2)  # Go to the end of the file
        return log_file

class PendulumExporter(threading.Thread):
    """
    """
    def __init__(self, name, thread_id, logger):
        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.log = logger
        self.known_nodes = []
        self.node_metrics = {}

    def start_tracking_nodes_metrics(self, node_name):
        try:
            if node_name not in self.known_nodes:
                self.known_nodes.append(node_name)
                self.node_metrics.update(
                    self.construct_metrics(
                        node_name,
                        API_REQUEST_METRICS,
                        X_CLASS_METRICS
                    )
                )
        except:
            self.log.exception("start_tracking_nodes_metrics error:")
            sys.exit(1)


    def construct_metrics(
                            self,
                            node_name,
                            API_REQUEST_METRICS,
                            X_CLASS_METRICS
                        ):
        """
        Return a dictionary for exporting to prometheus
            {
            node_node: {
                metric_name: {
                    Gauge(node_name_metric_name)
                }
            }
        }
        """
        try:
            metrics = {
                node_name: {
                    metric[3:]: Gauge(metric.format(node_name), 'api metrics')
                        for metric in API_REQUEST_METRICS
                }
            }
        except:
            self.log.exception("construct_metrics error A:")
        try:
            for metric in X_CLASS_METRICS:
                metrics[node_name].update(
                    {
                        metric[3:]:
                        Gauge(metric.format(node_name), 'class metrics')
                    }
                )
        except:
            self.log.exception("construct_metrics error B:")
        return metrics


    def match_api_request(self, node_name, line):
        try:
            for metric in API_REQUEST_METRICS:
                if re.search(metric[3:], line):
                    self.inc_class_metric(node_name, metric[3:])
                    return (metric[3:], 1)
        except:
            self.log.exception("match_api_request error:")
        return None


    def match_x_class(self, node_name, line):
        try:
            if re.search("Stored_txhash", line):
                if re.search("API", line):
                    self.inc_class_metric(node_name, "apiStoredTx")
                    return ("apiStoredTx", 1)
                else:
                    inc_class_metric(node_name, "nodeStoredTx")
                    return ("nodeStoredTx", 1)
        except:
            self.log.exception("error:")

        try:
            if re.search("totalTransactions", line):
                rstats = self.set_rstat_metrics(node_name, line)
                return ("rstats", rstats)
        except:
            self.log.exception("error:")

        try:
            if re.search("Broadcasted_txhash", line):
                self.inc_class_metric(node_name, "broadcastedTx")
                return ("broadcastedTx", 1)
        except:
            self.log.exception("error:")

        try:
            if re.search("Received_txvm", line):
                self.inc_class_metric(node_name, "receivedTxvm")
                return ("receivedTxvm", 1)
        except:
            self.log.exception("error:")


        try:
            if re.search("traversed", line):
                ntails =\
                    int(
                        line.split(
                            " tails traversed to find tip")[0].split('- ')[1]
                        )
                self.set_class_metric(node_name, "tailsTraversed", ntails)
                return ("tailsTraversed", 1)
        except:
            self.log.exception("error:")

        try:
            if re.search("#Solid/NonSolid", line):
                solid, non_solid = \
                    [int(i) for i in line.split(
                        "#Solid/NonSolid: ")[1].split('/')
                    ]
                self.set_class_metric(node_name, 'solid', solid)
                self.set_class_metric(node_name, 'nonSolid', non_solid)
                return ("Solid/NonSolid", (solid, non_solid))
        except:
            self.log.exception("error:")

        try:
            if re.search("DEBUG MilestoneTrackerImpl:391 - Milestone ", line):
                if re.search("VALID", line):
                    self.inc_class_metric(node_name, "milestoneValid")
                    return ("milestoneValid", 1)
                return None
        except:
            self.log.exception("error:")

        try:
            if re.search("[generating solid entry points]: 100.00%", line):#snapshot
                self.inc_class_metric(node_name, "snapShot")
                return ("snapShot", 1)
        except:
            self.log.exception("error:")

        try:
            if re.search("DNS Checker", line):
                self.inc_class_metric(node_name, "dnsCheck")
                return ("dnsCheck", 1)
        except:
            self.log.exception("error:")

        try:
            if re.search("balance is not consistent", line):
                if re.search("Validation failed:", line):
                    self.inc_class_metric(node_name, "inconsistentBalance")
                    return ("inconsistentBalance", 1)
                return None
        except:
            self.log.exception("error:")

        try:
            if re.search("Invalid transaction timestamp", line):
                self.inc_class_metric(node_name, "invalidTimestamp")
                return ("invalidTimestamp", 1)
        except:
            self.log.exception("error:")

        try:
            if re.search("Sync check = ", line):
                sync_check = (line.split("Sync check = ")[-1])
                self.set_class_metric(node_name, "syncCheck", sync_check)
                return ("syncCheck", sync_check)
        except:
            self.log.exception("error:")

        return None


    def inc_class_metric(self, node_name, metric):
        """metric should be a string in the node's metrics dictionary"""
        try:
            self.node_metrics[node_name][metric].inc()
        except:
            self.log.exception("error:")


    def set_class_metric(self, node_id, metric, val):
        """metric should be a string in the node's metrics dictionary"""
        try:
            self.node_metrics[node_id][metric].set(val)
        except:
            self.log.exception("error:")


    def set_rstat_metrics(self, node_name, line):
        try:
            rstats = self.parse_rstats(line) # rstats is tuple where idx is val
        except:
            self.log.exception("error:")
        try:
            self.set_class_metric(
                node_name, 'toProcess', rstats[0]
            )
        except:
            self.log.exception("error:")
        try:
            self.set_class_metric(
                node_name, 'toBroadcast', rstats[1]
            )
        except:
            self.log.exception("error:")
        try:
            self.set_class_metric(
                node_name, 'toRequest', rstats[2]
            )
        except:
            self.log.exception("error:")
        try:
            self.set_class_metric(
                node_name, 'toReply', rstats[3]
            )
        except:
            self.log.exception("error:")
        try:
            self.set_class_metric(
                node_name, 'totalTransactions', rstats[4]
            )
        except:
            self.log.exception("error:")
        return rstats


    def parse_rstats(self, line):
        try:
            line = line.split("= ")
            toProcess = int(line[1].split(' ')[0])
            toBroadcast = int(line[2].split(' ')[0])
            toRequest = int(line[3].split(' ')[0])
            toReply = int(line[4].split(' ')[0])
            totalTransactions = int(line[5])
        except:
            self.log.exception("error:")
        return (toProcess, toBroadcast, toRequest, toReply, totalTransactions)


    def match_and_set_node_metric(self, node_name, line):
        try:
            result = self.match_api_request(node_name, line)
        except:
            self.log.exception("error:")
        if result:
            return result
        else:
            try:
                result = self.match_x_class(node_name, line)
            except:
                self.log.exception("error:")
            if result:
                return result
        return None


    def run(self):
        while True:
            try:
                line = EXPORTER_QUEUE.get(timeout=120.0)
            except:
                STOP_SIGNAL.put(True)
                self.log.exception("error:")
                sys.exit(1)
            try:
                if line:
                    # we match the start of the line for snake_case node_names
                    node = re.match(NODE_NAME_PATTERN, line)
                    if node:
                        node_name = node.group(0)
                        # does nothing if we already are tracking
                        self.start_tracking_nodes_metrics(node_name)
                        result = self.match_and_set_node_metric(
                                                                node_name, line
                                                                )
                        if result:
                            if result[1] == 1 and not (result[0]=="syncCheck"):
                                self.log.info("Incremented {} for {}".format(
                                    result[0], node_name)
                                )
                            else:
                                self.log.info("Set {} for {} to {}".format(
                                    result[0], node_name, result[1])
                                )
            except:
                self.log.exception("error:")



if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(description='Log scrapper.')

    PARSER.add_argument(
        '-fname',
        metavar='fname',
        type=str,
        default='/home/ubuntu/logline/logs/testnet.log',
        help='Log file to scrap'
    )
    PARSER.add_argument(
        '-server_port',
        metavar='server_port',
        type=int,
        default=9111,
        help='Port to push the metrics to.'
    )

    ARGS = PARSER.parse_args()

    NOTIFIER = telegram_notifier.NotificationHandler()

    LOGGER = results_manager.LogManager(level="debug", output="file",
        filename="pendulum_export_"+str(ARGS.server_port)+".log")

    start_http_server(ARGS.server_port)

    TAIL = LogTailer("LogTailer", 1, ARGS.fname, LOGGER)
    EXPORT = PendulumExporter("PendulumExporter", 2, LOGGER)

    # Start new Threads
    TAIL.start()
    EXPORT.start()

    EXPORT.join()

    TAIL.join()

    NOTIFIER.emit(
        "ALERT! Stopped exporting pendulum metrics from {}".format(ARGS.fname)
    )
