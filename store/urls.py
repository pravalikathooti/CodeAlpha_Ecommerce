from django.urls import path
from . import views

urlpatterns = [
    path(
    "my-orders/",
    views.my_orders,
    name="my_orders"
),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('login/', views.user_login, name='login'),
    path('', views.home, name='home'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/', views.cart, name='cart'),

    path(
        'cart/increase/<int:product_id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),

    path(
        'cart/decrease/<int:product_id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),

    path(
        'cart/remove/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path('checkout/', views.checkout, name='checkout'),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),

    # User Authentication
    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
]