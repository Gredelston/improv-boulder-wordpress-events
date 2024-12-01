"""Interface with the Meetup website."""

import logging
import re
from typing import Any

import feedparser
import icalendar
import requests

import config
import events


class MeetupRequestException(Exception):
    """Something went wrong when firing an HTTP request to Meetup."""


def _download_ical(cfg: config.Config) -> icalendar.Calendar:
    """Download the iCal file containing all Meetup events."""
    ical_url = cfg.meetup_events_url.rstrip("/") + "/ical"
    response = requests.get(ical_url, timeout=30)
    if response.status_code != 200:
        raise MeetupRequestException(
            f"Failed to get Events ical from {ical_url} "
            "(code {response.status_code}): {response.text}"
        )
    return icalendar.Calendar.from_ical(response.text)


def _download_rss(cfg: config.Config) -> list[dict[str, Any]]:
    """Download and parse the RSS feed containing all Meetup events.

    NOTE: The RSS feed doesn't seem as useful as the iCal format, since it
    doesn't include as much information -- for example, it doesn't even have
    the event date. We might delete this method.
    """
    rss_url = cfg.meetup_events_url.rstrip("/") + "/rss"
    entries = feedparser.parse(rss_url).entries
    logging.info(
        "Downloaded %s Meetup events from %s: %s",
        len(entries),
        rss_url,
        entries,
    )
    return entries


def _create_event_from_ical_vevent(vevent: icalendar.cal.Event) -> events.Event:
    """Convert an iCal vevent into a platform-agnostic Event."""
    return events.Event(
        str(vevent["summary"]),
        # TODO: Remove the group name and datetime from the beginning of
        # the description, and maybe remove the URL from the end.
        str(vevent["description"]),
        str(vevent["location"]),
        vevent["url"],
        _extract_event_id_from_vevent(vevent),
        vevent["dtstart"].dt,
        vevent["dtend"].dt,
    )


def _extract_event_id_from_vevent(vevent: icalendar.cal.Event) -> int:
    uid = str(vevent["uid"])
    regex = re.compile(r"^event_(\d+)@meetup\.com$")
    m = regex.search(uid)  # pylint: disable=invalid-name
    if not m:
        raise ValueError(f"Failed to extract Meetup ID from vevent uid {uid}")
    capture_group = m.group(1)
    return int(capture_group)


def download_events(cfg: config.Config) -> list[events.Event]:
    """Download all events from Meetup."""
    calendar = _download_ical(cfg)
    vevents = calendar.walk("VEVENT")
    return [_create_event_from_ical_vevent(vevent) for vevent in vevents]
