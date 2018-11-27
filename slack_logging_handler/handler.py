# -*- coding: utf-8 -*-
"""
Module containing the Slack logging handler.
"""
__author__ = "Matt Pryor"
__date__ = "21/11/17"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__author__ = "Matt Pryor"
import os
import logging
import requests


class SlackHandler(logging.Handler):
    '''Logging handler to feed log messages to a Slack channel via webhook URL
    '''

    def __init__(self, webhook_url, channel = None, username = None,
                 level = logging.NOTSET):
        super(SlackHandler, self).__init__(level)
        self._webhook_url = webhook_url
        self._channel = channel
        # If no username was given, use the hostname
        self._username = username or os.uname()[1]

    def emit(self, record):
        try:
            # We want to add any exception info as an attachment rather than as
            # part of the log message
            # So we temporarily remove it from the record while we get the
            # message
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
                exc_text = '```' + formatter.formatException(record.exc_info) +\
                           '```'
                content['attachments'] = [
                    {
                        'color' : 'danger',
                        'mrkdwn_in' : ['text'],
                        'title' : 'Exception traceback',
                        'text' : exc_text,
                    },
                ]
                
            # Add workaround where caller wants to pass a string from an
            # exception.  This is done via the extra keyword to 
            # log.[debug|info|warning|error|exception]
            elif hasattr(record, 'slack_exception_attachment'):
                content['attachments'] = [
                    {
                        'color' : 'danger',
                        'mrkdwn_in' : ['text'],
                        'title' : 'Exception traceback',
                        'text' : record.slack_exception_attachment,
                    },
                ]
                                
            # Send the request
            requests.post(self._webhook_url, json = content)
        except Exception:
            self.handleError(record)
