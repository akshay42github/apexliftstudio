# ApexLiftStudio - Django Gym Management System

A complete, production-ready gym management web application built with Django, featuring membership management, class booking, Stripe payments, and Google Maps integration.

## Assumptions Made

- SQLite for local dev, PostgreSQL for production
- DRF TokenAuthentication for API
- AOS.js for scroll animations
- Django's built-in User model with Profile extension
- Stripe test mode with webhook signature verification
- Simple class booking (no complex conflict resolution in MVP)

## Tech Stack

- **Backend**: Python 3.11+, Django 5.0+, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (dev)
- **Frontend**: HTML5, Tailwind CSS (CDN), Vanilla JavaScript, AOS.js
- **Payments**: Stripe Checkout & Webhooks
- **Maps**: Google Maps JavaScript API
- **Containerization**: Docker & Docker Compose

## Environment Variables

Create a `.env` file in the project root (use `.env.example` as template):
```env
# Django
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production/Docker)
DATABASE_URL=postgresql://apexlift:apexlift123@db:5432/apexliftdb

# Stripe (test keys)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Google Maps
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Email (optional, for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
```

## Quick Start (Local Development with SQLite)

This guide is for running the application locally with SQLite database (no PostgreSQL required).

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone and setup virtual environment**:
```bash
   cd apexliftstudio
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
```

2. **Install dependencies**:
```bash
   pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
   # Copy the example file
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # macOS/Linux
   
   # Edit .env file (optional for basic local dev)
   # You can use the default values for testing
```

4. **Run migrations**:
```bash
   python manage.py migrate
```

5. **Create superuser**:
```bash
   python manage.py createsuperuser
   
   # Or use demo credentials:
   # Username: admin
   # Email: admin@apexlift.com
   # Password: admin123
```

6. **Load demo data** (recommended):
```bash
   python manage.py seed_demo
```
   
   This will create:
   - Admin user (admin/admin123)
   - Test member (johndoe/testpass123)
   - 3 membership plans
   - 3 trainers
   - 2 locations
   - Multiple classes
   - 3 blog posts
   - 4 testimonials

7. **Collect static files**:
```bash
   python manage.py collectstatic --noinput
```

8. **Run development server**:
```bash
   python manage.py runserver
```

9. **Access the application**:
   - Homepage: http://localhost:8000/
   - Admin Panel: http://localhost:8000/admin/
   - API Root: http://localhost:8000/api/
   - Dashboard: http://localhost:8000/dashboard/ (login required)

### Demo Credentials

After running `seed_demo`:

**Admin User:**
- Username: `admin`
- Password: `admin123`

**Test Member:**
- Username: `johndoe`
- Password: `testpass123`

### Database Location

The SQLite database file will be created at: `apexliftstudio/db.sqlite3`

To reset the database, simply delete this file and run migrations again.

### Running Tests
```bash
python manage.py test
```

### Troubleshooting

**Issue: "No module named 'decouple'"**
```bash
pip install python-decouple
```

**Issue: "No module named 'PIL'"**
```bash
pip install Pillow
```

**Issue: Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**Issue: Database errors**
```bash
# Delete database and start fresh
rm db.sqlite3  # or delete manually on Windows
python manage.py migrate
python manage.py seed_demo
```

## Quick Start (Docker)

1. **Build and run**:
```bash
   cp .env.example .env
   # Edit .env if needed
   docker-compose up --build
```

2. **In another terminal, run migrations and seed data**:
```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   docker-compose exec web python manage.py seed_demo
```

3. **Access**: http://localhost:8000/

## Demo Credentials (Development Only)

**Admin User** (created by seed_demo command):
- Username: `admin`
- Password: `admin123`

**Test Member User** (created by seed_demo command):
- Username: `johndoe`
- Password: `testpass123`

## Running Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Stripe Testing

1. Use test keys in `.env` (get from https://dashboard.stripe.com/test/apikeys)
2. Test card numbers:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - Requires auth: `4000 0025 0000 3155`
3. Use any future expiry date and any CVC

### Testing Webhooks Locally
```bash
# Install Stripe CLI
stripe listen --forward-to localhost:8000/api/webhook/stripe/

# Use the webhook signing secret provided by Stripe CLI in your .env
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

## API Endpoints

### Public Endpoints
- `GET /api/plans/` - List membership plans
- `GET /api/locations/` - List gym locations
- `GET /api/classes/` - List classes (optional filters: ?date=YYYY-MM-DD&location=1)
- `POST /api/signup/` - Register new user
- `POST /api/login/` - Get authentication token

### Authenticated Endpoints (requires Token in header)
- `POST /api/classes/<id>/book/` - Book a class
- `POST /api/stripe/create-checkout/` - Create Stripe checkout session
- `GET /api/user/profile/` - Get user profile

### Webhook
- `POST /api/webhook/stripe/` - Stripe webhook handler

**Authentication Header**:
```
Authorization: Token <your-token-here>
```

## Project Structure
```
apexliftstudio/          # Django project settings
core/                    # Main application
├── models.py           # Database models
├── views.py            # Template views
├── api_views.py        # DRF API views
├── serializers.py      # DRF serializers
├── forms.py            # Django forms
├── admin.py            # Admin customization
└── tests.py            # Unit tests
```

## Deployment Notes

### Render.com / Railway.app

1. Set environment variables in dashboard
2. Use `Procfile` for web process
3. Run migrations on first deploy:
```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py seed_demo
```

### Docker Production

1. Update `docker-compose.yml` for production settings
2. Set `DEBUG=False` in `.env`
3. Configure proper `ALLOWED_HOSTS`
4. Use a secret management service for keys
5. Set up SSL/TLS with reverse proxy (nginx)

## Makefile Commands (Optional)
```makefile
.PHONY: run migrate test seed

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	python manage.py test

seed:
	python manage.py seed_demo

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
```

## Security Checklist for Production

- [ ] Change SECRET_KEY to a random secure value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS
- [ ] Set up proper CORS headers
- [ ] Configure CSP headers
- [ ] Use environment-based secrets management
- [ ] Enable Stripe webhook signature verification
- [ ] Set up rate limiting
- [ ] Configure proper logging

## License

MIT License