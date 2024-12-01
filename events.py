"""Deal with events in a platform-agnostic way."""

import datetime


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
