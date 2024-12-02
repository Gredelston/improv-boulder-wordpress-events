"""Deal with events in a platform-agnostic way."""

import datetime
import enum
import typing

import exceptions


class EventCategory(enum.StrEnum):
    """A type of event."""
    WORKSHOPS = "workshops"
    CLASSES = "classes"
    SHOWS = "shows"


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

    def _is_show(self) -> bool:
        """Determine whether the event is a show."""
        return "SHOW" in self.title.upper()

    def _is_class(self) -> bool:
        """Determine whether the event is a class."""
        return "CLASS" in self.title.upper()

    def _is_workshop(self) -> bool:
        """Determine whether the event is a workshop."""
        return "WORKSHOP" in self.title.upper()

    def get_categories(self) -> list[EventCategory]:
        """Determine the event category (show, class, workshop)."""
        categories = []
        if self._is_show():
            categories.append(EventCategory.SHOWS)
        if self._is_class():
            categories.append(EventCategory.CLASSES)
        if self._is_workshop():
            categories.append(EventCategory.WORKSHOPS)
        return categories
