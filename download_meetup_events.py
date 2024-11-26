#!/usr/bin/env python3

from typing import Any

import feedparser

# URL of our Meetup group's RSS feed for events.
EVENTS_URL = "https://www.meetup.com/improvbouldermeetup/events/rss/"

def download_meetup_events() -> list[dict[str, Any]]:
    return feedparser.parse(EVENTS_URL).entries

if __name__ == "__main__":
    events = download_meetup_events()
    event0 = events[0]
    for k, v in event0.items():
        print(f"{k}: {v}")
