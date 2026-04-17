# Buchi Pet Adoption Backend

Backend API for the Buchi pet adoption platform. This service allows users to search for adoptable pets from both a local PostgreSQL database and TheDogAPI, register as customers, and submit adoption requests.

## Overview

Buchi is a hybrid pet adoption system that aggregates pet listings from:
- Local PostgreSQL database (for pets directly added to the platform)
- TheDogAPI external service (for extended dog listings)

The system includes customer management with phone-based deduplication, adoption request tracking with rate limiting, and analytics reporting.

## Technology Stack

- **Language**: Python 3.11
- **Framework**: Django 5.0.3 with Django REST Framework
- **Database**: PostgreSQL 15
- **API Documentation**: Swagger/OpenAPI (drf-spectacular)
- **External Integration**: TheDogAPI
- **Deployment**: Docker & Docker Compose
- **Testing**: Django test framework

## Features

### Core Functionality
- **Pet Management**: Create pets with photo uploads (auto-optimized to 800x800)
- **Unified Search**: Query local database and TheDogAPI simultaneously, with local results prioritized
- **Customer Registration**: Phone-based deduplication prevents duplicate accounts
- **Adoption Workflow**: Submit adoption requests with automatic rate limiting (5 per day per customer)
- **Adoption Tracking**: Retrieve adoption requests filtered by date range

### Bonus Features
- **Analytics Reporting**: Generate reports showing adopted pet types and weekly adoption trends
- **Photo Optimization**: Automatic image resizing and compression on upload
- **Redis Caching**: 10-minute TTL on external API responses
- **Ethiopian Phone Validation**: Supports 09XXXXXXXX and +251XXXXXXXXX formats

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- A free API key from [TheDogAPI](https://thedogapi.com)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/buchi-pet-finder-service.git
cd buchi-pet-finder-service
```

2. Create environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` and add your DogAPI key:
```bash
DOG_API_KEY=your-actual-api-key-here
```

4. Start the application:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

### Accessing the Application

- **API Base URL**: http://localhost:8000/api/
- **Swagger Documentation**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/ (create superuser first)

## API Endpoints

### 1. Create Pet
```
POST /api/pets/
Content-Type: multipart/form-data

Parameters:
- type: string (Dog, Cat, Bird, Other)
- gender: string (male, female)
- size: string (small, medium, large, xlarge)
- age: string (baby, young, adult, senior)
- good_with_children: boolean
- uploaded_images: file[] (one or more images)

Response:
{
  "status": "success",
  "pet_id": "uuid-string"
}
```

### 2. Search Pets
```
GET /api/pets/?type=Dog&gender=male&limit=5

Query Parameters:
- type: string (optional)
- gender: string[] (optional)
- size: string[] (optional)
- age: string[] (optional)
- good_with_children: boolean (optional)
- limit: integer (required)

Response:
{
  "status": "success",
  "pets": [
    {
      "id": "uuid-or-external-id",
      "type": "Dog",
      "gender": "male",
      "size": "small",
      "age": "baby",
      "good_with_children": true,
      "photos": ["/media/path.jpg"],
      "source": "local"
    }
  ]
}
```

### 3. Add Customer
```
POST /api/customers/
Content-Type: application/json

{
  "name": "Customer Name",
  "phone": "0911223344"
}

Response:
{
  "status": "created" or "already_exists",
  "customer_id": "uuid-string",
  "message": "..."
}
```

### 4. Request Adoption
```
POST /api/adoptions/
Content-Type: application/json

{
  "pet_id": "uuid-or-external-id",
  "pet_source": "local",
  "customer_name": "Customer Name",
  "customer_phone": "0911223344"
}

Response:
{
  "status": "success",
  "adoption_id": "uuid-string"
}
```

### 5. Get Adoption Requests
```
GET /api/adoptions/requests/?from_date=2026-04-01&to_date=2026-04-17

Response:
{
  "status": "success",
  "data": [
    {
      "customer_id": "uuid",
      "customer_name": "Name",
      "customer_phone": "09XXXXXXXX",
      "pet_id": "uuid",
      "pet_type": "Dog",
      "pet_gender": "male",
      "pet_size": "small",
      "pet_age": "baby",
      "pet_good_with_children": true,
      "requested_at": "2026-04-15T10:30:00Z"
    }
  ]
}
```

### 6. Generate Report (Bonus)
```
POST /api/reports/generate/
Content-Type: application/json

{
  "from_date": "2026-04-01",
  "to_date": "2026-04-17"
}

Response:
{
  "status": "success",
  "data": {
    "adopted_pet_types": {
      "Dog": 5,
      "Cat": 2
    },
    "weekly_adoption_requests": {
      "2026-04-01": 3,
      "2026-04-08": 4
    }
  }
}
```

## API Documentation

- **Postman Collection**: [View on Postman](https://www.postman.com/meazamisgina/workspace/buchi-pet-adoption-api/collection/45826698-da48576f-3f4a-4007-94f7-f9589f97b50c)
- **Published Documentation**: [API Docs](https://meaza-misgina.docs.buildwithfern.com/buchi-pet-adoption-api/introduction)
- **Swagger UI**: http://localhost:8000/api/docs/

## Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test pets
docker-compose exec web python manage.py test adoptions
```
## Project Structure

```
buchi-pet-finder-service/
├── buchi/                 # Django project configuration
│   ├── settings.py        # Environment-aware settings
│   ├── urls.py            # API routing and Swagger setup
│   └── wsgi.py            # WSGI entry point
├── pets/                  # Pet management module
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py        # TheDogAPI integration
│   └── utils.py           # Photo optimization
├── customers/             # Customer registration
├── adoptions/             # Adoption workflow
│   ├── models.py
│   ├── views.py
│   └── utils.py           # Rate limiting
├── reports/               # Analytics (bonus)
├── docker-compose.yml     # Multi-service configuration
├── Dockerfile             # Production-ready build
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Environment Variables

The application requires environment variables for configuration. Copy `.env.example` to `.env` and configure:

| Variable | Purpose | Required |
|----------|---------|----------|
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Enable debug mode | Yes |
| DATABASE_URL | PostgreSQL connection | Yes |
| DOG_API_KEY | TheDogAPI authentication | Yes (for external search) |
| REDIS_URL | Redis cache connection | No (defaults to locmem) |
| MAX_ADOPTIONS_PER_DAY | Rate limit per customer | No (default: 5) |

## Engineering Decisions

### Local-First Search Results
The search endpoint prioritizes local database results over external API results, as specified in the requirements. This ensures pets directly added to the platform get maximum visibility.

### Customer Deduplication Strategy
Instead of requiring pre-registration, the adoption endpoint accepts customer name and phone number and automatically handles deduplication. This reduces API calls and improves user experience while maintaining data integrity.

### Photo Optimization
All uploaded photos are automatically resized to a maximum of 800x800 pixels and converted to JPEG format with 85% quality. This balances image quality with storage efficiency and load times.

### Rate Limiting Implementation
Rate limiting uses Django's cache framework with a 24-hour TTL. This provides flexibility to switch between in-memory caching (development) and Redis (production) without code changes.

## Production Deployment

The Dockerfile is configured for production deployment:
- Multi-stage build to minimize image size
- Gunicorn WSGI server
- Non-root user for security
- Static file collection

For production:
1. Set `DEBUG=False`
2. Configure a strong `SECRET_KEY`
3. Use a production PostgreSQL instance
4. Add Redis for caching

## Future Improvements

- Add authentication for admin operations
- Implement email notifications for adoption requests
- Integrate TheCatAPI for broader cat listings
- Add pet status tracking (available, pending, adopted)
- Implement advanced search with full-text search

## Author

**Meaza Misgina**  
Internship Candidate, Kifiya Financial Technology  
Email: misginameaza@gmail.com
GitHub: meazamisgina

---
*This project was developed as part of the Kifiya Financial Technology internship assessment.*
```
