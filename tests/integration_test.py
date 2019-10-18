# -*- coding: utf-8 -*-
"""
You were probably hoping to see more here. Sorry.
"""
from context import telegram_notifier


notifier = telegram_notifier.NotificationHandler()

notifier.emit("This is a test notification.")
