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
    "zmq", "coo", "node1", "node2", "node3", "hlxtest", "helix-esports",
    "follower_1_1", "follower_2_1", "follower_3_1", "follower_4_1",
    "coordinator_1_1", "relayer_1", "backend_1"
]

node_id_pattern = re.compile(r"^[a-zA-Z0-9_]+")

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
    'coo': {
        'toProcess': Gauge('coo_toProcess', ''),
        'toBroadcast': Gauge('coo_toBroadcast', ''),
        'toRequest': Gauge('coo_toRequest', ''),
        'toReply': Gauge('coo_toReply', ''),
        'totalTransactions': Gauge('coo_totalTransactions', ''),
        'tailsTraversed': Gauge('coo_tailsTraversed', ''),
        'solid': Gauge('coo_solid', ''),
        'nonSolid': Gauge('coo_nonSolid', ''),
        'dnsCheck': Gauge('coo_dnsCheck', ''),
        'milestoneChange': Gauge('coo_milestoneChange', ''),
        'solidMilestoneChange': Gauge('coo_solidMilestoneChange', ''),
        'addNeighbors': Gauge('coo_addNeighbors', ''),
        'getNodeInfo': Gauge('coo_getNodeInfo', ''),
        'attachToTangle': Gauge('coo_attachToTangle', ''),
        'broadcastTransactions': Gauge('coo_broadcastTransactions', ''),
        'getBalances': Gauge('coo_getBalances', ''),
        'getInclusionStates': Gauge('coo_getInclusionStates', ''),
        'getNeighbors': Gauge('coo_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('coo_getNodeAPIConfiguration', ''),
        'getTips': Gauge('coo_getTips', ''),
        'getTransactionsToApprove': Gauge('coo_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('coo_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('coo_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('coo_removeNeighbors', ''),
        'storeTransactions': Gauge('coo_storeTransactions', ''),
        'getMissingTransactions': Gauge('coo_getMissingTransactions', ''),
        'checkConsistency': Gauge('coo_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('coo_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('coo_startSpamming', ''),
        'stopSpamming': Gauge('coo_stopSpamming', '')
    },
    'node1': {
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
    'node2': {
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
    'node3': {
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
    'helix': {
        'toProcess': Gauge('esports_toProcess', ''),
        'toBroadcast': Gauge('esports_toBroadcast', ''),
        'toRequest': Gauge('esports_toRequest', ''),
        'toReply': Gauge('esports_toReply', ''),
        'totalTransactions': Gauge('esports_totalTransactions', ''),
        'tailsTraversed': Gauge('esports_tailsTraversed', ''),
        'solid': Gauge('esports_solid', ''),
        'nonSolid': Gauge('esports_nonSolid', ''),
        'dnsCheck': Gauge('esports_dnsCheck', ''),
        'milestoneChange': Gauge('esports_milestoneChange', ''),
        'solidMilestoneChange': Gauge('esports_solidMilestoneChange', ''),
        'addNeighbors': Gauge('esports_addNeighbors', ''),
        'getNodeInfo': Gauge('esports_getNodeInfo', ''),
        'attachToTangle': Gauge('esports_attachToTangle', ''),
        'broadcastTransactions': Gauge('esports_broadcastTransactions', ''),
        'getBalances': Gauge('esports_getBalances', ''),
        'getInclusionStates': Gauge('esports_getInclusionStates', ''),
        'getNeighbors': Gauge('esports_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('esports_getNodeAPIConfiguration', ''),
        'getTips': Gauge('esports_getTips', ''),
        'getTransactionsToApprove': Gauge('esports_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('esports_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('esports_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('esports_removeNeighbors', ''),
        'storeTransactions': Gauge('esports_storeTransactions', ''),
        'getMissingTransactions': Gauge('esports_getMissingTransactions', ''),
        'checkConsistency': Gauge('esports_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('esports_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('esports_startSpamming', ''),
        'stopSpamming': Gauge('esports_stopSpamming', '')
    },
    'follower_1_1': {
        'toProcess': Gauge('follower_1_toProcess', ''),
        'toBroadcast': Gauge('follower_1_toBroadcast', ''),
        'toRequest': Gauge('follower_1_toRequest', ''),
        'toReply': Gauge('follower_1_toReply', ''),
        'totalTransactions': Gauge('follower_1_totalTransactions', ''),
        'tailsTraversed': Gauge('follower_1_tailsTraversed', ''),
        'solid': Gauge('follower_1_solid', ''),
        'nonSolid': Gauge('follower_1_nonSolid', ''),
        'dnsCheck': Gauge('follower_1_dnsCheck', ''),
        'milestoneChange': Gauge('follower_1_milestoneChange', ''),
        'solidMilestoneChange': Gauge('follower_1_solidMilestoneChange', ''),
        'addNeighbors': Gauge('follower_1_addNeighbors', ''),
        'getNodeInfo': Gauge('follower_1_getNodeInfo', ''),
        'attachToTangle': Gauge('follower_1_attachToTangle', ''),
        'broadcastTransactions': Gauge('follower_1_broadcastTransactions', ''),
        'getBalances': Gauge('follower_1_getBalances', ''),
        'getInclusionStates': Gauge('follower_1_getInclusionStates', ''),
        'getNeighbors': Gauge('follower_1_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('follower_1_getNodeAPIConfiguration', ''),
        'getTips': Gauge('follower_1_getTips', ''),
        'getTransactionsToApprove': Gauge('follower_1_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('follower_1_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('follower_1_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('follower_1_removeNeighbors', ''),
        'storeTransactions': Gauge('follower_1_storeTransactions', ''),
        'getMissingTransactions': Gauge('follower_1_getMissingTransactions', ''),
        'checkConsistency': Gauge('follower_1_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('follower_1_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('follower_1_startSpamming', ''),
        'stopSpamming': Gauge('follower_1_stopSpamming', '')
    },
    'follower_2_1': {
        'toProcess': Gauge('follower_2_toProcess', ''),
        'toBroadcast': Gauge('follower_2_toBroadcast', ''),
        'toRequest': Gauge('follower_2_toRequest', ''),
        'toReply': Gauge('follower_2_toReply', ''),
        'totalTransactions': Gauge('follower_2_totalTransactions', ''),
        'tailsTraversed': Gauge('follower_2_tailsTraversed', ''),
        'solid': Gauge('follower_2_solid', ''),
        'nonSolid': Gauge('follower_2_nonSolid', ''),
        'dnsCheck': Gauge('follower_2_dnsCheck', ''),
        'milestoneChange': Gauge('follower_2_milestoneChange', ''),
        'solidMilestoneChange': Gauge('follower_2_solidMilestoneChange', ''),
        'addNeighbors': Gauge('follower_2_addNeighbors', ''),
        'getNodeInfo': Gauge('follower_2_getNodeInfo', ''),
        'attachToTangle': Gauge('follower_2_attachToTangle', ''),
        'broadcastTransactions': Gauge('follower_2_broadcastTransactions', ''),
        'getBalances': Gauge('follower_2_getBalances', ''),
        'getInclusionStates': Gauge('follower_2_getInclusionStates', ''),
        'getNeighbors': Gauge('follower_2_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('follower_2_getNodeAPIConfiguration', ''),
        'getTips': Gauge('follower_2_getTips', ''),
        'getTransactionsToApprove': Gauge('follower_2_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('follower_2_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('follower_2_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('follower_2_removeNeighbors', ''),
        'storeTransactions': Gauge('follower_2_storeTransactions', ''),
        'getMissingTransactions': Gauge('follower_2_getMissingTransactions', ''),
        'checkConsistency': Gauge('follower_2_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('follower_2_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('follower_2_startSpamming', ''),
        'stopSpamming': Gauge('follower_2_stopSpamming', '')
    },
    'follower_3_1': {
        'toProcess': Gauge('follower_3_toProcess', ''),
        'toBroadcast': Gauge('follower_3_toBroadcast', ''),
        'toRequest': Gauge('follower_3_toRequest', ''),
        'toReply': Gauge('follower_3_toReply', ''),
        'totalTransactions': Gauge('follower_3_totalTransactions', ''),
        'tailsTraversed': Gauge('follower_3_tailsTraversed', ''),
        'solid': Gauge('follower_3_solid', ''),
        'nonSolid': Gauge('follower_3_nonSolid', ''),
        'dnsCheck': Gauge('follower_3_dnsCheck', ''),
        'milestoneChange': Gauge('follower_3_milestoneChange', ''),
        'solidMilestoneChange': Gauge('follower_3_solidMilestoneChange', ''),
        'addNeighbors': Gauge('follower_3_addNeighbors', ''),
        'getNodeInfo': Gauge('follower_3_getNodeInfo', ''),
        'attachToTangle': Gauge('follower_3_attachToTangle', ''),
        'broadcastTransactions': Gauge('follower_3_broadcastTransactions', ''),
        'getBalances': Gauge('follower_3_getBalances', ''),
        'getInclusionStates': Gauge('follower_3_getInclusionStates', ''),
        'getNeighbors': Gauge('follower_3_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('follower_3_getNodeAPIConfiguration', ''),
        'getTips': Gauge('follower_3_getTips', ''),
        'getTransactionsToApprove': Gauge('follower_3_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('follower_3_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('follower_3_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('follower_3_removeNeighbors', ''),
        'storeTransactions': Gauge('follower_3_storeTransactions', ''),
        'getMissingTransactions': Gauge('follower_3_getMissingTransactions', ''),
        'checkConsistency': Gauge('follower_3_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('follower_3_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('follower_3_startSpamming', ''),
        'stopSpamming': Gauge('follower_3_stopSpamming', '')
    },
    'follower_4_1': {
        'toProcess': Gauge('follower_4_toProcess', ''),
        'toBroadcast': Gauge('follower_4_toBroadcast', ''),
        'toRequest': Gauge('follower_4_toRequest', ''),
        'toReply': Gauge('follower_4_toReply', ''),
        'totalTransactions': Gauge('follower_4_totalTransactions', ''),
        'tailsTraversed': Gauge('follower_4_tailsTraversed', ''),
        'solid': Gauge('follower_4_solid', ''),
        'nonSolid': Gauge('follower_4_nonSolid', ''),
        'dnsCheck': Gauge('follower_4_dnsCheck', ''),
        'milestoneChange': Gauge('follower_4_milestoneChange', ''),
        'solidMilestoneChange': Gauge('follower_4_solidMilestoneChange', ''),
        'addNeighbors': Gauge('follower_4_addNeighbors', ''),
        'getNodeInfo': Gauge('follower_4_getNodeInfo', ''),
        'attachToTangle': Gauge('follower_4_attachToTangle', ''),
        'broadcastTransactions': Gauge('follower_4_broadcastTransactions', ''),
        'getBalances': Gauge('follower_4_getBalances', ''),
        'getInclusionStates': Gauge('follower_4_getInclusionStates', ''),
        'getNeighbors': Gauge('follower_4_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('follower_4_getNodeAPIConfiguration', ''),
        'getTips': Gauge('follower_4_getTips', ''),
        'getTransactionsToApprove': Gauge('follower_4_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('follower_4_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('follower_4_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('follower_4_removeNeighbors', ''),
        'storeTransactions': Gauge('follower_4_storeTransactions', ''),
        'getMissingTransactions': Gauge('follower_4_getMissingTransactions', ''),
        'checkConsistency': Gauge('follower_4_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('follower_4_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('follower_4_startSpamming', ''),
        'stopSpamming': Gauge('follower_4_stopSpamming', '')
    },
    'coordinator_1': {
        'toProcess': Gauge('coordinator_1_toProcess', ''),
        'toBroadcast': Gauge('coordinator_1_toBroadcast', ''),
        'toRequest': Gauge('coordinator_1_toRequest', ''),
        'toReply': Gauge('coordinator_1_toReply', ''),
        'totalTransactions': Gauge('coordinator_1_totalTransactions', ''),
        'tailsTraversed': Gauge('coordinator_1_tailsTraversed', ''),
        'solid': Gauge('coordinator_1_solid', ''),
        'nonSolid': Gauge('coordinator_1_nonSolid', ''),
        'dnsCheck': Gauge('coordinator_1_dnsCheck', ''),
        'milestoneChange': Gauge('coordinator_1_milestoneChange', ''),
        'solidMilestoneChange': Gauge('coordinator_1_solidMilestoneChange', ''),
        'addNeighbors': Gauge('coordinator_1_addNeighbors', ''),
        'getNodeInfo': Gauge('coordinator_1_getNodeInfo', ''),
        'attachToTangle': Gauge('coordinator_1_attachToTangle', ''),
        'broadcastTransactions': Gauge('coordinator_1_broadcastTransactions', ''),
        'getBalances': Gauge('coordinator_1_getBalances', ''),
        'getInclusionStates': Gauge('coordinator_1_getInclusionStates', ''),
        'getNeighbors': Gauge('coordinator_1_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('coordinator_1_getNodeAPIConfiguration', ''),
        'getTips': Gauge('coordinator_1_getTips', ''),
        'getTransactionsToApprove': Gauge('coordinator_1_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('coordinator_1_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('coordinator_1_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('coordinator_1_removeNeighbors', ''),
        'storeTransactions': Gauge('coordinator_1_storeTransactions', ''),
        'getMissingTransactions': Gauge('coordinator_1_getMissingTransactions', ''),
        'checkConsistency': Gauge('coordinator_1_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('coordinator_1_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('coordinator_1_startSpamming', ''),
        'stopSpamming': Gauge('coordinator_1_stopSpamming', '')
    },
    'relayer_1': {
        'toProcess': Gauge('relayer_1_toProcess', ''),
        'toBroadcast': Gauge('relayer_1_toBroadcast', ''),
        'toRequest': Gauge('relayer_1_toRequest', ''),
        'toReply': Gauge('relayer_1_toReply', ''),
        'totalTransactions': Gauge('relayer_1_totalTransactions', ''),
        'tailsTraversed': Gauge('relayer_1_tailsTraversed', ''),
        'solid': Gauge('relayer_1_solid', ''),
        'nonSolid': Gauge('relayer_1_nonSolid', ''),
        'dnsCheck': Gauge('relayer_1_dnsCheck', ''),
        'milestoneChange': Gauge('relayer_1_milestoneChange', ''),
        'solidMilestoneChange': Gauge('relayer_1_solidMilestoneChange', ''),
        'addNeighbors': Gauge('relayer_1_addNeighbors', ''),
        'getNodeInfo': Gauge('relayer_1_getNodeInfo', ''),
        'attachToTangle': Gauge('relayer_1_attachToTangle', ''),
        'broadcastTransactions': Gauge('relayer_1_broadcastTransactions', ''),
        'getBalances': Gauge('relayer_1_getBalances', ''),
        'getInclusionStates': Gauge('relayer_1_getInclusionStates', ''),
        'getNeighbors': Gauge('relayer_1_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('relayer_1_getNodeAPIConfiguration', ''),
        'getTips': Gauge('relayer_1_getTips', ''),
        'getTransactionsToApprove': Gauge('relayer_1_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('relayer_1_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('relayer_1_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('relayer_1_removeNeighbors', ''),
        'storeTransactions': Gauge('relayer_1_storeTransactions', ''),
        'getMissingTransactions': Gauge('relayer_1_getMissingTransactions', ''),
        'checkConsistency': Gauge('relayer_1_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('relayer_1_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('relayer_1_startSpamming', ''),
        'stopSpamming': Gauge('relayer_1_stopSpamming', '')
    },
    'backend_1': {
        'toProcess': Gauge('backend_1_toProcess', ''),
        'toBroadcast': Gauge('backend_1_toBroadcast', ''),
        'toRequest': Gauge('backend_1_toRequest', ''),
        'toReply': Gauge('backend_1_toReply', ''),
        'totalTransactions': Gauge('backend_1_totalTransactions', ''),
        'tailsTraversed': Gauge('backend_1_tailsTraversed', ''),
        'solid': Gauge('backend_1_solid', ''),
        'nonSolid': Gauge('backend_1_nonSolid', ''),
        'dnsCheck': Gauge('backend_1_dnsCheck', ''),
        'milestoneChange': Gauge('backend_1_milestoneChange', ''),
        'solidMilestoneChange': Gauge('backend_1_solidMilestoneChange', ''),
        'addNeighbors': Gauge('backend_1_addNeighbors', ''),
        'getNodeInfo': Gauge('backend_1_getNodeInfo', ''),
        'attachToTangle': Gauge('backend_1_attachToTangle', ''),
        'broadcastTransactions': Gauge('backend_1_broadcastTransactions', ''),
        'getBalances': Gauge('backend_1_getBalances', ''),
        'getInclusionStates': Gauge('backend_1_getInclusionStates', ''),
        'getNeighbors': Gauge('backend_1_getNeighbors', ''),
        'getNodeAPIConfiguration': Gauge('backend_1_getNodeAPIConfiguration', ''),
        'getTips': Gauge('backend_1_getTips', ''),
        'getTransactionsToApprove': Gauge('backend_1_getTransactionsToApprove', ''),
        'getTransactionStrings': Gauge('backend_1_getTransactionStrings', ''),
        'interruptAttachingToTangle': Gauge('backend_1_interruptAttachingToTangle', ''),
        'removeNeighbors': Gauge('backend_1_removeNeighbors', ''),
        'storeTransactions': Gauge('backend_1_storeTransactions', ''),
        'getMissingTransactions': Gauge('backend_1_getMissingTransactions', ''),
        'checkConsistency': Gauge('backend_1_checkConsistency', ''),
        'wereAddressesSpentFrom': Gauge('backend_1_wereAddressesSpentFrom', ''),
        'startSpamming': Gauge('backend_1_startSpamming', ''),
        'stopSpamming': Gauge('backend_1_stopSpamming', '')
        }
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
