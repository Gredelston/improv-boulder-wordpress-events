"""Interface with our Wordpress website."""

import logging
from typing import Any

import requests

import config
import exceptions

# Wordpress meta_key for the Meetup event ID.
WP_META_KEY_MEETUP_EVENT_ID = "_meetup_event_id"

def _get_wordpress_events_api_url(wordpress_url: str) -> str:
    """Return a Wordpress URL we can send HTTP requeasts for events to."""
    return wordpress_url.rstrip("/") + "/wp-json/wp/v2/events"


def get_wordpress_events(
    cfg: config.Config,
    params: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a list of events already on Wordpress."""
    response = requests.get(
        _get_wordpress_events_api_url(cfg.wordpress_url),
        params=params,
        auth=cfg.wordpress_credentials,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_wordpress_event_by_id(
    cfg: config.Config,
    event_id: str,
) -> dict[str, Any] | None:
    """Return the pre-existing Wordpress event with the given ID."""
    params = {
        "meta_key": WP_META_KEY_MEETUP_EVENT_ID,
        "meta_value": event_id,
    }
    wp_events = get_wordpress_events(cfg, params)
    if not wp_events:
        return None
    if len(wp_events) > 1:
        raise exceptions.InvalidResponseException(
            f"Found {len(wp_events)} events with ID {event_id}: {wp_events}")
    return wp_events[0]


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
