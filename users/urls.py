# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomPasswordResetView
from .forms import CustomSetPasswordForm,CustomPasswordResetForm

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # This line fixes the error
    path('products_listing/', views.product_listing_view, name='product_listing'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/',views.checkout_view, name='checkout'),
    path('payment/', views.paypal_payment, name='paypal_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/confirm/', views.confirm_payment, name='confirm_payment'),

    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    path(
    'accounts/password_reset/',
    auth_views.PasswordResetView.as_view(
        form_class=CustomPasswordResetForm,
        template_name='users/password_reset_form.html'
    ),
    name='password_reset'
),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        form_class=CustomSetPasswordForm
    ),
    name='password_reset_confirm'
),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),




]
