from django.urls import path
from . import views


app_name = 'ecommerce'

urlpatterns = [
    path('chi_sono',views.chi_sono, name='chi_sono'),
]