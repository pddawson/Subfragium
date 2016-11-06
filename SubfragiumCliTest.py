import argparse


main_parser = argparse.ArgumentParser(add_help=True)
type = main_parser.add_subparsers(title="target",
                    dest="service_command")
action = type.add_subparsers(title="action",dest="action")

target = type.add_parser("target", help="target")
poller = type.add_parser("poller", help="target")
oid = type.add_parser("oid", help="target")

targetAdd = target.add_subparsers(title="action",dest="action")
targetDelete = target.add_subparsers(title="delete",dest="action")
action_parser = targetAdd.add_parser("action", help="action")

args = main_parser.parse_args()