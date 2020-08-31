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
        self.status = {"throttling": False}
        return self.status

    def shape(self, options):
        if self.status["throttling"]:
            self.teardown()
        self.netem.netem(
            loss_ratio=int(options.get("loss_ratio", 0)),
            loss_corr=int(options.get("loss_corr", 0)),
            dup_ratio=int(options.get("dup_ratio", 0)),
            delay=int(options.get("delay", 0)),
            jitter=int(options.get("jitter", 0)),
            delay_jitter_corr=int(options.get("delay_jitter_corr", 0)),
            reorder_ratio=int(options.get("reorder_ratio", 0)),
            reorder_corr=int(options.get("reorder_corr", 0)))

        self.status.update(options)
        self.status["throttling"] = True
        return self.status
