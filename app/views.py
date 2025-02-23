from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView, DetailView
from app.models import Category, Product, Order, OrderItem, Payment, Contact
from app.forms import CustomUserCreationForm, ContactForm
import uuid


class About(TemplateView):
    template_name = 'about.html'

class Help(TemplateView):
    template_name = 'help.html'

class Faq(TemplateView):
    template_name = 'faq.html'
# Create your views here.
class Home(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Categories (unpaginated)
        context['categories'] = Category.objects.all()

        # Featured Products (8 random products)
        context['featured_products'] = Product.objects.order_by('?')[:8]

        # Recent Products (all products, paginated with 15 per page)
        product_queryset = Product.objects.all()
        paginator = Paginator(product_queryset, 15)  # 15 products per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['products'] = page_obj

        return context


class Cart(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        context['cart'] = cart

        # Calculate totals
        subtotal = 0
        for item in cart.values():
            subtotal += float(item['price']) * item['quantity']

        shipping = 10.00  # Fixed shipping cost (adjust as needed)
        total = subtotal + shipping

        context['subtotal'] = subtotal
        context['shipping'] = shipping
        context['total'] = total
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
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'success': True, 'cart': cart})
        return JsonResponse({'success': False, 'message': 'Product not found in cart'})


class Checkout(LoginRequiredMixin, View):
    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart')

        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        shipping = 10.00  # Fixed shipping cost
        total = subtotal + shipping

        context = {
            'cart': cart,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': total,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            return redirect('cart')

        # Calculate total
        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        shipping = 10.00
        total_price = subtotal + shipping

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='pending'
        )

        # Create OrderItems
        for product_id, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                quantity=item['quantity'],
                price=item['price']
            )

        # Create Payment record
        payment_method = request.POST.get('payment', 'card')
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            transaction_id=str(uuid.uuid4()),  # Generate unique transaction ID
            amount_paid=total_price,
            is_successful=True  # You might want to handle actual payment processing here
        )

        # Clear the cart
        request.session['cart'] = {}
        request.session.modified = True

        # Redirect to a success page or order detail page
        return redirect('home')  # Create an order success page and redirec


class Detail(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'detail.html'

    def get_context_data(self, **kwargs):
        """Add related products from the same category to the context."""
        context = super().get_context_data(**kwargs)
        product = self.get_object()  # The current product
        # Get related products from the same category, excluding the current product
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]  # Limit to 4
        context['related_products'] = related_products
        return context


class Shop(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop.html'
    paginate_by = 6

    def get_queryset(self):
        """Filter products based on category and price."""
        queryset = Product.objects.all()
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        # Apply price filter from GET parameters
        price_range = self.request.GET.get('price_range', 'all')
        if price_range != 'all':
            min_price, max_price = map(float, price_range.split('-'))
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)

        return queryset

    def get_context_data(self, **kwargs):
        """Pass price filter options, counts, and selected value to the template."""
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        context['category'] = get_object_or_404(Category, slug=category_slug) if category_slug else None

        # Price filter options
        price_ranges = {
            'all': 'All Price',
            '0-100': '$0 - $100',
            '100-200': '$100 - $200',
            '200-300': '$200 - $300',
            '300-400': '$300 - $400',
            '400-500': '$400 - $500'
        }

        # Precompute counts for price ranges
        all_products = Product.objects.all()
        price_counts = {
            'all': all_products.count(),
            '0-100': all_products.filter(price__gte=0, price__lte=100).count(),
            '100-200': all_products.filter(price__gte=100, price__lte=200).count(),
            '200-300': all_products.filter(price__gte=200, price__lte=300).count(),
            '300-400': all_products.filter(price__gte=300, price__lte=400).count(),
            '400-500': all_products.filter(price__gte=400, price__lte=500).count(),
        }

        # Add to context
        context['price_ranges'] = price_ranges
        context['price_counts'] = price_counts
        context['selected_price'] = self.request.GET.get('price_range', 'all')

        return context


class Contact(View):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, 'There was an error sending your message. Please try again.')

        return redirect('contact')  # Ma


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

