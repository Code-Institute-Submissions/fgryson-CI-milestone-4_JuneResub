from django.views.generic import TemplateView

class TestView(TemplateView):
    """
    Test view
    """
    template_name = 'test.html'
