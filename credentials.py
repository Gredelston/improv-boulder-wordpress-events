#!/usr/bin/env

import json
from pathlib import Path
from typing import Any

import requests.auth

CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"

def load_credentials() -> dict[str, Any]:
    """Load the credentials JSON file."""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)

def _assert_dict_has_key(
    d: dict[str, Any],
    key: str,
    dict_name: str = "dict",
) -> None:
    """If key is not in d, complain helpfully but without leaking keys."""
    if key not in d:
        raise KeyError(f"Key {key} not in {dict_name}: {d.keys()}")

def get_wordpress_credentials() -> requests.auth.HTTPBasicAuth:
    """Return the password needed to interact with Wordpress."""
    credentials = load_credentials()
    _assert_dict_has_key(credentials, "wordpress", dict_name="credentials.json")
    wordpress = credentials["wordpress"]
    _assert_dict_has_key(
        wordpress, "username", dict_name="wordpress")
    _assert_dict_has_key(
        wordpress, "application-password", dict_name="wordpress")
    return requests.auth.HTTPBasicAuth(
        wordpress["username"], wordpress["application-password"])

if __name__ == "__main__":
    print(get_wordpress_application_password())
