
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from .models import Processor, User, UserProfile, Farmer
from processing.models import Service, Product, Booking, ProductService
from django.http import JsonResponse
from decimal import Decimal





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
    products = Product.objects.all()  # List of all products
    services = Service.objects.none()  # No services initially
    processors = Processor.objects.none()  # No processors initially
    
    if request.method == "POST":
        # Get phone number and account number from the form
        phone_number = request.POST.get('phone_number')
        account_number = request.POST.get('account_number')

        # Get or create the farmer instance
        farmer, created = Farmer.objects.get_or_create(user=request.user)
        farmer.phone_number = phone_number
        farmer.account_no = account_number
        

        # Selected options from form
        selected_product = request.POST.get('product')
        selected_service_processor = request.POST.get('service_processor')
        quantity = request.POST.get('quantity')  # Quantity input from the form

        # Get the product, service, and processor objects based on selected IDs
        # product = Product.objects.get(id=selected_product)
        product_service = ProductService.objects.get(id=selected_service_processor)

        # Use price_per_unit from ProductService
        price_per_unit = product_service.price_per_unit
        total_price = price_per_unit * Decimal(quantity)


        # Create and save the booking
        Booking.objects.create(
            farmer=farmer,
            product=product_service.product,  # Product is part of the ProductService
            service=product_service.service,  # Service is part of the ProductService
            processor=product_service.processor,  # Processor is part of the ProductService
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_price=total_price,  # Save the total price here
            status='Pending'
        )
        
        return redirect('farmer_dashboard')  # Redirect to farmer dashboard after registration

    return render(request, 'user_app/farmer_register.html', {
        'products': products,
        'services': services,
        'processors': processors
    })

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