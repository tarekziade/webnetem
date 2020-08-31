from webnetem.utils import call, check_call
from webnetem.throttler import Throttler


class MacosThrottler(Throttler):
    def initialize(self):
        self.teardown()
        cmds = [
            "dnctl -q flush",
            "dnctl -q pipe flush",
            "dnctl pipe 1 config delay 0ms noerror",
            "dnctl pipe 2 config delay  0ms noerror",
            # should restrict to the web app, not the whole OS
            'echo "dummynet in all pipe 1\ndummynet out all pipe 2"  | pfctl -f -',
        ]

        for cmd in cmds:
            call(cmd)

    def teardown(self):
        cmds = [
            "dnctl -q flush",
            "dnctl -q pipe flush",
            "pfctl -f /etc/pf.conf",
            "pfctl -E",
            "pfctl -d",
        ]

        for cmd in cmds:
            call(cmd)

        return {}

    def shape(self, options):
        # XXX control input
        bw_up = options["up"]["bw"]
        delay_up = options["up"]["delay"]
        bw_dn = options["down"]["bw"]
        delay_dn = options["down"]["delay"]

        cmds = [
            f"dnctl pipe 1 config bw {bw_up} delay {delay_up}",
            f"dnctl pipe 2 config bw {bw_dn} delay {delay_dn}",
            "pfctl -E",
        ]

        for cmd in cmds:
            call(cmd)

        return {}
