# taken from https://github.com/urbenlegend/netimpair/
# and heavily modified

"""
The MIT License (MIT)

Copyright (c) 2015 Benjamin Xiao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import datetime
import sys

from webnetem.throttler import Throttler
from webnetem.utils import call, check_call


class LinuxThrottler(Throttler):
    """Wrapper around netem module and tc command."""

    def _generate_filters(self, filter_list):
        filter_strings = []
        filter_strings_ipv6 = []
        for tcfilter in filter_list:
            filter_tokens = tcfilter.split(",")
            try:
                filter_string = ""
                filter_string_ipv6 = ""
                for token in filter_tokens:
                    token_split = token.split("=")
                    key = token_split[0]
                    value = token_split[1]
                    # Check for ipv6 addresses and add them to the appropriate
                    # filter string
                    if key == "src" or key == "dst":
                        if "::" in value:
                            filter_string_ipv6 += "match ip6 {0} {1} ".format(
                                key, value
                            )
                        else:
                            filter_string += "match ip {0} {1} ".format(key, value)
                    else:
                        filter_string += "match ip {0} {1} ".format(key, value)
                        filter_string_ipv6 += "match ip6 {0} {1} ".format(key, value)
                    if key == "sport" or key == "dport":
                        filter_string += "0xffff "
                        filter_string_ipv6 += "0xffff "
            except IndexError:
                self.logger.info("ERROR: Invalid filter parameters", file=sys.stderr)

            if filter_string:
                filter_strings.append(filter_string)
            if filter_string_ipv6:
                filter_strings_ipv6.append(filter_string_ipv6)

        return filter_strings, filter_strings_ipv6

    def initialize(self):
        """Set up traffic control."""
        if self.inbound:
            # Create virtual ifb device to do inbound impairment on
            check_call("/sbin/modprobe ifb")
            check_call(f"ip link set dev {self.nic} up")
            # Delete ingress device before trying to add
            call(f"tc qdisc del dev {self.real_nic} ingress")
            # Add ingress device
            check_call(f"tc qdisc replace dev {self.real_nic} ingress")
            # Add filter to redirect ingress to virtual ifb device
            check_call(
                f"tc filter replace dev {self.real_nic} parent ffff: protocol ip prio 1 "
                "u32 match u32 0 0 flowid 1:1 action mirred egress redirect "
                f"dev {self.nic}"
            )

        # Delete network impairments from any previous runs of this script
        call(f"tc qdisc del root dev {self.nic}")

        # Create prio qdisc so we can redirect some traffic to be unimpaired
        check_call(f"tc qdisc add dev {self.nic} root handle 1: prio")

        # Apply selective impairment based on include and exclude parameters
        self.logger.info("Including the following for network impairment:")
        include_filters, include_filters_ipv6 = self._generate_filters(self.include)
        for filter_string in include_filters:
            include_filter = (
                f"tc filter add dev {self.nic} protocol ip parent 1:0 "
                f"prio 3 u32 {filter_string}flowid 1:3"
            )
            check_call(include_filter)

        for filter_string_ipv6 in include_filters_ipv6:
            include_filter_ipv6 = (
                f"tc filter add dev {self.nic} protocol ipv6 "
                f"parent 1:0 prio 4 u32 {filter_string_ipv6}flowid 1:3"
            )
            check_call(include_filter_ipv6)

        self.logger.info("Excluding the following from network impairment:")
        exclude_filters, exclude_filters_ipv6 = self._generate_filters(self.exclude)
        for filter_string in exclude_filters:
            exclude_filter = (
                f"tc filter add dev {self.nic} protocol ip parent 1:0 "
                f"prio 1 u32 {filter_string}flowid 1:2"
            )
            check_call(exclude_filter)

        for filter_string_ipv6 in exclude_filters_ipv6:
            exclude_filter_ipv6 = (
                f"tc filter add dev {self.nic} protocol ipv6 "
                f"parent 1:0 prio 2 u32 {filter_string_ipv6}flowid 1:2"
            )
            check_call(exclude_filter_ipv6)

    def shape(self, options):
        # decide here if we call _netem or _rate
        self.logger.info("Setting network impairment:")
        self._start_packet_loss()

        return self.status

    def _start_packet_loss(
        self,
        loss_ratio=0,
        loss_corr=0,
        dup_ratio=0,
        delay=0,
        jitter=0,
        delay_jitter_corr=0,
        reorder_ratio=0,
        reorder_corr=0,
        toggle=None,
    ):
        """Enable packet loss.
        """
        check_call(f"tc qdisc add dev {self.nic} parent 1:3 handle 30: netem")
        impair_cmd = (
            f"tc qdisc change dev {self.nic} parent 1:3 handle 30: "
            f"netem loss {loss_ratio}% {loss_corr}% duplicate {dup_ratio}% "
            f"delay {delay}ms {jitter}ms {delay_jitter_corr}% "
            f"reorder {reorder_ratio}% {reorder_corr}%"
        )
        # Set network impairment
        check_call(impair_cmd)

    def _stop_packet_loss(self):
        check_call(f"tc qdisc change dev {self.nic} parent 1:3 handle 30: netem")
        self.logger.info(f"Impairment stopped timestamp: {datetime.datetime.today()}")

    def _start_packet_reorder(
        self, limit=0, buffer_length=2000, latency=20, toggle=None
    ):
        """Enable packet reorder.
        """
        check_call(
            f"tc qdisc add dev {self.nic} parent 1:3 handle 30: tbf rate 1000mbit "
            f"buffer {buffer_length} latency {latency}ms"
        )
        impair_cmd = (
            f"tc qdisc change dev {self.nic} parent 1:3 handle 30: tbf "
            f"rate {limit}kbit buffer {buffer_length} latency {latency}ms"
        )
        # Set network impairment
        check_call(impair_cmd)

    def _stop_packet_reorder(self):
        check_call(
            f"tc qdisc change dev {self.nic} parent 1:3 handle 30: tbf rate "
            f"1000mbit buffer {buffer_length} latency {latency}ms"
        )
        self.logger.info(f"Impairment stopped timestamp: {datetime.datetime.today()}")

    def teardown(self):
        """Reset traffic control rules."""
        if self.inbound:
            call(f"tc filter del dev {self.real_nic} parent ffff: protocol ip prio 1")
            call(f"tc qdisc del dev {self.real_nic} ingress")
            call("ip link set dev ifb0 down")
        call("tc qdisc del root dev {self.nic}")
        self.logger.info("Network impairment teardown complete.")
