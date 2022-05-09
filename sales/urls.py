from django.urls import path

from . import views

app_name = 'sales'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('<category>', views.HomeView.as_view(), name='home'),
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('order/', views.OrderSummaryView.as_view(), name='order'),
    path('increase-quantity/<slug>/', views.increase_quantity, name='increase-quantity'),
    path('decrease-quantity/<slug>/', views.decrease_quantity, name='decrease-quantity'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
]
