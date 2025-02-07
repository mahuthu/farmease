
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.shortcuts import render, redirect
from .models import Processor, User, UserProfile, Farmer
from processing.models import Service, Product, Booking, ProductService
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Prefetch, Count





User = get_user_model()  # Get the built-in User model

def registration_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Create user
        user = User.objects.create_user(username=username, password=password, email=email)

        return redirect('login')  # Redirect to login page after registration

    return render(request, 'user_app/registration.html')  # Render registration template

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check if the user already has a profile
            if not hasattr(user, 'userprofile'):  # If no profile exists, redirect to choose role
                return redirect('choose_role')
            else:
                # Redirect based on the user's role
                if user.userprofile.role == 'farmer':
                    return redirect('farmer_dashboard')
                elif user.userprofile.role == 'processor':
                    return redirect('processor_dashboard')
        else:
            return render(request, 'user_app/login.html', {'error': 'Invalid credentials'})
    return render(request, 'user_app/login.html')


def choose_role_view(request):
    if request.method == "POST":
        role = request.POST.get('role')
        user = request.user
        
        # Create a UserProfile with the selected role
        if role in ['farmer', 'processor']:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()

            # Redirect based on the selected role
            return redirect(f'{role}_register')
    
    return render(request, 'user_app/choose_role.html')

def farmer_registration_view(request):
    # Try to get existing farmer data
    farmer = None
    try:
        farmer = request.user.farmer
    except:
        pass
    
    products = Product.objects.all()
    services = Service.objects.none()
    processors = Processor.objects.none()
    
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        account_number = request.POST.get('account_number')

        # Get or create the farmer instance
        farmer, created = Farmer.objects.get_or_create(user=request.user)
        farmer.phone_number = phone_number
        farmer.account_no = account_number
        farmer.save()

        # Handle booking creation if product is selected
        selected_product = request.POST.get('product')
        selected_service_processor = request.POST.get('service_processor')
        quantity = request.POST.get('quantity')

        if selected_product and selected_service_processor and quantity:
            product_service = ProductService.objects.get(id=selected_service_processor)
            price_per_unit = product_service.price_per_unit
            total_price = price_per_unit * Decimal(quantity)

            Booking.objects.create(
                farmer=farmer,
                product=product_service.product,
                service=product_service.service,
                processor=product_service.processor,
                quantity=quantity,
                price_per_unit=price_per_unit,
                total_price=total_price,
                status='pending'
            )
            
            return redirect('farmer_dashboard')

    context = {
        'products': products,
        'services': services,
        'processors': processors,
        'farmer': farmer,
        'is_booking': 'booking' in request.GET  # Check if this is a booking request
    }
    
    return render(request, 'user_app/farmer_register.html', context)

def processor_registration_view(request):
    products = Product.objects.all()  # Fetch all products
    services = Service.objects.all()  # Fetch all services

    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        license_no = request.POST.get('license_no')
        certification = request.POST.get('certification')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        selected_products = request.POST.getlist('products')  # Multiple product selection
        selected_services = request.POST.getlist('services')  # Multiple service selection

        # Create the processor
        processor, created = Processor.objects.get_or_create(
            user=request.user,
            business_name=business_name,
            license_no=license_no,
            certification=certification,
            contact_number=contact_number,
            address=address,
        )

        # Associate selected products and create ProductService instances
        for product_id in selected_products:
            for service_id in selected_services:
                price_per_unit = request.POST.get(f'price_per_unit_{product_id}_{service_id}')
                min_amount = request.POST.get(f'min_amount_{product_id}_{service_id}')

                # Create a ProductService instance
                product = Product.objects.get(id=product_id)  # Assuming product exists
                service = Service.objects.get(id=service_id)  # Assuming service exists
                ProductService.objects.create(
                    product=product,
                    service=service,
                    processor=processor,
                    price_per_unit=price_per_unit,
                    min_amount=min_amount,
                )

        return redirect('processor_dashboard')  # Redirect to the processor's dashboard after registration

    return render(request, 'user_app/processor_register.html', {
        'products': products,
        'services': services,
    })

def get_product_services(request):
    product_id = request.GET.get('product_id')
    product_services = ProductService.objects.filter(product_id=product_id)

    data = []
    for ps in product_services:
        data.append({
            'id': ps.id,
            'service': {'name': ps.service.name},
            'processor': {'business_name': ps.processor.business_name},
            'price_per_unit': ps.price_per_unit,
            'min_amount': ps.min_amount,
        })

    return JsonResponse({'product_services': data})

def farmer_dashboard_view(request):
    farmer = request.user.farmer  # Get the farmer associated with the logged-in user
    bookings = Booking.objects.filter(farmer=farmer)  # Fetch all bookings for the farmer

    # Add total_price calculation for each booking
    for booking in bookings:
        # Use the related_name 'product_services' to access ProductService via Processor
        product_service = booking.processor.product_services.get(service=booking.service, product=booking.product)
        booking.total_price = product_service.price_per_unit * Decimal(booking.quantity)

    return render(request, 'user_app/farmer_dashboard.html', {
        'bookings': bookings,
    })

def processor_dashboard_view(request):
    processor = request.user.processor  # Get the processor associated with the logged-in user
    bookings = Booking.objects.filter(processor=processor)  # Fetch all bookings for the processor
    services = ProductService.objects.filter(processor=processor)  # Fetch all services offered by the processor
    return render(request, 'user_app/processor_dashboard.html', {
        'bookings': bookings,
        'services': services,
        'processor':processor,
    })

def logout_view(request):
    logout(request)
    return redirect('login')

# def home_view(request):
#     # Fetch all processors with their related services and products efficiently
#     processors = Processor.objects.prefetch_related(
#         Prefetch(
#             'product_services',
#             queryset=ProductService.objects.select_related('product', 'service')
#         )
#     ).all()

#     # Get unique products and services for filtering
#     products = Product.objects.all()
#     services = Service.objects.all()

#     # Get some statistics for the homepage
#     stats = {
#         'processor_count': Processor.objects.count(),
#         'farmer_count': Farmer.objects.count(),
#         'booking_count': Booking.objects.count(),
#         'product_count': Product.objects.count(),
#     }

#     context = {
#         'processors': processors,
#         'products': products,
#         'services': services,
#         'stats': stats,
#         'featured_processors': processors[:3],  # Get first 3 processors for featured section
#     }
    
#     return render(request, 'user_app/home.html', context)


def home_view(request):
    # Get statistics
    stats = {
        'processor_count': Processor.objects.count(),
        'farmer_count': Farmer.objects.count(),
        'booking_count': Booking.objects.count(),
        'product_count': Product.objects.count(),
    }
    
    # Get products we process
    products = Product.objects.annotate(
        service_count=Count('product_services')
    ).filter(service_count__gt=0)
    
    # Get featured processors
    featured_processors = Processor.objects.all()[:3]
    
    context = {
        'stats': stats,
        'products': products,
        'featured_processors': featured_processors,
    }
    
    return render(request, 'user_app/home.html', context)

def processors_list_view(request):
    # Get filter parameters from URL
    product_filter = request.GET.get('product')
    service_filter = request.GET.get('service')
    
    # Start with all processors
    processors = Processor.objects.prefetch_related(
        Prefetch(
            'product_services',
            queryset=ProductService.objects.select_related('product', 'service')
        )
    )
    
    # Apply filters if provided
    if product_filter:
        processors = processors.filter(product_services__product_id=product_filter).distinct()
    if service_filter:
        processors = processors.filter(product_services__service_id=service_filter).distinct()

    context = {
        'processors': processors,
        'products': Product.objects.all(),
        'services': Service.objects.all(),
        'selected_product': product_filter,
        'selected_service': service_filter,
    }
    
    return render(request, 'user_app/processors_list.html', context)