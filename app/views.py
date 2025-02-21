from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView, DetailView
from app.models import Category, Product
from app.forms import CustomUserCreationForm


# Create your views here.
class Home(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


class Cart(TemplateView):
    template_name = 'cart.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.request.session.get('cart', {})
        return context



class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        cart = request.session.get('cart', {})

        if product_id in cart:
            cart[product_id]['quantity'] += 1
        else:
            cart[product_id] = {
                'name': product.name,
                'price': float(product.price),
                'image': product.image.url,
                'quantity': 1
            }

        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({'success': True, 'cart': cart})

class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')

        cart = request.session.get('cart', {})

        if product_id in cart:
            del cart[product_id]  # Remove product from cart
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'success': True, 'cart': cart})

        return JsonResponse({'success': False, 'message': 'Product not found in cart'})



class Checkout(TemplateView):
    template_name = 'checkout.html'


class Detail(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'detail.html'


class Shop(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop.html'

    def get_queryset(self):
        """Filter products based on category slug if provided."""
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            return Product.objects.filter(category=category)

        return Product.objects.all()  # Show all products if no category is selected

    def get_context_data(self, **kwargs):
        """Pass category info to the template."""
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            context['category'] = get_object_or_404(Category, slug=category_slug)
        else:
            context['category'] = None  # No category selected (show all products)

        return context


class Contact(TemplateView):
    template_name = 'contact.html'


class Register(FormView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        if "sign_up" in request.POST:  # User clicked Sign Up
            return self.handle_signup(request)
        elif "sign_in" in request.POST:  # User clicked Sign In
            return self.handle_signin(request)
        return redirect("register")  # If no valid form is submitted

    def handle_signup(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form, "login_form": AuthenticationForm()})

    def handle_signin(self, request):
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": CustomUserCreationForm(), "login_form": login_form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_form"] = AuthenticationForm()  # Add login form to context
        return context

class Profile(TemplateView):
    template_name = 'profile.html'
