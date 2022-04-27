from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from .models import *
from .forms import CheckoutForm


class HomeView(ListView):
    """
    Display homepage with 10 item pagination
    """
    model = Item
    paginated_by = 10
    template_name = 'home.html'


class ItemDetailView(DetailView):
    """
    Display detail view for single item
    """
    model = Item
    template = 'product.html'


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


class TestView(TemplateView):
    """
    Test view
    """
    template_name = 'test.html'
