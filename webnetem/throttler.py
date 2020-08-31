import logging


class Throttler:
    def __init__(self, nic, inbound=False, include=None, exclude=None, logger=None):
        self.inbound = inbound
        self.include = include
        self.exclude = exclude
        self.nic = nic
        if logger is None:
            logger = logging.getLogger("webnetem")
        self.logger = logger
        self.status = {"throttling": False}

    def initialize(self):
        pass
