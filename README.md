# Improv Boulder Wordpress Events

This script allows us to import events from Meetup into Wordpress.

Normally we would need to pay for Meetup Pro to access the Meetup API, but we
can get by with the freely available iCal download. Likewise, normally we would
need to pay for the Wordpress Events Calendar pro subscription to schedule
imports, but this script lets us post events via direct HTTP requests.

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
