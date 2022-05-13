from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from .models import *
from .forms import CheckoutForm
from .stripe import stripe_payment


class HomeView(ListView):
    """
    Display homepage with 10 item pagination
    """
    model = Item
    paginated_by = 10
    template_name = 'home.html'

    def get_queryset(self):
        if 'category' in self.kwargs:
            category = self.kwargs['category']
        else:
            category = ""

        if category == "":
            return super().get_queryset()
        else:
            return Item.objects.filter(category=category)


class ItemDetailView(DetailView):
    """
    Display detail view for single item
    """
    model = Item


class OrderSummaryView(LoginRequiredMixin, View):
    """
    Displays summary of client order
    """

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, orderer=False)
            return render(self.request, 'order.html', {'object': order})
        except:
            return redirect('/')


class PaymentView(LoginRequiredMixin, View):
    """
    Handles Stripe payments via the Stripe API
    """

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        # Create Stripe payment
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        chargeID = stripe_payment(
            settings.STRIPE_SECRET_KEY, token, order.get_total(), str(order.id))
        if (chargeID is not None):
            order.ordered = True

            # Save the payment
            payment = Payment()
            payment.stripe_charge_id = chargeID
            payment.user = self.request.user
            payment.price = order.get_total() * 100
            payment.save()
            order.payment = payment
            order.save()
            return redirect('/')
        else:
            messages.error(
                self.request, "Something went wrong with Stripe. Please try again later")
            return redirect('sales:payment')


class CheckoutView(LoginRequiredMixin, View):
    """
    Displays checkout information
    """

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            return redirect('/')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                # Get and save them into the database.
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                postcode = form.cleaned_data.get('postcode')
                same_shipping_address = form.cleaned_data.get(
                    'same_shipping_address')
                save_info = form.cleaned_data.get('save_info')
                billingAddress = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    postcode=postcode,
                )
                billingAddress.save()
                # Connect address with order (Foreign Key)
                order.billing_address = billingAddress
                order.save()
                return redirect('sales:payment')
            return render(self.request, 'checkout.html', {'form': form})

        except ObjectDoesNotExist:
            messages.warning(self.request, "You don't have any active order")
            return redirect('sales:order')


class TestView(TemplateView):
    """
    Test view
    """
    template_name = 'test.html'


@login_required
def add_to_cart(request, slug):
    """
    Adds Item to Cart
    :param request: POST from form
    :param slug: slug of Item
    :return: Rerenders page
    """
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = order.items.filter(item__slug=slug)
        if order_item.exists():
            quant = order_item[0].quantity
            order_item.update(
                quantity=quant + int(request.POST.get('quantity')))
            messages.info(request, "This item has been added to your cart")
        else:
            order_item = OrderItem.objects.create(item=item)
            order.items.add(order_item)
            messages.info(request, "This item has been added to your cart")
    else:
        ordered_date = timezone.now()
        order_item = OrderItem.objects.create(item=item)
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item has been added to your cart")

    return redirect('sales:product', slug=slug)


@login_required
def remove_from_cart(request, slug):
    """
    Removes Item from Cart
    :param request: POST object
    :param slug: slug of Item
    :return: Rerenders page
    """
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = order.items.filter(item__slug=slug)
        if order_item.exists():
            order.items.remove(order_item[0])
            messages.info(request, "Item successfully removed.")
        else:
            messages.info(request, "Item not found in cart.")
    else:
        messages.info(request, "Item not found in cart.")
    return redirect('sales:product', slug=slug)


@login_required
def decrease_quantity(request, slug):
    """
    Decrease Item in Cart by 1
    :param request: POST object
    :param slug: slug of Item
    :return: Rerenders page
    """
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = order.items.filter(item__slug=slug)
        if order_item.exists():
            quant = order_item[0].quantity
            if(quant > 1):
                order_item.update(quantity=quant - 1)
        else:
            messages.info(request, "Item not found in cart.")
    else:
        messages.info(request, "Item not found in cart.")
    return redirect('sales:order', slug=slug)


@login_required
def increase_quantity(request, slug):
    """
    Increase Item in Cart by 1
    :param request: POST object
    :param slug: slug of Item
    :return: Rerenders page
    """
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        order_item = order.items.filter(item__slug=slug)
        if order_item.exists():
            quant = order_item[0].quantity
            if(quant > 1):
                order_item.update(quantity=quant + 1)
        else:
            messages.info(request, "Item not found in cart.")
    else:
        messages.info(request, "Item not found in cart.")
    return redirect('sales:order', slug=slug)
