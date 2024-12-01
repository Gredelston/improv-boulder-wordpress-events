#!/usr/bin/env python3

import argparse
import logging
import sys

import config
import events


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dryrun",
        "-d",
        help="If given, don't actually push changes to Wordpress.",
        action="store_true",
    )
    parser.add_argument(
        "--log-level",
        choices=("ERROR", "WARNING", "INFO", "DEBUG"),
        help="Set the minimum logging level to write to stdout. (Default: INFO)",
        default="INFO",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> None:
    args = parse_args(argv)
    logging.getLogger().setLevel(args.log_level)
    
    cfg = config.load()
    meetup_events = events.download_meetup_ical_events()
    for event in meetup_events:
        event.print()
        print()


if __name__ == "__main__":
    main(sys.argv[1:])
