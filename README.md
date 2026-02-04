# Aforro Backend Assignment

A complete Django backend system for product inventory management with REST APIs, Redis caching, Celery async processing, Docker containerization, and advanced search capabilities.

## 🌟 Key Features

### Core Functionality
- **Product Management**: Categories, products with pricing and descriptions.
- **Store Management**: Multiple store locations with inventory tracking.
- **Order Processing**: Transaction-safe order creation with stock validation.
- **Search & Filtering**: Advanced product search with multiple filters and relevance ranking.
- **Autocomplete**: Fast product title suggestions with prefix-match priority.

### Engineering & Technical Features
- **API Documentation (Swagger/OpenAPI)**: Interactive API documentation for easy exploration.
- **PostgreSQL Advanced Search**: Ranked full-text search using PostgreSQL `SearchVector`.
- **Redis Caching**: Optimized inventory listing with automatic cache invalidation on stock changes.
- **Rate Limiting**: Security-focused throttling for the Autocomplete API (20 requests/minute).
- **Asynchronous Tasks (Celery)**: Background processing for order confirmations and summaries.
- **Dockerized Environment**: Full multi-container setup (Django, Postgres, Redis, Celery).

## 📂 Project Structure

```
project/
├── orders/             # Order and OrderItem models, creation logic
├── products/           # Category and Product models, search logic
├── stores/             # Store and Inventory models, stock management
├── search/             # Enhanced Search and Autocomplete APIs
├── project/            # Main project configuration (settings.py, urls.py)
├── tests/              # Comprehensive test suite (Models, APIs, Cache, Throttling)
├── Dockerfile          # Python application image definition
├── docker-compose.yml  # Multi-service coordination
├── requirements.txt    # Python package dependencies
└── README.md           # Documentation
```

## 🚀 Quick Start (Docker)

The fastest way to run the project is using Docker Compose.

1. **Build and start services:**
   ```bash
   docker-compose up -d --build
   ```

2. **Apply migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Seed sample data (Generates 1000+ products, 20+ stores, and inventory):**
   ```bash
   docker-compose exec web python manage.py seed_data
   ```

The application will be available at [http://localhost:8000](http://localhost:8000).

## 📖 API Documentation

The API is fully documented using Swagger/OpenAPI. You can explore and test the endpoints directly from your browser:

- **Swagger UI**: [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **ReDoc**: [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)

## 🔍 Advanced Search Details

The search API (`GET /api/search/products/`) utilizes **PostgreSQL Full-Text Search**:
- **Relevance Ranking**: Results are ranked based on matches in Title (High), Category (Medium), and Description (Low).
- **Filters**: Support for `category`, `price range`, `store_id`, and `in_stock`.
- **Efficiency**: Uses indexed vectors for high-performance querying.

## 🛡️ Security & Performance

- **Rate Limiting**: The autocomplete endpoint is throttled to prevent abuse (20 requests per minute per IP).
- **Caching**: Store inventory listings are cached in Redis to minimize database hits.
- **Atomic Transactions**: All order creations use `transaction.atomic()` to ensure data consistency between order records and inventory updates.

## 🧪 Running Tests

The project includes **26 tests** covering all core requirements and enhancements.

**Run inside Docker:**
```bash
docker-compose exec web python manage.py test tests
```

**Run Locally (requires SQLite setup):**
```bash
python manage.py test tests --settings=local_settings
```

## 🛠️ Local Development (Non-Docker)

1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. Use local settings: `python manage.py migrate --settings=local_settings`
5. Run server: `python manage.py runserver --settings=local_settings`

---
*Developed for the Aforro Backend Developer Assignment (Round 2).*