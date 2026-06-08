# Med Voice Assistant Backend

A Django backend for booking doctor appointments via a voice-to-text frontend.

## Setup

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Seed initial doctors:
   ```bash
   python manage.py seed_doctors
   ```
4. Start the server:
   ```bash
   python manage.py runserver 8000
   ```

## Testing the Backend

1. Open `test_frontend.html` in your web browser (or navigate to it directly)
2. The frontend will auto-detect the backend connection
3. Use the interface to:
   - View available doctors
   - List existing appointments
   - Create new appointments with structured data
   - Test voice booking with simulated STT transcripts

## API Endpoints

All endpoints are prefixed with `/api/`

- `GET /api/doctors/`
- `GET /api/appointments/`
- `POST /api/appointments/`
- `POST /api/voice/book/`

## Appointment Creation

### Structured Appointment (POST /api/appointments/)

```json
{
  "doctorId": 1,
  "patientName": "John Doe",
  "date": "2026-06-10",
  "time": "10:30",
  "symptoms": "Headache and dizziness"
}
```

### Voice-Based Booking (POST /api/voice/book/)

The frontend can send JSON from STT results. The backend will:
- Extract doctor name from transcript
- Parse date and time using regex
- Create the appointment

Example:

```json
{
  "transcript": "Book an appointment with Dr. Aisha Khan on 2026-06-10 at 10:30 for headache",
  "patientName": "John Doe",
  "symptoms": "Headache"
}
```

## Project Structure

```
medvoice/
├── settings.py       # Django configuration & CORS setup
├── urls.py          # Main URL router
├── wsgi.py          # Production server entry
└── asgi.py          # Async server entry

bookings/
├── models.py        # Doctor & Appointment models
├── views.py         # API view functions
├── urls.py          # App URL routing
├── admin.py         # Admin panel registration
└── management/
    └── commands/
        └── seed_doctors.py  # Initialize sample doctors

test_frontend.html   # Standalone testing interface
```

## Database

SQLite database at `db.sqlite3` (auto-created)

### Models

- **Doctor**: name, specialty, location
- **Appointment**: doctor (FK), patient_name, date, time, symptoms, created_at

### Switching to External Database

When your friend builds a dedicated database (PostgreSQL, MySQL, MongoDB, etc.):

1. Copy `.env.example` to `.env`
2. Update environment variables with your database credentials:
   ```bash
   DB_ENGINE=postgresql
   DB_NAME=medvoice_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=database.example.com
   DB_PORT=5432
   ```
3. Restart the server:
   ```bash
   python manage.py runserver 8000
   ```

**Supported Databases**:
- SQLite (default, local)
- PostgreSQL
- MySQL
- MongoDB (with djongo)

See `medvoice/db_config.py` for configuration details and examples.

## Admin Panel

Access at `http://localhost:8000/admin`

Default Django admin can be created with:
```bash
python manage.py createsuperuser
```
