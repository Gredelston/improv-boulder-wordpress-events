#!/usr/bin/env

import json
import logging
from pathlib import Path
from typing import Any

import requests.auth

CONFIG_FILE = Path(__file__).parent / "config.json"


class Config:
    """Config settings to run the script in any environment."""

    def __init__(self, config_json: dict[str, Any]) -> None:
        """Initialize a Config object that reads from a json dict."""
        self._json = config_json

    @property
    def wordpress(self) -> dict[str, Any]:
        """Return wordpress config."""
        _get(self._json, "wordpress", dict_name="config")
        return self._json["wordpress"]

    @property
    def wordpress_url(self) -> str:
        """Return the Wordpress URL."""
        wordpress = self.wordpress
        _get(wordpress, "url", dict_name="wordpress config")
        return wordpress["url"]

    @property
    def wordpress_credentials(self) -> requests.auth.HTTPBasicAuth:
        """Return credentials used to access the Wordpress API."""
        wordpress = self.wordpress
        _get(wordpress, "username", dict_name="wordpress config")
        _get(wordpress, "application-password", dict_name="wordpress config")
        return requests.auth.HTTPBasicAuth(
            wordpress["username"], wordpress["application-password"]
        )


def load(config_file: Path = CONFIG_FILE) -> Config:
    """Load the config JSON file."""
    logging.debug("Loading config file: %s", config_file)
    if not config_file.exists():
        raise FileNotFoundError(config_file)
    with open(config_file, "r") as f:
        return Config(json.load(f))


def _get(d: dict[str, Any], key: str, dict_name: str = "dict") -> Any:
    """Return a value from a dict.

    If the key is not present, then raise a more helpful KeyError that will help
    the user debug their config.json. In particular, reveal what other keys are
    in the dict, but don't leak the values because they might contain secrets.
    """
    if key not in d:
        raise KeyError(f"Key {key} not in {dict_name}: {d.keys()}")
    return d[key]
