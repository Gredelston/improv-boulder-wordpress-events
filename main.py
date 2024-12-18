#!/usr/bin/env python3

"""Download events from Meetup and upload them to Wordpress Events Calendar."""

import argparse
import logging
import sys

import config
import meetup
import wordpress


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
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
    """Main script logic."""
    args = parse_args(argv)
    logging.getLogger().setLevel(args.log_level)

    cfg = config.load()
    meetup_events = meetup.download_events(cfg)
    for event in meetup_events:
        wordpress.upload_event(cfg, event, dryrun=args.dryrun)


if __name__ == "__main__":
    main(sys.argv[1:])
