#!/usr/bin/env python3

import csv
import datetime
import logging
import re
from typing import Any

import feedparser
import icalendar
import requests
import requests.auth

import config

# URLs to access our Meetup group's events.
MEETUP_EVENTS_URL = "https://www.meetup.com/improvbouldermeetup/events"
MEETUP_EVENTS_RSS_URL = f"{MEETUP_EVENTS_URL}/rss"
MEETUP_EVENTS_ICAL_URL = f"{MEETUP_EVENTS_URL}/ical"

# Wordpress meta_key for the Meetup event ID.
WP_META_KEY_MEETUP_EVENT_ID = "_meetup_event_id"


class Event:
    def __init__(
        self,
        title: str,
        description: str,
        location: str,
        url: str,
        meetup_id: int,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ) -> None:
        self.title = title
        self.description = description
        self.location = location
        self.url = url
        self.meetup_id = meetup_id
        self.start_time = start_time
        self.end_time = end_time

    @classmethod
    def from_ical_vevent(cls, vevent: icalendar.cal.Event) -> "Event":
        return cls(
            str(vevent["summary"]),
            # TODO: Remove the group name and datetime from the beginning of
            # the description, and maybe remove the URL from the end.
            str(vevent["description"]),
            str(vevent["location"]),
            vevent["url"],
            _extract_meetup_id(vevent),
            vevent["dtstart"].dt,
            vevent["dtend"].dt,
        )

    def print(self) -> None:
        print("EVENT")
        print(f"Title: {self.title}")
        print(f"Description: {self.description}")
        print(f"Location: {self.location}")
        print(f"URL: {self.url}")
        print(f"Meetup ID: {self.meetup_id}")
        print(f"Start time: {self.start_time}")
        print(f"End time: {self.end_time}")


def _extract_meetup_id(vevent: icalendar.cal.Event) -> int:
    uid = str(vevent["uid"])
    regex = re.compile(r"^event_(\d+)@meetup\.com$")
    m = regex.search(uid)
    if not m:
        raise ValueError("Failed to extract Meetup ID from vevent uid %s", uid)
    capture_group = m.group(1)
    return int(capture_group)


def download_meetup_ical() -> icalendar.Calendar:
    response = requests.get(MEETUP_EVENTS_ICAL_URL)
    if response.status_code != 200:
        raise Exception(
            "Failed to get Events ical from %s (code %d): %s",
            MEETUP_EVENTS_ICAL_URL,
            response.status_code,
            response.text,
        )
    return icalendar.Calendar.from_ical(response.text)


def download_meetup_ical_events() -> list[icalendar.Event]:
    calendar = download_meetup_ical()
    vevents = calendar.walk("VEVENT")
    return [Event.from_ical_vevent(vevent) for vevent in vevents]


def download_meetup_rss() -> list[dict[str, Any]]:
    events = feedparser.parse(MEETUP_EVENTS_RSS_URL).entries
    logging.info(
        "Downloaded %s Meetup events from %s: %s",
        len(events),
        MEETUP_EVENTS_URL,
        events,
    )
    return events


def get_event_id_from_meetup_event(event: dict[str, Any]) -> str:
    """Extract the event ID from a Meetup event JSON."""
    # TODO
    return ""


def _get_wordpress_events_api_url(wordpress_url: str) -> str:
    """Return a Wordpress URL we can send HTTP requeasts for events to."""
    # TODO: Use urlparse (or urllib.prase, or whatever it's called these days)
    return wordpress_url.rstrip("/") + "/wp-json/wp/v2/events"


def get_wordpress_event(
    cfg: config.Config,
    meetup_event_id: str,
) -> dict[str, Any] | None:
    """Check Wordpress to see whether a Meetup event already exists."""
    params = {
        "meta_key": WP_META_KEY_MEETUP_EVENT_ID,
        "meta_value": meetup_event_id,
    }
    response = requests.get(
        _get_wordpress_events_api_url(cfg.wordpress_url),
        params=params,
        auth=cfg.wordpress_credentials,
    )
    if response.status_code == 200:
        events = response.json()
        if len(events) > 1:
            raise Exception(
                "Found %d events with meetup event ID %s: %s",
                len(events),
                meetup_event_id,
                events,
            )
        return events[0]
    return None


def upload_event_to_wordpress(
    cfg: config.Config,
    title: str,
    description: str,
) -> None:
    event_data = {
        "title": title,
        "content": description,
        "status": "publish",
    }
    logging.info("Trying to create event: %s", event_data)
    response = requests.post(
        _get_wordpress_events_api_url(cfg.wordpress_url),
        json=event_data,
        auth=cfg.wordpress_credentials,
    )
    if response.status_code == 201:
        logging.info("Event '%s' created successfully.", title)
    else:
        logging.warning("Failed to create event '%s': %s", title, response.text)

