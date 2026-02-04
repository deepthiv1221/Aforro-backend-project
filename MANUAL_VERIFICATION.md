# Manual Verification Guide for Aforro Backend Assignment

This guide will help you manually verify that all components are working correctly.

## Prerequisites
- Python 3.10+
- Virtual environment activated
- Docker Desktop (for full testing)

## Step-by-Step Manual Verification

### 1. Verify File Structure ✅

First, check that all required files exist:

```bash
# Check main files
dir *.py
dir *.txt
dir *.yml
dir *.md

# Check app structure
dir apps\products
dir apps\stores  
dir apps\orders
dir apps\search
dir project
dir tests
```

**Expected files:**
- ✅ `manage.py`
- ✅ `requirements.txt` 
- ✅ `Dockerfile`
- ✅ `docker-compose.yml`
- ✅ `README.md`
- ✅ `project/settings.py`
- ✅ All app directories with models, views, serializers

### 2. Verify Python Dependencies ✅

```bash
# Check installed packages
pip list | findstr -i "django\|celery\|redis\|psycopg2"

# Should show:
# Django (6.0.2)
# djangorestframework (3.16.1)
# celery (5.6.2)
# redis (6.4.0)
# psycopg2-binary (2.9.11)
```

### 3. Test Individual Components

#### A. Test Models (without database)
```bash
python -c "from products.models import Category, Product; print('✓ Products models imported')"
python -c "from stores.models import Store, Inventory; print('✓ Stores models imported')"
python -c "from orders.models import Order, OrderItem; print('✓ Orders models imported')"
```

#### B. Test Serializers
```bash
python -c "from products.serializers import ProductSerializer; print('✓ Product serializer works')"
python -c "from stores.serializers import StoreSerializer; print('✓ Store serializer works')"
python -c "from orders.serializers import OrderSerializer; print('✓ Order serializer works')"
```

#### C. Test Celery Tasks
```bash
python -c "from project.tasks import send_order_confirmation_email; result = send_order_confirmation_email(1, 'Test Store', 'test@example.com'); print(f'✓ Celery task result: {result[\"status\"]}')"
```

#### D. Test Cache Configuration
```bash
python -c "from django.core.cache import cache; cache.set('test', 'value', 300); print(f'✓ Cache set: {cache.get(\"test\")}')"
```

### 4. Full Docker-Based Testing

#### A. Start Docker Services
```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# Should show:
# db          Running
# redis       Running  
# web         Running
# celery      Running
# celery-beat Running
```

#### B. Run Database Migrations
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Should show successful migration output
```

#### C. Generate Sample Data
```bash
# Generate test data
docker-compose exec web python manage.py seed_data

# Should create categories, products, stores, and inventory
```

#### D. Test API Endpoints
```bash
# Start the development server
docker-compose exec web python manage.py runserver 0.0.0.0:8000

# In another terminal, test endpoints:

# Test inventory listing (should show cached data)
curl http://localhost:8000/stores/1/inventory/

# Test order creation
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{"store_id": 1, "items": [{"product_id": 1, "quantity_requested": 2}]}'

# Test order listing
curl http://localhost:8000/stores/1/orders/

# Test product search
curl "http://localhost:8000/api/search/products/?q=phone"

# Test autocomplete
curl "http://localhost:8000/api/search/suggest/?q=iph"
```

### 5. Test Celery Workers

#### A. Check Celery Worker Status
```bash
# View Celery worker logs
docker-compose logs celery

# Should show worker startup messages
```

#### B. Test Async Tasks Manually
```bash
# Run a Celery task
docker-compose exec web python -c "
from project.tasks import generate_daily_inventory_summary
result = generate_daily_inventory_summary()
print('Task result:', result['status'])
"
```

### 6. Test Caching

#### A. Verify Cache Configuration
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

#### B. Test Cache Behavior
```bash
# First request (should populate cache)
curl http://localhost:8000/stores/1/inventory/ | findstr "from_cache"

# Second request (should use cache)  
curl http://localhost:8000/stores/1/inventory/ | findstr "from_cache"
```

### 7. Run Test Suite

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific test modules
docker-compose exec web python manage.py test tests.test_models
docker-compose exec web python manage.py test tests.test_apis
docker-compose exec web python manage.py test tests.test_cache
```

### 8. Check Docker Logs

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs db
docker-compose logs redis
docker-compose logs celery
```

## Verification Checklist

### ✅ Core Functionality
- [ ] Models import and validate correctly
- [ ] Serializers work properly
- [ ] API endpoints respond with correct data
- [ ] Order processing logic works (validation, status updates)
- [ ] Inventory management functions correctly
- [ ] Search and filtering work as expected
- [ ] Autocomplete returns relevant results

### ✅ Engineering Requirements
- [ ] Redis caching implemented and working
- [ ] Celery tasks execute successfully
- [ ] Docker containers start and run properly
- [ ] Database migrations apply correctly
- [ ] Sample data generation works
- [ ] All tests pass

### ✅ Performance & Quality
- [ ] Database queries are optimized (no N+1 issues)
- [ ] Caching improves response times
- [ ] Error handling is comprehensive
- [ ] API responses are properly formatted
- [ ] Code follows Django best practices

## Troubleshooting Common Issues

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database service
docker-compose restart db
```

### Redis Connection Issues
```bash
# Check Redis status
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Celery Worker Issues
```bash
# Check worker status
docker-compose ps celery

# View worker logs
docker-compose logs celery

# Restart worker
docker-compose restart celery
```

### API Endpoint Issues
```bash
# Check web service
docker-compose ps web

# View web logs
docker-compose logs web

# Test internal connectivity
docker-compose exec web python manage.py shell
```

## Success Criteria

✅ **All tests pass** (at least 3-5 tests as required)
✅ **All Docker services running** without errors
✅ **API endpoints respond** with correct JSON data
✅ **Database operations work** (create, read, update, delete)
✅ **Caching functions** as expected
✅ **Async tasks execute** successfully
✅ **Documentation is complete** and accurate

If all these criteria are met, your Aforro Backend Assignment is fully implemented and working correctly!