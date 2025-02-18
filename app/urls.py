from django.urls import path
from app.views import Home, Contact, Cart, Checkout, Shop, Detail, Register,Profile

urlpatterns = [
    path('home/', Home.as_view(), name='home'),
    path('contact/', Contact.as_view(), name='contact'),
    path('cart/', Cart.as_view(), name='cart'),
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('shop/', Shop.as_view(), name='shop'),
    path('detail/', Detail.as_view(), name='detail'),
    path('register/', Register.as_view(), name='register'),
    path('profile/',Profile.as_view(),name='profile')
]
