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
    'stdout_only': True, 'level': 'info',
    'parentdir': '/home/hlx-dev/helix/simple-log-aggregation',
    'log_filename': 'test.log'
}

log_manager = results_manager.ResultsManager(IO_OPTIONS)

logger = log_manager.logger

node_names = [
    "zmq", "hlxtest", "wallet.hlxtest", "node1", "node2", "node3",
    "nominee_1", "nominee_2", "nominee_3", "nominee_3", "nominee_5"
]

node_id_pattern = re.compile(r"^[a-zA-Z0-9._]+")

node_metrics = {
    'zmq': {
        'toProcess': Gauge('zmq_toProcess', ''),
        'toBroadcast': Gauge('zmq_toBroadcast', ''),
        'toRequest': Gauge('zmq_toRequest', ''),
        'toReply': Gauge('zmq_toReply', ''),
        'totalTransactions': Gauge('zmq_totalTransactions', ''),
        'tailsTraversed': Gauge('zmq_tailsTraversed', ''),
        'solid': Gauge('zmq_solid', ''),
        'nonSolid': Gauge('zmq_nonSolid', ''),
        'dnsCheck': Gauge('zmq_dnsCheck', ''),
        'milestoneChange': Gauge('zmq_milestoneChange', ''),
        'solidMilestoneChange': Gauge('zmq_solidMilestoneChange', ''),
        'addNeighbors': Gauge('zmq_addNeighbors', ''),
        'getNodeInfo': Gauge('zmq_getNodeInfo', ''),
        'attachToTangle': Gauge('zmq_attachToTangle', ''),
        'broadcastTransactions': Gauge('zmq_broadcastTransactions', ''),
        'getBalances': Gauge('zmq_getBalances', ''),
        'getInclusionStates': Gauge('zmq_getInclusionStates', ''),
        'getNeighbors': Gauge('zmq_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('zmq_getNodeAPIConfiguration', ''),
        'getTips': Gauge('zmq_getTips', ''),
        'getTransactionsToApprove': Gauge('zmq_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('zmq_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('zmq_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('zmq_removeNeighbors', ''),
        'storeTransactions': Gauge('zmq_storeTransactions', ''),
        'getMissingTransactions': Gauge('zmq_getMissingTransactions', ''),
        'checkConsistency': Gauge('zmq_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('zmq_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('zmq_startSpamming', ''),
        'stopSpamming': Gauge('zmq_stopSpamming', '')
    },
    'wallet.hlxtest': {
        'toProcess': Gauge('wallet_toProcess', ''),
        'toBroadcast': Gauge('wallet_toBroadcast', ''),
        'toRequest': Gauge('wallet_toRequest', ''),
        'toReply': Gauge('wallet_toReply', ''),
        'totalTransactions': Gauge('wallet_totalTransactions', ''),
        'tailsTraversed': Gauge('wallet_tailsTraversed', ''),
        'solid': Gauge('wallet_solid', ''),
        'nonSolid': Gauge('wallet_nonSolid', ''),
        'dnsCheck': Gauge('wallet_dnsCheck', ''),
        'milestoneChange': Gauge('wallet_milestoneChange', ''),
        'solidMilestoneChange': Gauge('wallet_solidMilestoneChange', ''),
        'addNeighbors': Gauge('wallet_addNeighbors', ''),
        'getNodeInfo': Gauge('wallet_getNodeInfo', ''),
        'attachToTangle': Gauge('wallet_attachToTangle', ''),
        'broadcastTransactions': Gauge('wallet_broadcastTransactions', ''),
        'getBalances': Gauge('wallet_getBalances', ''),
        'getInclusionStates': Gauge('wallet_getInclusionStates', ''),
        'getNeighbors': Gauge('wallet_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('wallet_getNodeAPIConfiguration', ''),
        'getTips': Gauge('wallet_getTips', ''),
        'getTransactionsToApprove': Gauge('wallet_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('wallet_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('wallet_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('wallet_removeNeighbors', ''),
        'storeTransactions': Gauge('wallet_storeTransactions', ''),
        'getMissingTransactions': Gauge('wallet_getMissingTransactions', ''),
        'checkConsistency': Gauge('wallet_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('wallet_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('wallet_startSpamming', ''),
        'stopSpamming': Gauge('wallet_stopSpamming', '')
    },
    'node_1': {
        'toProcess': Gauge('node1_toProcess', ''),
        'toBroadcast': Gauge('node1_toBroadcast', ''),
        'toRequest': Gauge('node1_toRequest', ''),
        'toReply': Gauge('node1_toReply', ''),
        'totalTransactions': Gauge('node1_totalTransactions', ''),
        'tailsTraversed': Gauge('node1_tailsTraversed', ''),
        'solid': Gauge('node1_solid', ''),
        'nonSolid': Gauge('node1_nonSolid', ''),
        'dnsCheck': Gauge('node1_dnsCheck', ''),
        'milestoneChange': Gauge('node1_milestoneChange', ''),
        'solidMilestoneChange': Gauge('node1_solidMilestoneChange', ''),
        'addNeighbors': Gauge('node1_addNeighbors', ''),
        'getNodeInfo': Gauge('node1_getNodeInfo', ''),
        'attachToTangle': Gauge('node1_attachToTangle', ''),
        'broadcastTransactions': Gauge('node1_broadcastTransactions', ''),
        'getBalances': Gauge('node1_getBalances', ''),
        'getInclusionStates': Gauge('node1_getInclusionStates', ''),
        'getNeighbors': Gauge('node1_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('node1_getNodeAPIConfiguration', ''),
        'getTips': Gauge('node1_getTips', ''),
        'getTransactionsToApprove': Gauge('node1_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('node1_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('node1_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('node1_removeNeighbors', ''),
        'storeTransactions': Gauge('node1_storeTransactions', ''),
        'getMissingTransactions': Gauge('node1_getMissingTransactions', ''),
        'checkConsistency': Gauge('node1_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('node1_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('node1_startSpamming', ''),
        'stopSpamming': Gauge('node1_stopSpamming', '')
    },
    'node_2': {
        'toProcess': Gauge('node2_toProcess', ''),
        'toBroadcast': Gauge('node2_toBroadcast', ''),
        'toRequest': Gauge('node2_toRequest', ''),
        'toReply': Gauge('node2_toReply', ''),
        'totalTransactions': Gauge('node2_totalTransactions', ''),
        'tailsTraversed': Gauge('node2_tailsTraversed', ''),
        'solid': Gauge('node2_solid', ''),
        'nonSolid': Gauge('node2_nonSolid', ''),
        'dnsCheck': Gauge('node2_dnsCheck', ''),
        'milestoneChange': Gauge('node2_milestoneChange', ''),
        'solidMilestoneChange': Gauge('node2_solidMilestoneChange', ''),
        'addNeighbors': Gauge('node2_addNeighbors', ''),
        'getNodeInfo': Gauge('node2_getNodeInfo', ''),
        'attachToTangle': Gauge('node2_attachToTangle', ''),
        'broadcastTransactions': Gauge('node2_broadcastTransactions', ''),
        'getBalances': Gauge('node2_getBalances', ''),
        'getInclusionStates': Gauge('node2_getInclusionStates', ''),
        'getNeighbors': Gauge('node2_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('node2_getNodeAPIConfiguration', ''),
        'getTips': Gauge('node2_getTips', ''),
        'getTransactionsToApprove': Gauge('node2_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('node2_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('node2_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('node2_removeNeighbors', ''),
        'storeTransactions': Gauge('node2_storeTransactions', ''),
        'getMissingTransactions': Gauge('node2_getMissingTransactions', ''),
        'checkConsistency': Gauge('node2_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('node2_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('node2_startSpamming', ''),
        'stopSpamming': Gauge('node2_stopSpamming', '')
    },
    'node_3': {
        'toProcess': Gauge('node3_toProcess', ''),
        'toBroadcast': Gauge('node3_toBroadcast', ''),
        'toRequest': Gauge('node3_toRequest', ''),
        'toReply': Gauge('node3_toReply', ''),
        'totalTransactions': Gauge('node3_totalTransactions', ''),
        'tailsTraversed': Gauge('node3_tailsTraversed', ''),
        'solid': Gauge('node3_solid', ''),
        'nonSolid': Gauge('node3_nonSolid', ''),
        'dnsCheck': Gauge('node3_dnsCheck', ''),
        'milestoneChange': Gauge('node3_milestoneChange', ''),
        'solidMilestoneChange': Gauge('node3_solidMilestoneChange', ''),
        'addNeighbors': Gauge('node3_addNeighbors', ''),
        'getNodeInfo': Gauge('node3_getNodeInfo', ''),
        'attachToTangle': Gauge('node3_attachToTangle', ''),
        'broadcastTransactions': Gauge('node3_broadcastTransactions', ''),
        'getBalances': Gauge('node3_getBalances', ''),
        'getInclusionStates': Gauge('node3_getInclusionStates', ''),
        'getNeighbors': Gauge('node3_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('node3_getNodeAPIConfiguration', ''),
        'getTips': Gauge('node3_getTips', ''),
        'getTransactionsToApprove': Gauge('node3_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('node3_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('node3_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('node3_removeNeighbors', ''),
        'storeTransactions': Gauge('node3_storeTransactions', ''),
        'getMissingTransactions': Gauge('node3_getMissingTransactions', ''),
        'checkConsistency': Gauge('node3_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('node3_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('node3_startSpamming', ''),
        'stopSpamming': Gauge('node3_stopSpamming', '')
    },
    'hlxtest': {
        'toProcess': Gauge('hlxtest_toProcess', ''),
        'toBroadcast': Gauge('hlxtest_toBroadcast', ''),
        'toRequest': Gauge('hlxtest_toRequest', ''),
        'toReply': Gauge('hlxtest_toReply', ''),
        'totalTransactions': Gauge('hlxtest_totalTransactions', ''),
        'tailsTraversed': Gauge('hlxtest_tailsTraversed', ''),
        'solid': Gauge('hlxtest_solid', ''),
        'nonSolid': Gauge('hlxtest_nonSolid', ''),
        'dnsCheck': Gauge('hlxtest_dnsCheck', ''),
        'milestoneChange': Gauge('hlxtest_milestoneChange', ''),
        'solidMilestoneChange': Gauge('hlxtest_solidMilestoneChange', ''),
        'addNeighbors': Gauge('hlxtest_addNeighbors', ''),
        'getNodeInfo': Gauge('hlxtest_getNodeInfo', ''),
        'attachToTangle': Gauge('hlxtest_attachToTangle', ''),
        'broadcastTransactions': Gauge('hlxtest_broadcastTransactions', ''),
        'getBalances': Gauge('hlxtest_getBalances', ''),
        'getInclusionStates': Gauge('hlxtest_getInclusionStates', ''),
        'getNeighbors': Gauge('hlxtest_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('hlxtest_getNodeAPIConfiguration', ''),
        'getTips': Gauge('hlxtest_getTips', ''),
        'getTransactionsToApprove': Gauge('hlxtest_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('hlxtest_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('hlxtest_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('hlxtest_removeNeighbors', ''),
        'storeTransactions': Gauge('hlxtest_storeTransactions', ''),
        'getMissingTransactions': Gauge('hlxtest_getMissingTransactions', ''),
        'checkConsistency': Gauge('hlxtest_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('hlxtest_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('hlxtest_startSpamming', ''),
        'stopSpamming': Gauge('hlxtest_stopSpamming', '')
    },
    'nominee_1': {
        'toProcess': Gauge('nominee_1_toProcess', ''),
        'toBroadcast': Gauge('nominee_1_toBroadcast', ''),
        'toRequest': Gauge('nominee_1_toRequest', ''),
        'toReply': Gauge('nominee_1_toReply', ''),
        'totalTransactions': Gauge('nominee_1_totalTransactions', ''),
        'tailsTraversed': Gauge('nominee_1_tailsTraversed', ''),
        'solid': Gauge('nominee_1_solid', ''),
        'nonSolid': Gauge('nominee_1_nonSolid', ''),
        'dnsCheck': Gauge('nominee_1_dnsCheck', ''),
        'milestoneChange': Gauge('nominee_1_milestoneChange', ''),
        'solidMilestoneChange': Gauge('nominee_1_solidMilestoneChange', ''),
        'addNeighbors': Gauge('nominee_1_addNeighbors', ''),
        'getNodeInfo': Gauge('nominee_1_getNodeInfo', ''),
        'attachToTangle': Gauge('nominee_1_attachToTangle', ''),
        'broadcastTransactions': Gauge('nominee_1_broadcastTransactions', ''),
        'getBalances': Gauge('nominee_1_getBalances', ''),
        'getInclusionStates': Gauge('nominee_1_getInclusionStates', ''),
        'getNeighbors': Gauge('nominee_1_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('nominee_1_getNodeAPIConfiguration', ''),
        'getTips': Gauge('nominee_1_getTips', ''),
        'getTransactionsToApprove': Gauge('nominee_1_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('nominee_1_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('nominee_1_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('nominee_1_removeNeighbors', ''),
        'storeTransactions': Gauge('nominee_1_storeTransactions', ''),
        'getMissingTransactions': Gauge('nominee_1_getMissingTransactions', ''),
        'checkConsistency': Gauge('nominee_1_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('nominee_1_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('nominee_1_startSpamming', ''),
        'stopSpamming': Gauge('nominee_1_stopSpamming', '')
    },
    'nominee_2': {
        'toProcess': Gauge('nominee_2_toProcess', ''),
        'toBroadcast': Gauge('nominee_2_toBroadcast', ''),
        'toRequest': Gauge('nominee_2_toRequest', ''),
        'toReply': Gauge('nominee_2_toReply', ''),
        'totalTransactions': Gauge('nominee_2_totalTransactions', ''),
        'tailsTraversed': Gauge('nominee_2_tailsTraversed', ''),
        'solid': Gauge('nominee_2_solid', ''),
        'nonSolid': Gauge('nominee_2_nonSolid', ''),
        'dnsCheck': Gauge('nominee_2_dnsCheck', ''),
        'milestoneChange': Gauge('nominee_2_milestoneChange', ''),
        'solidMilestoneChange': Gauge('nominee_2_solidMilestoneChange', ''),
        'addNeighbors': Gauge('nominee_2_addNeighbors', ''),
        'getNodeInfo': Gauge('nominee_2_getNodeInfo', ''),
        'attachToTangle': Gauge('nominee_2_attachToTangle', ''),
        'broadcastTransactions': Gauge('nominee_2_broadcastTransactions', ''),
        'getBalances': Gauge('nominee_2_getBalances', ''),
        'getInclusionStates': Gauge('nominee_2_getInclusionStates', ''),
        'getNeighbors': Gauge('nominee_2_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('nominee_2_getNodeAPIConfiguration', ''),
        'getTips': Gauge('nominee_2_getTips', ''),
        'getTransactionsToApprove': Gauge('nominee_2_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('nominee_2_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('nominee_2_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('nominee_2_removeNeighbors', ''),
        'storeTransactions': Gauge('nominee_2_storeTransactions', ''),
        'getMissingTransactions': Gauge('nominee_2_getMissingTransactions', ''),
        'checkConsistency': Gauge('nominee_2_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('nominee_2_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('nominee_2_startSpamming', ''),
        'stopSpamming': Gauge('nominee_2_stopSpamming', '')
    },
    'nominee_3': {
        'toProcess': Gauge('nominee_3_toProcess', ''),
        'toBroadcast': Gauge('nominee_3_toBroadcast', ''),
        'toRequest': Gauge('nominee_3_toRequest', ''),
        'toReply': Gauge('nominee_3_toReply', ''),
        'totalTransactions': Gauge('nominee_3_totalTransactions', ''),
        'tailsTraversed': Gauge('nominee_3_tailsTraversed', ''),
        'solid': Gauge('nominee_3_solid', ''),
        'nonSolid': Gauge('nominee_3_nonSolid', ''),
        'dnsCheck': Gauge('nominee_3_dnsCheck', ''),
        'milestoneChange': Gauge('nominee_3_milestoneChange', ''),
        'solidMilestoneChange': Gauge('nominee_3_solidMilestoneChange', ''),
        'addNeighbors': Gauge('nominee_3_addNeighbors', ''),
        'getNodeInfo': Gauge('nominee_3_getNodeInfo', ''),
        'attachToTangle': Gauge('nominee_3_attachToTangle', ''),
        'broadcastTransactions': Gauge('nominee_3_broadcastTransactions', ''),
        'getBalances': Gauge('nominee_3_getBalances', ''),
        'getInclusionStates': Gauge('nominee_3_getInclusionStates', ''),
        'getNeighbors': Gauge('nominee_3_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('nominee_3_getNodeAPIConfiguration', ''),
        'getTips': Gauge('nominee_3_getTips', ''),
        'getTransactionsToApprove': Gauge('nominee_3_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('nominee_3_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('nominee_3_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('nominee_3_removeNeighbors', ''),
        'storeTransactions': Gauge('nominee_3_storeTransactions', ''),
        'getMissingTransactions': Gauge('nominee_3_getMissingTransactions', ''),
        'checkConsistency': Gauge('nominee_3_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('nominee_3_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('nominee_3_startSpamming', ''),
        'stopSpamming': Gauge('nominee_3_stopSpamming', '')
    },
    'nominee_4': {
        'toProcess': Gauge('nominee_4_toProcess', ''),
        'toBroadcast': Gauge('nominee_4_toBroadcast', ''),
        'toRequest': Gauge('nominee_4_toRequest', ''),
        'toReply': Gauge('nominee_4_toReply', ''),
        'totalTransactions': Gauge('nominee_4_totalTransactions', ''),
        'tailsTraversed': Gauge('nominee_4_tailsTraversed', ''),
        'solid': Gauge('nominee_4_solid', ''),
        'nonSolid': Gauge('nominee_4_nonSolid', ''),
        'dnsCheck': Gauge('nominee_4_dnsCheck', ''),
        'milestoneChange': Gauge('nominee_4_milestoneChange', ''),
        'solidMilestoneChange': Gauge('nominee_4_solidMilestoneChange', ''),
        'addNeighbors': Gauge('nominee_4_addNeighbors', ''),
        'getNodeInfo': Gauge('nominee_4_getNodeInfo', ''),
        'attachToTangle': Gauge('nominee_4_attachToTangle', ''),
        'broadcastTransactions': Gauge('nominee_4_broadcastTransactions', ''),
        'getBalances': Gauge('nominee_4_getBalances', ''),
        'getInclusionStates': Gauge('nominee_4_getInclusionStates', ''),
        'getNeighbors': Gauge('nominee_4_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('nominee_4_getNodeAPIConfiguration', ''),
        'getTips': Gauge('nominee_4_getTips', ''),
        'getTransactionsToApprove': Gauge('nominee_4_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('nominee_4_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('nominee_4_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('nominee_4_removeNeighbors', ''),
        'storeTransactions': Gauge('nominee_4_storeTransactions', ''),
        'getMissingTransactions': Gauge('nominee_4_getMissingTransactions', ''),
        'checkConsistency': Gauge('nominee_4_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('nominee_4_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('nominee_4_startSpamming', ''),
        'stopSpamming': Gauge('nominee_4_stopSpamming', '')
    },
    'nominee_5': {
        'toProcess': Gauge('nominee_5_toProcess', ''),
        'toBroadcast': Gauge('nominee_5_toBroadcast', ''),
        'toRequest': Gauge('nominee_5_toRequest', ''),
        'toReply': Gauge('nominee_5_toReply', ''),
        'totalTransactions': Gauge('nominee_5_totalTransactions', ''),
        'tailsTraversed': Gauge('nominee_5_tailsTraversed', ''),
        'solid': Gauge('nominee_5_solid', ''),
        'nonSolid': Gauge('nominee_5_nonSolid', ''),
        'dnsCheck': Gauge('nominee_5_dnsCheck', ''),
        'milestoneChange': Gauge('nominee_5_milestoneChange', ''),
        'solidMilestoneChange': Gauge('nominee_5_solidMilestoneChange', ''),
        'addNeighbors': Gauge('nominee_5_addNeighbors', ''),
        'getNodeInfo': Gauge('nominee_5_getNodeInfo', ''),
        'attachToTangle': Gauge('nominee_5_attachToTangle', ''),
        'broadcastTransactions': Gauge('nominee_5_broadcastTransactions', ''),
        'getBalances': Gauge('nominee_5_getBalances', ''),
        'getInclusionStates': Gauge('nominee_5_getInclusionStates', ''),
        'getNeighbors': Gauge('nominee_5_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('nominee_5_getNodeAPIConfiguration', ''),
        'getTips': Gauge('nominee_5_getTips', ''),
        'getTransactionsToApprove': Gauge('nominee_5_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('nominee_5_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('nominee_5_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('nominee_5_removeNeighbors', ''),
        'storeTransactions': Gauge('nominee_5_storeTransactions', ''),
        'getMissingTransactions': Gauge('nominee_5_getMissingTransactions', ''),
        'checkConsistency': Gauge('nominee_5_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('nominee_5_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('nominee_5_startSpamming', ''),
        'stopSpamming': Gauge('nominee_5_stopSpamming', '')
    },
}

def match_for_api_request(line):
    if re.search("getNodeInfo", line):
        return "getNodeInfo"
    if re.search("getBalances", line):
        return "getBalances"
    if re.search("findTransactions", line):
        return "findTransactions"
    if re.search("getTransactionsToApprove", line):
        return "getTransactionsToApprove"
    if re.search("getTransactionStrings", line):
        return "getTransactionStrings"
    if re.search("attachToTangle", line):
        return "attachToTangle"
    if re.search("broadcastTransactions", line):
        return "broadcastTransactions"
    if re.search("getInclusionStates", line):
        return "getInclusionStates"
    if re.search("getNeighbors", line):
        return "getNeighbors"
    if re.search("addNeighbors", line):
        return "findTransactions"
    if re.search("getNodeAPIConfiguration", line):
        return "getNodeAPIConfiguration"
    if re.search("getTips", line):
        return "getTips"
    if re.search("interruptAttachingToTangle", line):
        return "interruptAttachingToTangle"
    if re.search("removeNeighbors", line):
        return "removeNeighbors"
    if re.search("storeTransactions", line):
        return "storeTransactions"
    if re.search("getMissingTransactions", line):
        return "getMissingTransactions"
    if re.search("checkConsistency", line):
        return "checkConsistency"
    if re.search("wereAddressesSpentFrom", line):
        return "wereAddressesSpentFrom"
    if re.search("startSpamming", line):
        return "startSpamming"
    if re.search("stopSpamming", line):
        return "stopSpamming"
    return

def node_class_rstats(line):
    line = line.split("= ")
    toProcess = int(line[1].split(' ')[0])
    toBroadcast = int(line[2].split(' ')[0])
    toRequest = int(line[3].split(' ')[0])
    toReply = int(line[4].split(' ')[0])
    totalTransactions = int(line[5])
    return (toProcess, toBroadcast, toRequest, toReply, totalTransactions)

def match_class_outside_api(line):
    if re.search("totalTransactions", line):
        rstats = node_class_rstats(line)
        return {"rstats": rstats}

    if re.search("traversed", line):
        ntails =\
            int(line.split(" tails traversed to find tip")[0].split('- ')[1])
        return {"tailsTraversed": ntails}

    if re.search("Latest SOLID milestone index changed", line):
        solid_ms_index = int(line.split("#")[2])
        return {"solidMilestoneChange": solid_ms_index}

    if re.search("#Solid/NonSolid", line):
        solid, non_solid = \
            [int(i) for i in line.split("#Solid/NonSolid: ")[1].split('/')]
        return {"solid/nonSolid": (solid, non_solid)}

    if re.search("Latest milestone has changed", line):
        latest_ms_index = int(line.split("#")[2])
        return {"milestoneChange": latest_ms_index}

    if re.search("generating solid entry points", line):#snapshot
        return {"snapShot": 1}

    if re.search("DNS Checker", line):
        return {"dnsCheck": 1}

    return None

def inc_api_metric(node_id, api_request):
    node_metrics[node_id][api_request].inc()

def set_class_metric(node_id, metric, val):
    node_metrics[node_id][metric].set(val)

def export_metrics(exporter_queue):
    while True:
        line = exporter_queue.get(timeout=10000.0)
        if line:
            node = re.match(node_id_pattern, line)
            if node:
                node_id = node.group(0)
                api_request = match_for_api_request(line)
                if api_request:
                    inc_api_metric(node_id, api_request)
                    logger.info("Incremented {} for {}".format(api_request, node_id))
                    continue
                data = match_class_outside_api(line)
                if data:
                    if data.get("rstats"):
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
            #print(line)
            exporter_queue.put(line)

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
    description='Log server.'
    )
    PARSER.add_argument('-fname',
        metavar='fname', type=str, default='',
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
