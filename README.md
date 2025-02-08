# WSTI Calendar Integration 📅

Automatically sync your WSTI class schedule with Google Calendar. This Python application scrapes the WSTI course schedule and creates corresponding events in your Google Calendar, making it easier to keep track of your classes.

## ✨ Features

- Automatic schedule scraping from WSTI website
- Seamless Google Calendar integration
- Duplicate event detection to avoid redundancy
- Support for course details including:
  - Course name and type
  - Room number
  - Lecturer information
  - Time slots
- Automatic time zone handling (Europe/Warsaw)
- Custom reminder settings (15 minutes before class)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/wsti-calendar
cd wsti-calendar
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Calendar API:
   1. Visit [Google Cloud Console](https://console.cloud.google.com/)
   2. Create a new project or select an existing one
   3. Enable the Google Calendar API for your project
   4. Go to "Credentials" and create a new OAuth 2.0 Client ID
   5. Download the credentials file as `credentials.json`
   6. Place `credentials.json` in the project root directory

4. Configure your credentials:
```bash
cp credentials.example.json credentials.json
```

## 🔧 Configuration

1. Update `credentials.json` with your Google API credentials
2. Modify the schedule URL in `Class2Calendar.py` if needed:
```python
url = 'https://www.wsti.pl/wp-content/uploads/2025/02/4ADI.htm'
```

## 📖 Usage

Simply run the script:
```bash
python Class2Calendar.py
```

The script will:
1. Fetch the schedule from WSTI website
2. Authenticate with Google Calendar
3. Create events for each class session
4. Skip any existing events to avoid duplicates

## 🔑 Authentication

On first run, the script will:
1. Open a browser window for Google authentication
2. Ask for permission to modify your calendar
3. Save the authentication token locally in `token.pickle`

## 📝 Event Details

Each calendar event includes:
- Title: Course name and type
- Location: Room number
- Description: Lecturer information and day of the week
- Time: Start and end time with proper timezone
- Reminder: 15-minute popup notification

## ⚠️ Important Notes

- Keep your `credentials.json` and `token.pickle` files secure
- Never commit these files to version control
- The script assumes the WSTI schedule is in Polish time (Europe/Warsaw)

## 🛠️ Dependencies

- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- requests
- beautifulsoup4
- python-dotenv
- pytz

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.