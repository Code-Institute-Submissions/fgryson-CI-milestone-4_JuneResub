from django.views.generic import TemplateView, ListView
from models import *


class HomeView(ListView):
    """
    Dispaly homepage with 10 item pagination
    """
    model = Item
    paginated_by = 10
    template_name = 'home.html'


class TestView(TemplateView):
    """
    Test view
    """
    template_name = 'test.html'
