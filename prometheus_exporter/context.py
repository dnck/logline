# -*- coding: utf-8 -*-
#pylint: skip-file
"""
This script is a testing utility used to append the '../app' directory (where the primary .py executables live) to the system path so that they can be
imported during the tests.
"""
import os
import sys


SCRIPT_DIRNAME, SCRIPT_FILENAME = os.path.split(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(SCRIPT_DIRNAME)
SRC_DIR0 = os.path.join(PROJECT_ROOT_DIR, "alert_utilities")
SRC_DIR1 = os.path.join(PROJECT_ROOT_DIR, "prometheus_exporter")

sys.path.insert(0, SRC_DIR0)
sys.path.insert(0, SRC_DIR1)

import telegram_notifier
