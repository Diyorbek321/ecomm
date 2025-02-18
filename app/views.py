from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class Home(TemplateView):
    template_name = 'index.html'

class Cart(TemplateView):
    template_name = 'cart.html'

class Checkout(TemplateView):
    template_name = 'checkout.html'

class Detail(TemplateView):
    template_name = 'detail.html'

class Shop(TemplateView):
    template_name = 'shop.html'

class Contact(TemplateView):
    template_name = 'contact.html'

class Register(TemplateView):
    template_name = 'register.html'

class Profile(TemplateView):
    template_name = 'profile.html'