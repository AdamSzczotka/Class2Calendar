import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pytz

# Zakres uprawnień dla Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Autoryzacja i utworzenie usługi Google Calendar."""
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def event_exists(service, start_time, timezone='Europe/Warsaw'):
    tz = pytz.timezone(timezone)
    start_time = tz.localize(start_time)

    start = start_time.isoformat()
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=(start_time + timedelta(minutes=1)).isoformat()
    ).execute()

    return len(events_result.get('items', [])) > 0


def add_event(service, zajecia):
    """Dodaje pojedyncze zajęcia do kalendarza."""
    try:
        data = zajecia['date']
        if ' - ' not in zajecia['time']:
            print(f"Nieprawidłowy format czasu dla zajęć: {zajecia}")
            return None

        start_time, end_time = zajecia['time'].split(' - ')

        start_datetime = datetime.strptime(
            f"{data} {start_time.strip()}",
            "%Y-%m-%d %H:%M"
        )
        end_datetime = datetime.strptime(
            f"{data} {end_time.strip()}",
            "%Y-%m-%d %H:%M"
        )

        if event_exists(service, start_datetime):
            print(
                f"Wydarzenie już istnieje: "
                f"{zajecia['subject']} {start_datetime}"
            )
            return None

        event = {
            'summary': f"{zajecia['subject']} ({zajecia['type']})",
            'location': f"Sala {zajecia['room']}",
            'description': (
                f"Prowadzący: {zajecia['lecturer']}\n"
                f"Dzień: {zajecia['day']}"
            ),
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

        event = (
                service.events()
                .insert(calendarId='primary', body=event)
                .execute()
            )
        print(f"Dodano zajęcia: {zajecia['subject']} ({start_time})")
        return event
    except ValueError as e:
        print(f"Błąd przetwarzania daty/czasu dla zajęć: {zajecia}")
        print(f"Szczegóły błędu: {str(e)}")
        return None
    except HttpError as error:
        print(f"Wystąpił błąd podczas dodawania wydarzenia: {error}")
        return None


def is_valid_time_format(time_str):
    """Sprawdza czy string zawiera prawidłowy format czasu (HH:MM - HH:MM)"""
    if not time_str or ' - ' not in time_str:
        return False
    try:
        start, end = time_str.split(' - ')
        datetime.strptime(start.strip(), "%H:%M")
        datetime.strptime(end.strip(), "%H:%M")
        return True
    except ValueError:
        return False


def main():
    url = 'https://www.wsti.pl/wp-content/uploads/2025/02/4ADI.htm'
    response = requests.get(url)
    response.encoding = 'windows-1250'

    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all("table")

    schedule = []
    current_date = None
    current_day = None

    for table in tables:
        rows = table.find_all("tr")

        for row in rows:
            cols = [
                col.get_text(strip=True).replace("\r\n", " ")
                for col in row.find_all("td")
            ]

            if not cols or (len(cols) >= 5 and "Prowadzący" in cols[0]):
                if schedule:
                    break
                continue

            if "DATA" in cols or "GRUPA" in cols:
                continue

            if len(cols) >= 2 and "-" in cols[0] and len(cols[0]) == 10:
                current_date = cols[0]
                current_day = cols[1]
                continue

            if len(cols) >= 4 and current_date:
                if "BRAK ZAJĘĆ" in cols:
                    continue

                # Sprawdź czy format czasu jest prawidłowy
                if not is_valid_time_format(cols[0]):
                    continue

                if len(cols) == 4:
                    godzina = cols[0]
                    przedmiot = cols[1]
                    rodzaj = cols[2]
                    sala = cols[3]
                    prowadzacy = "Nieznany"
                else:
                    godzina = cols[0]
                    przedmiot = cols[1]
                    rodzaj = cols[2]
                    sala = cols[3]
                    prowadzacy = cols[4] if len(cols) > 4 else "Nieznany"

                schedule.append({
                    "date": current_date,
                    "day": current_day,
                    "time": godzina,
                    "subject": przedmiot,
                    "type": rodzaj,
                    "room": sala,
                    "lecturer": prowadzacy
                })

        if schedule and not cols:
            break

    try:
        service = get_calendar_service()
        print("Połączono z Google Calendar")

        for zajecia in schedule:
            add_event(service, zajecia)

        print("Zakończono dodawanie zajęć do kalendarza")

    except Exception as e:
        print(f"Wystąpił błąd: {str(e)}")


if __name__ == '__main__':
    main()
