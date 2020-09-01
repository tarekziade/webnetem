import os
import requests
import argparse


_SERVER = "http://localhost:8080"


class NetemService:
    def __init__(self, options):
        self.options = options
        self.server = options.server
        self.verify = not options.insecure
        self.key = options.key

    def _req(self, verb="GET", api="", **kw):
        options = vars(self.options)
        headers = {}
        if self.key is not None:
            headers["X-WEBNETEM-KEY"] = self.key
        verb = verb.lower()
        rkw = dict(kw)
        if verb == "post":
            rkw["json"] = options
        func = getattr(requests, verb, "get")
        return func(self.server + api, verify=self.verify, headers=headers,
                **rkw).json()

    def status(self):
        return self._req()

    def reset(self):
        return self._req("GET", "/reset")

    def shape(self):
        return self._req("POST", "/shape")

    def run_action(self):
        if self.options.subparser_name is None:
            action = "status"
        else:
            action = self.options.subparser_name
        return getattr(self, action)()


def parse_args():
    """Parse command-line arguments."""
    argparser = argparse.ArgumentParser(description="Network Impairment Test Tool")

    argparser.add_argument("-s", "--server", default=_SERVER, help="endpoint")

    argparser.add_argument(
        "--key",
        type=str,
        help="API key (you can also set WEBNETEM-KEY in the env)",
        default=os.environ.get("WEBNETEM-KEY"),
    )

    argparser.add_argument(
        "-k",
        "--insecure",
        default=False,
        action="store_true",
        help="verify https certificate",
    )

    subparsers = argparser.add_subparsers(
        title="impairments",
        dest="subparser_name",
        description="specify which impairment to enable",
        help="valid impairments",
    )

    info_args = subparsers.add_parser("status", help="Get info")

    reset_args = subparsers.add_parser("reset", help="disable packet loss")
    # loss args
    netem_args = subparsers.add_parser("shape", help="enable packet loss")
    netem_args.add_argument(
        "--loss_ratio",
        type=int,
        default=0,
        help="specify percentage of packets that will be lost",
    )
    netem_args.add_argument(
        "--loss_corr",
        type=int,
        default=0,
        help="specify a correlation factor for the random packet loss",
    )
    # dup args
    netem_args.add_argument(
        "--dup_ratio",
        type=int,
        default=0,
        help="specify percentage of packets that will be duplicated",
    )
    # delay/jitter args
    netem_args.add_argument(
        "--delay", type=int, default=0, help="specify an overall delay for each packet"
    )
    netem_args.add_argument(
        "--jitter", type=int, default=0, help="specify amount of jitter in milliseconds"
    )
    netem_args.add_argument(
        "--delay_jitter_corr",
        type=int,
        default=0,
        help="specify a correlation factor for the random jitter",
    )
    # reorder args
    netem_args.add_argument(
        "--reorder_ratio",
        type=int,
        default=0,
        help="specify percentage of packets that will be reordered",
    )
    netem_args.add_argument(
        "--reorder_corr",
        type=int,
        default=0,
        help="specify a correlation factor for the random reordering",
    )

    return argparser.parse_args()


def main():
    server = NetemService(parse_args())
    return server.run_action()


if __name__ == "__main__":
    main()
