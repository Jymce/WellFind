from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render,redirect, get_object_or_404
from products.models import Product
from products.forms import ProductForm
from django.core.paginator import Paginator
from django.db.models import Q  # For searching
from users.models import Order

from django.contrib.auth.models import User
from users.models import UserProfile


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
@login_required
def admin_dashboard(request):
    return render(request, 'admin_page/dashboard.html')


@user_passes_test(lambda u: u.is_superuser)
def product_list(request):
    VALID_SORT_FIELDS = ['name', 'price', 'quantity', 'is_featured']

    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')
    search_query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    is_featured = request.GET.get('featured', '')

    if sort not in VALID_SORT_FIELDS:
        sort = 'name'
    if direction not in ['asc', 'desc']:
        direction = 'asc'

    sort_key = sort if direction == 'asc' else f"-{sort}"

    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(product_type__icontains=search_query)
        )

    if type_filter:
        products = products.filter(product_type=type_filter)

    if is_featured == '1':
        products = products.filter(is_featured=True)

    products = products.order_by(sort_key)

    paginator = Paginator(products, 5)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    product_types = Product.objects.values_list('product_type', flat=True).distinct()

    return render(request, 'admin_page/product_lists.html', {
        'products': products_page,
        'sort': sort,
        'dir': direction,
        'q': search_query,
        'type': type_filter,
        'types': product_types,
        'featured': is_featured,
    })


@user_passes_test(is_superuser)
def add_product(request):
    if request.method == 'POST':
        post_data = request.POST.copy()  # Create a mutable copy of POST data

        # Ensure is_featured is present (Django won't include unchecked checkboxes)
        if 'is_featured' not in post_data:
            post_data['is_featured'] = False

        form = ProductForm(post_data, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'admin_page/add_product.html', {'form': form})
@user_passes_test(is_superuser)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_page/edit_product.html', {'form': form})

@user_passes_test(is_superuser)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'admin_page/delete_product.html', {'product': product})

@user_passes_test(lambda u: u.is_superuser)
def completed_orders(request):
    orders = Order.objects.filter(is_paid=True).order_by('-created_at')

    # Filtering
    username = request.GET.get('username', '')
    date = request.GET.get('date', '')

    if username:
        orders = orders.filter(user__username__icontains=username)
    if date:
        orders = orders.filter(created_at__date=date)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_page/completed_orders.html', {
        'orders': page_obj,
        'username': username,
        'date': date
    })

@user_passes_test(lambda u: u.is_superuser)
def completed_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, is_paid=True)
    return render(request, 'admin_page/completed_order_detail.html', {'order': order})

@user_passes_test(is_superuser)
def manage_users(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')

    users = User.objects.filter(is_superuser=False)

    if query:
        users = users.filter(username__icontains=query)

    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)

    paginator = Paginator(users.order_by('username'), 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    return render(request, 'admin_page/manage_users.html', {
        'users': users_page,
        'query': query,
        'status_filter': status,
    })

@user_passes_test(is_superuser)
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    profile = get_object_or_404(UserProfile, user=user)
    return render(request, "admin_page/user_detail.html", {
        "user_obj": user,
        "profile": profile,
    })

@user_passes_test(is_superuser)
def user_orders(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    orders = Order.objects.filter(user=user, is_paid=True).order_by('-created_at')
    return render(request, 'admin_page/user_orders.html', {
        'orders': orders,
        'viewed_user': user
    })

@user_passes_test(is_superuser)
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = not user.is_active
    user.save()
    return redirect('user_detail', user_id=user.id)

