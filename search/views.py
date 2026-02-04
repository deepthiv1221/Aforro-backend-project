from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.core.paginator import Paginator
from products.models import Product
from products.serializers import ProductSerializer
from stores.models import Inventory


@api_view(['GET'])
def search_products(request):
    """
    Search products with filtering, sorting, and pagination.
    Uses PostgreSQL Full-Text Search if available, otherwise falls back to icontains.
    """
    from django.db import connection
    
    # Get query parameters
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    store_id = request.GET.get('store_id')
    in_stock = request.GET.get('in_stock')
    sort_by = request.GET.get('sort_by', 'relevance')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    # Start with all products
    products = Product.objects.all()
    
    # Check if using PostgreSQL
    is_postgres = connection.vendor == 'postgresql'
    
    # Apply keyword search
    if query:
        if is_postgres:
            # Advanced PostgreSQL Full-Text Search
            # Create a search vector combining title, description, and category name
            from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
            
            # Weighted search: Title (A) > Category (B) > Description (C)
            vector = (
                SearchVector('title', weight='A') +
                SearchVector('category__name', weight='B') +
                SearchVector('description', weight='C')
            )
            search_query = SearchQuery(query)
            
            # Filter and annotate with rank
            products = products.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(rank__gte=0.1)  # Only reasonably relevant results
            
            # If sorting by relevance, use the rank
            if sort_by == 'relevance':
                products = products.order_by('-rank')
        else:
            # Fallback for SQLite/Other DBs
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
    
    # Apply category filter
    if category:
        products = products.filter(category__name__icontains=category)
    
    # Apply price range filters
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Apply in_stock filter
    if in_stock:
        if store_id:
            products = products.filter(
                inventories__store_id=store_id,
                inventories__quantity__gt=0
            ).distinct()
        else:
            products = products.filter(
                inventories__quantity__gt=0
            ).distinct()
    
    # Apply sorting (if not already sorted by relevance in Postgres block)
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'newest':
        products = products.order_by('-id')
    elif sort_by == 'relevance' and not (query and is_postgres):
        # Default fallback for relevance if no query or not postgres
        products = products.order_by('title')
    elif sort_by not in ['price', 'newest', 'relevance']:
         products = products.order_by('title')

    # Apply pagination
    paginator = Paginator(products, page_size)
    
    try:
        paginated_products = paginator.page(page)
    except:
        paginated_products = paginator.page(1)
    
    # Serialize products
    serializer = ProductSerializer(paginated_products, many=True)
    
    # Add inventory information if store_id is provided
    product_data = serializer.data
    if store_id:
        for product_item in product_data:
            try:
                inventory = Inventory.objects.get(
                    store_id=store_id,
                    product_id=product_item['id']
                )
                product_item['inventory_quantity'] = inventory.quantity
                product_item['in_stock'] = inventory.quantity > 0
            except Inventory.DoesNotExist:
                product_item['inventory_quantity'] = 0
                product_item['in_stock'] = False
    
    # Prepare response
    response_data = {
        'results': product_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_results': paginator.count,
            'page_size': page_size,
            'has_next': paginated_products.has_next(),
            'has_previous': paginated_products.has_previous(),
        },
        'filters_applied': {
            'query': query,
            'category': category,
            'min_price': min_price,
            'max_price': max_price,
            'store_id': store_id,
            'in_stock': in_stock,
            'sort_by': sort_by,
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AutocompleteRateThrottle(AnonRateThrottle):
    scope = 'autocomplete'

@api_view(['GET'])
@throttle_classes([AutocompleteRateThrottle])
def autocomplete_products(request):
    """
    Autocomplete API for product titles.
    Returns up to 10 product titles matching the query.
    Rate limited to 20 requests/minute.
    """
    query = request.GET.get('q', '')
    
    # Minimum 3 characters required
    if len(query) < 3:
        return Response({
            'error': 'Query must be at least 3 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get products matching the query
    # First get prefix matches (exact start of title)
    prefix_matches = Product.objects.filter(
        title__istartswith=query
    ).order_by('title')[:5]
    
    # Then get general matches (anywhere in title)
    general_matches = Product.objects.filter(
        title__icontains=query
    ).exclude(
        id__in=[p.id for p in prefix_matches]
    ).order_by('title')[:5]
    
    # Combine results - prefix matches first, then general matches
    all_matches = list(prefix_matches) + list(general_matches)
    
    # Limit to 10 results total
    all_matches = all_matches[:10]
    
    # Format response
    suggestions = [
        {
            'id': product.id,
            'title': product.title,
            'category': product.category.name,
            'price': str(product.price),
            'match_type': 'prefix' if product in prefix_matches else 'general'
        }
        for product in all_matches
    ]
    
    return Response({
        'query': query,
        'suggestions': suggestions,
        'total_results': len(suggestions)
    }, status=status.HTTP_200_OK)
