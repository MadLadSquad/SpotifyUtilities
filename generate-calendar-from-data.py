#!/usr/bin/env python3
import recurring_ical_events
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
from pathlib import Path

import os
import json
import pytz

calendar = Calendar()
calendar.add("prodid", "-//modus mio calendar//madladsquad.com//")
calendar.add("version", "2.0")

data = json.loads(open("artists.json", "r").read())
for item in data:
    date = item["release_date"].split("-")
    if (len(date) < 3):
        continue

    event = Event()
    event["RRULE"] = "FREQ=YEARLY" # Repeat event every year on the same date
    event.add("summary", item["name"])
    event.add("title", item["name"])
    event.add("name", item["name"])
    event.add("description", f"{item['name']} release date")
    event.add("dtstart", datetime(int(date[0]), int(date[1]), int(date[2]), 12, 0, 0, tzinfo=pytz.utc))
    event.add("dtend", datetime(int(date[0]), int(date[1]), int(date[2]), 12, 1, 0, tzinfo=pytz.utc))
    calendar.add_component(event)

f = open("releases.ics", "wb")
f.write(calendar.to_ical())
f.close()
