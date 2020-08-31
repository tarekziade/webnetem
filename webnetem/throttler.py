import logging


class Throttler:
    def __init__(self, nic, inbound=False, include=None, exclude=None, logger=None):
        self.inbound = inbound
        self.include = include if include is not None else ["src=0/0", "src=::/0"]
        self.exclude = exclude
        self.nic = "ifb1" if inbound else nic
        self.real_nic = nic
        if logger is None:
            logger = logging.getLogger("webnetem")
        self.logger = logger
        self.status = {"throttling": False}

    def initialize(self):
        pass
