# -*- coding: utf-8 -*-
"""
Module description
"""
from context import telegram_notifier


notifier = telegram_notifier.NotificationHandler()

notifier.emit("This is a test notification.")
