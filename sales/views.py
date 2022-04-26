from django.views.generic import TemplateView, ListView, DetailView
from .models import *


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


class TestView(TemplateView):
    """
    Test view
    """
    template_name = 'test.html'
