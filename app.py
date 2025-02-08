import yaml
import argparse
import logging
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import calendar

def load_yaml(file_path):
    """Loads event data from a YAML file."""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data.get('events', [])  # Return only the list of events

def adjust_to_weekend(date):
    """Ensures the given date falls on a Saturday or Sunday."""
    # Check if the input is a string, if so, convert it to a datetime object
    if isinstance(date, str):
        date_obj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    else:
        date_obj = date  # Assume it's already a datetime object

    if date_obj.weekday() not in [5, 6]:  # If not Saturday (5) or Sunday (6)
        date_obj += timedelta(days=(5 - date_obj.weekday()) if date_obj.weekday() < 5 else (6 - date_obj.weekday()))
    return date_obj.strftime('%Y-%m-%dT%H:%M:%S')

def create_ics(events, output_file='output_calendar'):
    """Generates an ICS file from the given event data."""
    cal = Calendar()
    cal.add('prodid', '-//Custom Calendar//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')

    for event in events:
        vevent = Event()
        adjusted_start = adjust_to_weekend(event['start'])
        adjusted_end = adjust_to_weekend(event['end'])

        vevent.add('summary', event['summary'])
        vevent.add('dtstart', datetime.strptime(adjusted_start, '%Y-%m-%dT%H:%M:%S'))
        vevent.add('dtend', datetime.strptime(adjusted_end, '%Y-%m-%dT%H:%M:%S'))
        vevent.add('location', event.get('location', ''))
        vevent.add('description', event.get('description', ''))
        vevent.add('uid', event.get('uid', f"{event['summary'].replace(' ', '_')}@custom.com"))

        if 'recurrence' in event:
            rrule = {'FREQ': event['recurrence']['freq'], 'COUNT': event['recurrence'].get('count')}
            if 'byday' in event['recurrence']:
                rrule['BYDAY'] = event['recurrence']['byday']  # Capture the byday attribute
            vevent.add('rrule', rrule)

        if 'alarm' in event and event['alarm']:
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', timedelta(days=-event['alarm']['days_before']))
            alarm.add('description', 'Event Reminder')
            vevent.add_component(alarm)

        cal.add_component(vevent)

    output_file = f"{output_file}.ics"
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())

    logging.info(f"ICS file generated: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an ICS file from a YAML configuration.")
    parser.add_argument('--config', type=str, required=True, help="Path to the YAML configuration file.")
    parser.add_argument('--name', type=str, required=True, help="Output ICS filename.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    events = load_yaml(args.config)
    create_ics(events, args.name)
