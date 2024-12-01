"""Deal with events in a platform-agnostic way."""

import datetime
import logging
from typing import Any

import requests

import config

# Wordpress meta_key for the Meetup event ID.
WP_META_KEY_MEETUP_EVENT_ID = "_meetup_event_id"


class InvalidResponseException(Exception):
    """An HTTP request returned an unexpected response."""


class Event:  # pylint: disable=too-few-public-methods
    """Platform-agnostic representation of an event."""

    def __init__(  # pylint: disable=too-many-arguments
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
    event_id: str,
) -> dict[str, Any] | None:
    """Check Wordpress to see whether a event already exists on Wordpress."""
    params = {
        "meta_key": WP_META_KEY_MEETUP_EVENT_ID,
        "meta_value": event_id,
    }
    response = requests.get(
        _get_wordpress_events_api_url(cfg.wordpress_url),
        params=params,
        auth=cfg.wordpress_credentials,
        timeout=30,
    )
    response.raise_for_status()
    events = response.json()
    if not events:
        return None
    if len(events) > 1:
        raise InvalidResponseException(
            f"Found {len(events)} events with ID {event_id}: {events}"
        )
    return events[0]


def upload_event_to_wordpress(
    cfg: config.Config,
    title: str,
    description: str,
) -> None:
    """Upload an event to Wordpress."""
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
        timeout=30,
    )
    if response.status_code == 201:
        logging.info("Event '%s' created successfully.", title)
    else:
        logging.warning("Failed to create event '%s': %s", title, response.text)
