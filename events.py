"""Deal with events in a platform-agnostic way."""

import csv
import datetime
import logging
from typing import Any

import requests

import config

# Wordpress meta_key for the Meetup event ID.
WP_META_KEY_MEETUP_EVENT_ID = "_meetup_event_id"


class Event:
    """Platform-agnostic representation of an event."""
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
        """Declare basic Event attributes."""
        self.title = title
        self.description = description
        self.location = location
        self.url = url
        self.meetup_id = meetup_id
        self.start_time = start_time
        self.end_time = end_time

    def print(self) -> None:
        """Print all the info about an Event."""
        print("EVENT")
        print(f"Title: {self.title}")
        print(f"Description: {self.description}")
        print(f"Location: {self.location}")
        print(f"URL: {self.url}")
        print(f"Meetup ID: {self.meetup_id}")
        print(f"Start time: {self.start_time}")
        print(f"End time: {self.end_time}")
        print()


def _get_wordpress_events_api_url(wordpress_url: str) -> str:
    """Return a Wordpress URL we can send HTTP requeasts for events to."""
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
