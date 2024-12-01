# Import Meetup Events... But For Free

## Prerequisites

This script was developed using python3.11, but anything python3.9+ should work.
In addition, you must install the following non-standard libraries:

* requests
* icalendar
* feedparser (TODO: remove this dependency)
* types-requests

TODO: Set up a virtual environment that contains these libraries.

## Config setup

Create a config file, `config.json`, with the following structure:

{
	"meetup": {
		"events_url": string
	},
	"wordpress": {
		"url": string,
		"username": string,
		"application-password": string
	}
}
