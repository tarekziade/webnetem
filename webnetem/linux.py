from webnetem.throttler import Throttler
from webnetem.netimpair import NetemInstance


class LinuxThrottler(Throttler):

    def initialize(self):
        self.netem = NetemInstance(
            self.nic, self.inbound, self.include, self.exclude)
        self.netem.initialize()
        return {}

    def teardown(self):
        self.netem.stop_netem()
        self.netem.teardown()
        return self.status

    def shape(self, options):
        self.netem.netem(
            loss_ratio=0,
            loss_corr=0,
            dup_ratio=0,
            delay=1000,
            jitter=0,
            delay_jitter_corr=0,
            reorder_ratio=0,
            reorder_corr=0)

        return self.status
