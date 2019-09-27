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

IO_OPTIONS = {
    'stdout_only': False, 'level': 'info',
    'parentdir': './',
    'log_filename': 'pendulum_export.log'
}

log_manager = results_manager.ResultsManager(IO_OPTIONS)

logger = log_manager.logger

known_node_names = [
    "zmq", "hlxtest", "wallet", "node1", "node2", "node3",
    "nominee_1", "nominee_2", "nominee_3", "nominee_3", "nominee_5"
]

"""
NO! Can't use this logic due to docker
The node_id_pattern matches the first segment of the logline. It is assumed
that the loglines are shipped with a unique hexdecimal string of len 8
This is cared for by the ship_log.py or pipe_log.py programs.
The program hashes the hostname and concatenates this hashed hostname
to the start of the logline.
node_id_pattern = re.compile(r"^[a-fA-F0-9]+")
"""

node_id_pattern = re.compile(r"^[a-zA-Z0-9._]+")

api_request_metrics = [
    '{}_addNeighbors', '{}_getNodeInfo', '{}_attachToTangle',
    '{}_broadcastTransactions', '{}_getBalances', '{}_getInclusionStates',
    '{}_getNeighbors', '{}_getNodeAPIConfiguration', '{}_getTips',
    '{}_getTransactionsToApprove', '{}_getTransactionStrings',
    '{}_interruptAttachingToTangle', '{}_removeNeighbors',
    '{}_storeTransactions', '{}_getMissingTransactions', '{}_checkConsistency',
    '{}_wereAddressesSpentFrom', '{}_findTransactions'
]

x_class_metrics = [
    '{}_toProcess', '{}_toBroadcast', '{}_toRequest', '{}_toReply',
    '{}_totalTransactions', '{}_tailsTraversed', '{}_solid', '{}_nonSolid',
    '{}_dnsCheck', '{}_milestoneChange', '{}_solidMilestoneChange'
]

"""
We construct all of the gauges for nodes here.
Current downside here is the insistent usage of the Gauge.
We should investigate our metric types in prom.
"""
def construct_metrics(node_name, api_request_metrics, x_class_metrics):
    metrics = {
        node_name: {
            metric[3:]: Gauge(metric.format(node_name), 'api metrics')
                for metric in api_request_metrics
        }
    }
    for metric in x_class_metrics:
        metrics[node_name].update(
            {metric[3:]: Gauge(metric.format(node_name), 'class metrics')}
        )
    return metrics

"""
The downside of this method is that we iterate through the
api request types without knowing the frequency distribution
of their occurence in the wild. If we knew that findTransactions
occurs more frequenctly than checkConsistency, for example,
then we could first match for findTransactions and then proceed.
"""
def match_for_api_request(api_request_metrics, line):
    for metric in api_request_metrics:
        if re.search(metric[3:], line):
            return metric[3:]
    return None

def parse_rstats(line):
    line = line.split("= ")
    toProcess = int(line[1].split(' ')[0])
    toBroadcast = int(line[2].split(' ')[0])
    toRequest = int(line[3].split(' ')[0])
    toReply = int(line[4].split(' ')[0])
    totalTransactions = int(line[5])
    return (toProcess, toBroadcast, toRequest, toReply, totalTransactions)

def match_class_outside_api(line):
    if re.search("totalTransactions", line):
        rstats = parse_rstats(line)
        return {"rstats": rstats}

    if re.search("traversed", line):
        ntails =\
            int(line.split(" tails traversed to find tip")[0].split('- ')[1])
        return {"tailsTraversed": ntails}

    # if re.search("Latest SOLID milestone index changed", line):
    #     solid_ms_index = int(line.split("#")[2])
    #     return {"solidMilestoneChange": solid_ms_index}

    if re.search("#Solid/NonSolid", line):
        solid, non_solid = \
            [int(i) for i in line.split("#Solid/NonSolid: ")[1].split('/')]
        return {"solid/nonSolid": (solid, non_solid)}

    if re.search("Latest milestone has changed", line):
        latest_ms_index = int(line.split("#")[2])
        return {"milestoneChange": latest_ms_index}

    if re.search("[generating solid entry points]: 100.00%", line):#snapshot
        return {"snapShot": 1}

    if re.search("DNS Checker", line):
        return {"dnsCheck": 1}

    if re.search("balance is not consistent", line):
        if re.search("Validation failed:", line):
            print(line)
            return {"validationFailure": 1}

    return None

def inc_api_metric(node_id, api_request):
    node_metrics[node_id][api_request].inc()


def set_rstat_metrics(node_id, data):
    set_class_metric(
        node_id, 'toProcess', data['rstats'][0]
    )
    set_class_metric(
        node_id, 'toBroadcast', data['rstats'][1]
    )
    set_class_metric(
        node_id, 'toRequest', data['rstats'][2]
    )
    set_class_metric(
        node_id, 'toReply', data['rstats'][3]
    )
    set_class_metric(
        node_id, 'totalTransactions', data['rstats'][4]
    )

def set_class_metric(node_id, metric, val):
    if metric in node_metrics[node_id]:
        node_metrics[node_id][metric].set(val)
    else:
        node_metrics[node_id][metric] = \
            Gauge('{}_{}'.format(node_id, metric),
                'The values of the metric {} for node {}'.format(
                    metric, node_id
                )
            )

KNOWN_NODES = []
node_metrics = {}

def update_node_metrics(node_id):
    if node_id not in KNOWN_NODES and len(KNOWN_NODES) < 10:
        KNOWN_NODES.append(node_id)
        node_metrics.update(
            construct_metrics(
                node_id,
                api_request_metrics,
                x_class_metrics
            )
        )

def export_metrics(exporter_queue):
    while True:
        line = exporter_queue.get(timeout=10000.0)
        if line:
            node = re.match(node_id_pattern, line)
            if node:
                node_id = node.group(0)
                update_node_metrics(node_id)
                api_request = match_for_api_request(api_request_metrics, line)
                if api_request:
                    inc_api_metric(node_id, api_request)
                    logger.info("Incremented {} for {}".format(api_request, node_id))
                    continue
                data = match_class_outside_api(line)
                if data:
                    if data.get("rstats"):
                        set_rstat_metrics(node_id, data)
                        logger.info("New rstats for node {}: {}".format(
                            node_id, data['rstats'])
                        )
                        continue
                    if data.get("solid/nonSolid"):
                        set_class_metric(
                            node_id, 'solid', data['solid/nonSolid'][0]
                        )
                        set_class_metric(
                            node_id, 'nonSolid', data['solid/nonSolid'][1]
                        )
                        logger.info(
                            "New solid/nonsolid report for {}: {}".format(
                                node_id, data['solid/nonSolid']
                            )
                        )
                        continue
                    else:
                        data = data.popitem()
                        set_class_metric(
                            node_id, data[0], data[1]
                        )
                        logger.info("New metric report {} for {}".format(
                            node_id, data
                            )
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

    ARGS = PARSER.parse_args()

    exporter_queue = Queue()

    start_http_server(9111)

    send_to_queue_thread = threading.Thread(
        target=trail_log, args = (exporter_queue, ARGS.fname,)
    )

    export_metrics_thread = threading.Thread(
        target=export_metrics,
        args = (exporter_queue,)
    )

    send_to_queue_thread.start()
    export_metrics_thread.start()
