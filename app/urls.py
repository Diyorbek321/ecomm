from django.urls import path
from app.views import Home, Contact, Cart, Checkout, Shop, Detail, Register, Profile, AddToCartView, RemoveFromCartView, \
    About,Help,Faq
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', Home.as_view(), name='home'),
    path('contact/', Contact.as_view(), name='contact'),
    path('cart/', Cart.as_view(), name='cart'),
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('shop/', Shop.as_view(), name='shop'),
    path('category/<slug:category_slug>/',Shop.as_view(),name='category'),
    path('product/<int:pk>/', Detail.as_view(), name='product-detail'),  # Detail page
    path('register/', Register.as_view(), name='register'),
    path('profile/', Profile.as_view(), name='profile'),
    path('add_to_cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('about/',About.as_view(),name='about'),
    path('help/',Help.as_view(),name='help'),
    path('faq/',Faq.as_view(),name='faq')

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
