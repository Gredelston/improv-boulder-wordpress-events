#!/usr/bin/env python3

import csv
import logging
from typing import Any

import feedparser
import icalendar
import requests
import requests.auth

import credentials

# URLs to access our Meetup group's events.
MEETUP_EVENTS_URL = "https://www.meetup.com/improvbouldermeetup/events"
MEETUP_EVENTS_RSS_URL = f"{MEETUP_EVENTS_URL}/rss"
MEETUP_EVENTS_ICAL_URL = f"{MEETUP_EVENTS_URL}/ical"

# URL of our Wordpress site.
WORDPRESS_URL = "https://improvboulder-staging.dreamhosters.com"
WORDPRESS_API_URL = f"{WORDPRESS_URL}/wp-json/wp/v2/events"

# Wordpress meta_key for the Meetup event ID.
WP_META_KEY_MEETUP_EVENT_ID = "_meetup_event_id"

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
    return calendar.walk("VEVENT")

def download_meetup_rss() -> list[dict[str, Any]]:
    events = feedparser.parse(MEETUP_EVENTS_RSS_URL).entries
    logging.info(
        "Downloaded %s Meetup events from %s: %s",
        len(events),
        EVENTS_URL,
        events,
    )

def get_event_id_from_meetup_event(event: dict[str, Any]) -> str:
    """Extract the event ID from a Meetup event JSON."""


def get_wordpress_event(meetup_event_id: str) -> dict[str, Any] | None:
    """Check Wordpress to see whether a Meetup event already exists."""
    params = {
        "meta_key": WP_META_KEY_MEETUP_EVENT_ID,
        "meta_value": meetup_event_id,
    }
    response = requests.get(
        WORDPRESS_API_URL,
        params=params,
        auth=credentials.get_wordpress_credentials(),
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
    title: str,
    description: str,
) -> None:
    wp_credentials = credentials.get_wordpress_credentials()
    event_data = {
        "title": title,
        "content": description,
        "status": "publish",
    }
    logging.info("Trying to create event: %s", event_data)
    response = requests.post(
        WORDPRESS_API_URL,
        json=event_data,
        auth=credentials.get_wordpress_credentials(),
    )
    if response.status_code == 201:
        logging.info("Event '%s' created successfully.", title)
    else:
        logging.warning("Failed to create event '%s': %s", title, response.text)

if __name__ == "__main__":
    print(download_meetup_ical())
