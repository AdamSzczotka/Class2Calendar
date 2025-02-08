import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Zakres uprawnień dla Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Autoryzacja i utworzenie usługi Google Calendar."""
    creds = None

    # Sprawdzenie czy istnieje zapisany token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Jeśli brak poświadczeń lub są nieważne
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Zapisanie poświadczeń do wykorzystania później
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def event_exists(service, start_time, subject, room):
    """Sprawdza czy wydarzenie już istnieje w kalendarzu."""
    # Szukamy wydarzeń w tym samym czasie
    start = start_time.isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=(start_time + timedelta(minutes=1)).isoformat() + 'Z',
        q=f"{subject} {room}"  # Szukamy po nazwie przedmiotu i sali
    ).execute()

    return len(events_result.get('items', [])) > 0


def add_event(service, zajecia):
    """Dodaje pojedyncze zajęcia do kalendarza."""
    # Parsowanie daty i czasu
    data = zajecia['date']
    start_time, end_time = zajecia['time'].split(' - ')

    # Tworzenie pełnych dat z czasem
    start_datetime = datetime.strptime(f"{data} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{data} {end_time}", "%Y-%m-%d %H:%M")

    # Sprawdzenie czy wydarzenie już istnieje
    if event_exists(service, start_datetime, zajecia['subject'], zajecia['room']):
        print(f"Wydarzenie już istnieje: {zajecia['subject']} {start_datetime}")
        return None

    # Tworzenie wydarzenia
    event = {
        'summary': f"{zajecia['subject']} ({zajecia['type']})",
        'location': f"Sala {zajecia['room']}",
        'description': f"Prowadzący: {zajecia['lecturer']}\nDzień: {zajecia['day']}",
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'Europe/Warsaw',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'Europe/Warsaw',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 15},
            ]
        }
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Dodano zajęcia: {zajecia['subject']} ({start_time})")
        return event
    except HttpError as error:
        print(f"Wystąpił błąd podczas dodawania wydarzenia: {error}")
        return None


def main():
    pass


if __name__ == '__main__':
    main()
