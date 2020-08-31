import requests
import argparse


_SERVER = "http://localhost:8888"

actions =  {}

def status(options):
    return requests.get(options["server"], verify=not options["insecure"]).json()

actions["status"] = status


def reset(options):
    return requests.get(options["server"] + "/reset", verify=not options["insecure"]).json()

actions["reset"] = reset

def shape(options):
    return requests.post(options["server"] + "/shape",
            verify=not options["insecure"], json=options).json()

actions["shape"] = shape


def parse_args():
    """Parse command-line arguments."""
    argparser = argparse.ArgumentParser(description="Network Impairment Test Tool")

    argparser.add_argument(
        '-s', '--server',
        default=_SERVER,
        help='endpoint')

    argparser.add_argument(
        '-k', '--insecure',
        default=False,
        action="store_true",
        help='verify https certificate')

    subparsers = argparser.add_subparsers(
        title='impairments',
        dest='subparser_name',
        description='specify which impairment to enable',
        help='valid impairments')

    info_args = subparsers.add_parser("status",
            help="Get info")

    reset_args = subparsers.add_parser("reset",
            help="disable packet loss")
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
    args = parse_args()
    if args.subparser_name is None:
        action = "status"
    else:
        action = args.subparser_name
    return actions[action](vars(args))


if __name__ == "__main__":
    main()
