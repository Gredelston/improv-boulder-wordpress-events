"""Interface with our Wordpress website."""

import functools
import logging
from typing import Any

import requests

import config
import events
import exceptions

# Wordpress meta_key for the Meetup event ID.
# This is exposed in the Wordpress theme's functions.php.
WP_META_KEY_MEETUP_EVENT_ID = "meetup_event_id"

def _get_wordpress_api_url(wordpress_url: str, endpoint: str) -> str:
    """Return a Wordpress URL we can send HTTP requeasts for events to."""
    endpoint = endpoint.lstrip("/")
    return wordpress_url.rstrip("/") + f"/wp-json/wp/v2/{endpoint}"


@functools.cache
def _get_category_ids(cfg: config.Config) -> dict[events.EventCategory, int]:
    """Determine the Wordpress category ID for each EventCategory.

    This function is cached so that we don't waste time GET-ing the category IDs
    every time we want to publish an event. For now that's fine because the
    script doesn't run for a long time, so the categories are unlikely to change
    while the script runs. But if someone were to modify this script to be
    long-running, then we should invalidate the cache after some timeout.
    """
    response = requests.get(
        _get_wordpress_api_url(cfg.wordpress_url, "tribe_events_cat"),
        timeout=30,
    )
    ids_by_category: dict[events.EventCategory, int] = {}
    for category_json in response.json():
        name = category_json["name"]
        category = events.EventCategory[name.upper()]
        ids_by_category[category] = category_json["id"]
    return ids_by_category


def get_wordpress_events(
    cfg: config.Config,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a list of events already on Wordpress."""
    response = requests.get(
        _get_wordpress_api_url(cfg.wordpress_url, "events"),
        params=params,
        auth=cfg.wordpress_credentials,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_wordpress_event_by_meetup_id(
    cfg: config.Config,
    meetup_id: str,
) -> dict[str, Any] | None:
    """Return the pre-existing Wordpress event with the given Meetup ID."""
    params = {"meta_key": WP_META_KEY_MEETUP_EVENT_ID, "meta_value": meetup_id}
    wp_events = get_wordpress_events(cfg, params)
    if not wp_events:
        return None
    if len(wp_events) > 1:
        raise exceptions.InvalidResponseException(
            f"Found {len(wp_events)} events with ID {event_id}: {wp_events}")
    return wp_events[0]


def upload_event(
    cfg: config.Config,
    event: events.Event,
    dryrun: bool = False,
) -> None:
    """Upload an event to Wordpress."""
    # TODO: why am I unable to view my published events on Wordpress?
    if not event.get_categories():
        raise exceptions.UndeterminedEventCategoryException(event.title)
    post_data = {
        "title": event.title,
        "description": event.description,
        "status": "publish",
        "timezone": event.start_time.tzinfo.zone,
        "start_date": event.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": event.end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "website": event.url,
        "tribe_events_cat": [
            _get_category_ids(cfg)[c] for c in event.get_categories()],
        "meta": {WP_META_KEY_MEETUP_EVENT_ID: str(event.meetup_id)},
    }
    api_url = _get_wordpress_api_url(cfg.wordpress_url, "/events")
    logging.info("Trying to create event: %s", event.title)
    logging.debug(
        "Sending POST request to %s with data: %s", api_url, post_data)
    response: requests.Response
    if dryrun:
        logging.info("DRYRUN: Skipping POST to %s with %s", api_url, post_data)
        response = requests.Response()
        response.status_code = 201
    else:
        response = requests.post(
            api_url,
            json=post_data,
            auth=cfg.wordpress_credentials,
            timeout=30,
        )
    logging.debug("Response: %s", response.text)
    response.raise_for_status()
    logging.info("Successfully created event: %s", event.title)

