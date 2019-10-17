import argparse
import results_manager
import time
import threading
import sys
import re
from prometheus_client import start_http_server, Gauge

if sys.version_info.major > 2:
    from queue import Queue
else:
    from Queue import Queue

SCRIPT_DIRNAME, SCRIPT_FILENAME = os.path.split(os.path.abspath(__file__))

NODE_METRICS = {}

KNOWN_NODES = []

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
    '{}_invalidTimestamp', "{}_inconsistentBalance"
]

def start_tracking_nodes_metrics(node_name):
    if node_name not in KNOWN_NODES and len(KNOWN_NODES) < 20:
        KNOWN_NODES.append(node_name)
        NODE_METRICS.update(
            construct_metrics(
                node_name,
                API_REQUEST_METRICS,
                X_CLASS_METRICS
            )
        )


def construct_metrics(node_name, API_REQUEST_METRICS, X_CLASS_METRICS):
    """
    Return a dictionary for use exporting to prometheus
        {
        node_node: {
            metric_name: {
                Gauge(node_name_metric_name)
            }
        }
    }
    """
    metrics = {
        node_name: {
            metric[3:]: Gauge(metric.format(node_name), 'api metrics')
                for metric in API_REQUEST_METRICS
        }
    }
    for metric in X_CLASS_METRICS:
        metrics[node_name].update(
            {metric[3:]: Gauge(metric.format(node_name), 'class metrics')}
        )
    return metrics


def match_api_request(node_name, line):
    for metric in API_REQUEST_METRICS:
        if re.search(metric[3:], line):
            inc_class_metric(node_name, metric[3:])
            return (metric[3:], 1)
    return None


def match_x_class(node_name, line):
    if re.search("API:602 - Stored_txhash", line):
        inc_class_metric(node_name, "apiStoredTx")
        return ("apiStoredTx", 1)

    if re.search("Node:474 - Stored_txhash", line):
        inc_class_metric(node_name, "nodeStoredTx")
        return ("nodeStoredTx", 1)

    if re.search("totalTransactions", line):
        rstats = set_rstat_metrics(node_name, line)
        return ("rstats", rstats)

    if re.search("traversed", line):
        ntails =\
            int(line.split(" tails traversed to find tip")[0].split('- ')[1])
        set_class_metric(node_name, "tailsTraversed", ntails)
        return ("tailsTraversed", 1)

    if re.search("#Solid/NonSolid", line):
        solid, non_solid = \
            [int(i) for i in line.split("#Solid/NonSolid: ")[1].split('/')]
        set_class_metric(node_name, 'solid', solid)
        set_class_metric(node_name, 'nonSolid', non_solid)
        return ("Solid/NonSolid", (solid, non_solid))

    if re.search("DEBUG MilestoneTrackerImpl:391 - Milestone ", line):
        if re.search("VALID", line):
            inc_class_metric(node_name, "milestoneValid")
            return ("milestoneValid", 1)
        return None

    if re.search("[generating solid entry points]: 100.00%", line):#snapshot
        inc_class_metric(node_name, "snapShot")
        return ("snapShot", 1)

    if re.search("DNS Checker", line):
        inc_class_metric(node_name, "dnsCheck")
        return ("dnsCheck", 1)

    if re.search("balance is not consistent", line):
        if re.search("Validation failed:", line):
            inc_class_metric(node_name, "inconsistentBalance")
            return ("inconsistentBalance", 1)
        return None

    if re.search("Invalid transaction timestamp", line):
        inc_class_metric(node_name, "invalidTimestamp")
        return ("invalidTimestamp", 1)

    if re.search("Sync check = ", line):
        sync_check = (line.split("Sync check = ")[-1])
        set_class_metric(node_name, "syncCheck", sync_check)
        return ("syncCheck", sync_check)

    return None


def inc_class_metric(node_name, metric):
    """metric should be a string in the node's metrics dictionary"""
    NODE_METRICS[node_name][metric].inc()


def set_class_metric(node_id, metric, val):
    """metric should be a string in the node's metrics dictionary"""
    NODE_METRICS[node_id][metric].set(val)


def set_rstat_metrics(node_name, line):
    rstats = parse_rstats(line) # rstats is tuple where idx is val
    set_class_metric(
        node_name, 'toProcess', rstats[0]
    )
    set_class_metric(
        node_name, 'toBroadcast', rstats[1]
    )
    set_class_metric(
        node_name, 'toRequest', rstats[2]
    )
    set_class_metric(
        node_name, 'toReply', rstats[3]
    )
    set_class_metric(
        node_name, 'totalTransactions', rstats[4]
    )
    return rstats


def parse_rstats(line):
    line = line.split("= ")
    toProcess = int(line[1].split(' ')[0])
    toBroadcast = int(line[2].split(' ')[0])
    toRequest = int(line[3].split(' ')[0])
    toReply = int(line[4].split(' ')[0])
    totalTransactions = int(line[5])
    return (toProcess, toBroadcast, toRequest, toReply, totalTransactions)


def match_and_set_node_metric(node_name, line):
    result = match_api_request(node_name, line)
    if result:
        return result
    else:
        result = match_x_class(node_name, line)
        if result:
            return result
    return None


def export_metrics(exporter_queue, logger):
    while True:
        line = exporter_queue.get(timeout=10000.0)
        if line:
            # we match the start of the line for snake_case node_names
            node = re.match(NODE_NAME_PATTERN, line)

            if node:
                node_name = node.group(0)
                # does nothing if we already are tracking
                start_tracking_nodes_metrics(node_name)

                result = match_and_set_node_metric(node_name, line)
                if result:
                    if result[1] == 1 and not (result[0]=="syncCheck"):
                        logger.info("Incremented {} for {}".format(
                            result[0], node_name)
                        )
                    else:
                        logger.info("Set {} for {} to {}".format(
                            result[0], node_name, result[1])
                        )


def trail_log(exporter_queue, fname):
    with open(fname, 'r') as fname:
        fname.seek(0,2) # Go to the end of the file
        while True:
            line = fname.readline()
            if not line:
                time.sleep(0.1) # Sleep briefly
                continue
            line = line.strip()
            exporter_queue.put(line)

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(description='Log scrapper.')

    PARSER.add_argument(
        '-fname',
        metavar='fname',
        type=str,
        default='',
        help='Log file to scrap'
    )
    PARSER.add_argument(
        '-server_port',
        metavar='server_port',
        type=int,
        default=9111,
        help='Port to push the metrics to. In case multiple exporters running.'
    )

    ARGS = PARSER.parse_args()

    logger = results_manager.LogManager(level="debug", output="file",
        filename="pendulum_export_"+str(ARGS.server_port)+".log")

    exporter_queue = Queue()


    start_http_server(ARGS.server_port)

    send_to_queue_thread = threading.Thread(
        target=trail_log, args = (exporter_queue, ARGS.fname,)
    )

    export_metrics_thread = threading.Thread(
        target=export_metrics,
        args = (exporter_queue, logger,)
    )

    send_to_queue_thread.start()
    export_metrics_thread.start()
