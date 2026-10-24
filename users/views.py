# users/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import path
from .models import UserProfile, CartItem, Order, OrderItem
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from urllib.parse import urlparse
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.conf import  settings


def register_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_superuser else 'home')

    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm = request.POST.get('confirm_password', '')
        address = request.POST['address']

        username_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        if username_exists:
            context['username_exists'] = True
        if email_exists:
            context['email_exists'] = True
        if password != confirm:
            context['password_mismatch'] = True
            messages.error(request, "Passwords do not match.")

        if context:  # If any error flags set
            return render(request, 'users/register.html', context)

        # Registration success
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, address=address)
        context['registration_success'] = True
        return render(request, 'users/register.html', context)

    return render(request, 'users/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_superuser else 'home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        next_url = request.POST.get('next', request.GET.get('next'))

        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                return render(request, 'users/deactivated.html')
        except User.DoesNotExist:
            user = None

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
            elif user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'users/login.html')

@login_required
def home_view(request):
    featured_products = Product.objects.filter(is_featured=True)[:8]
    categories = Product.objects.values_list('product_type', flat=True).distinct()

    # Create dictionary of current cart quantities per product
    cart_items = CartItem.objects.filter(user=request.user)
    cart_quantities = {item.product.id: item.quantity for item in cart_items}

    return render(request, 'users/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'cart_quantities': cart_quantities,
    })

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))

        existing_cart = CartItem.objects.filter(user=request.user, product=product).first()
        existing_qty = existing_cart.quantity if existing_cart else 0

        if quantity + existing_qty > product.quantity:
            error_context = {
                'error_product_id': product.id,
                'error_message': "Cart quantity exceeds available stock.",
            }

            if 'home' in next_url:
                featured_products = Product.objects.filter(is_featured=True)[:8]
                categories = Product.objects.values_list('product_type', flat=True).distinct()
                cart_items = CartItem.objects.filter(user=request.user)
                cart_quantities = {item.product.id: item.quantity for item in cart_items}
                return render(request, 'users/home.html', {
                    'featured_products': featured_products,
                    'categories': categories,
                    'cart_quantities': cart_quantities,
                    **error_context
                })

            elif 'products_listing' in next_url:
                query = request.GET.get('q', '')
                selected_type = request.GET.get('type', '')

                products = Product.objects.all()

                if selected_type:
                    products = products.filter(product_type=selected_type)

                if query:
                    products = products.filter(name__icontains=query)

                cart_items = CartItem.objects.filter(user=request.user)
                cart_quantities = {item.product.id: item.quantity for item in cart_items}

                return render(request, 'users/product_listing.html', {
                    'products': products,
                    'query': query,
                    'selected_type': selected_type,
                    'all_types': Product.objects.values_list('product_type', flat=True).distinct(),
                    'cart_quantities': cart_quantities,
                    **error_context
                })

        if existing_cart:
            existing_cart.quantity += quantity
            existing_cart.save()
        else:
            CartItem.objects.create(user=request.user, product=product, quantity=quantity)

        return redirect(next_url or 'product_listing')

    return redirect('product_listing')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Add total price for each item
    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    # Optional: grand total of the entire cart
    grand_total = sum(item.total_price for item in cart_items)

    return render(request, 'users/cart.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
    })

@login_required
def product_listing_view(request):
    query = request.GET.get('q', '')
    selected_type = request.GET.get('type', '')

    products = Product.objects.all()

    if selected_type:
        products = products.filter(product_type=selected_type)

    if query:
        products = products.filter(name__icontains=query)

    paginator = Paginator(products, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cart_items = CartItem.objects.filter(user=request.user)
    cart_quantities = {item.product.id: item.quantity for item in cart_items}


    context = {
        'products': page_obj,
        'query': query,
        'selected_type': selected_type,
        'all_types': Product.objects.values_list('product_type', flat=True).distinct(),
        'cart_quantities': cart_quantities, 
    }
    return render(request, 'users/product_listing.html', context)

@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == 'POST':
        qty = int(request.POST.get('quantity', 1))
        if 1 <= qty <= item.product.quantity:
            item.quantity = qty
            item.save()
    return redirect('cart')  # Change to your cart URL name

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')  # Replace with your cart view's name

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    grand_total = sum(item.product.price * item.quantity for item in cart_items)

    try:
        address = request.user.userprofile.address
    except UserProfile.DoesNotExist:
        address = "No address found. Please update your profile."

    if request.method == 'POST':
        # Simulate successful payment redirect
        request.session['paid'] = True  # <- Set flag in session
        return redirect('paypal_payment')

    return render(request, 'users/checkout.html', {
        'cart_items': cart_items,
        'grand_total': grand_total,
        'address': address,
        'paypal_client_id': settings.PAYPAL_SANDBOX_CLIENT_ID
    })

@login_required
def paypal_payment(request):
    return render(request, 'users/payment_simulation.html')

@login_required
def confirm_payment(request):
    request.session['paid'] = True
    return redirect('payment_success')

@login_required
def payment_success(request):
    if not request.session.get('paid'):
        return redirect('checkout')

    del request.session['paid']  # clean up session

    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('home')

    total = sum(item.product.price * item.quantity for item in cart_items)
    address = request.user.userprofile.address

    order = Order.objects.create(
        user=request.user,
        address=address,
        total_amount=total,
        is_paid=True
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
        item.product.quantity -= item.quantity
        item.product.save()

    cart_items.delete()
    print("🚀 Reached payment_success")

    return render(request, 'users/payment_success.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, is_paid=True).order_by('-created_at')

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')

    if start_date:
        orders = orders.filter(created_at__date__gte=parse_date(start_date))
    if end_date:
        orders = orders.filter(created_at__date__lte=parse_date(end_date))
    if min_amount:
        try:
            orders = orders.filter(total_amount__gte=float(min_amount))
        except ValueError:
            pass

    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    paginated_orders = paginator.get_page(page_number)
    print("Orders for user:", Order.objects.filter(user=request.user))

    return render(request, 'users/order_history.html', {
        'orders': paginated_orders,
        'start_date': start_date,
        'end_date': end_date,
        'min_amount': min_amount,
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'users/order_detail.html', {'order': order})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
