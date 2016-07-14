"""
Module containing the Slack logging handler.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

import os, logging
import requests


class SlackHandler(logging.Handler):
    def __init__(self, webhook_url, channel = None, username = None, level = logging.NOTSET):
        super(SlackLogHandler, self).__init__(level)
        self._webhook_url = webhook_url
        self._channel = channel
        # If no username was given, use the hostname
        self._username = username or os.uname()[1]

    def emit(self, record):
        try:
            # We want to add any exception info as an attachment rather than as part
            # of the log message
            # So we temporarily remove it from the record while we get the message
            exc_info, exc_text = record.exc_info, record.exc_text
            record.exc_info = record.exc_text = None
            content = { 'text' : self.format(record) }
            record.exc_info, record.exc_text = exc_info, exc_text
            # Set username and channel
            content['username'] = self._username
            if self._channel:
                content['channel'] = self._channel
            # If there is exception information, attach it
            if record.exc_info:
                formatter = self.formatter or logging.Formatter()
                # Wrap the traceback so it is formatted
                exc_text = '```' + formatter.formatException(record.exc_info) + '```'
                content['attachments'] = [
                    {
                        'color' : 'danger',
                        'mrkdwn_in' : ['text'],
                        'title' : str(exc_info[1]),
                        'text' : exc_text,
                    },
                ]
            # Send the request
            requests.post(self._webhook_url, json = content)
        except:
            self.handleError(record)
