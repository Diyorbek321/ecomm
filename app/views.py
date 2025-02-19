from django.contrib.auth import login
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from app.forms import CustomUserCreationForm


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


class Register(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # Log form errors
        return super().form_invalid(form)


class Profile(TemplateView):
    template_name = 'profile.html'
