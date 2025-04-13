from django.urls import path
from ecommerce.views import chi_sono, catalogo_prodotti, dettaglio_prodotto


app_name = 'ecommerce'

urlpatterns = [
    path('chi_sono',chi_sono, name='chi_sono'),
    path('prodotti/', catalogo_prodotti, name='catalogo_prodotti'),
    path('prodotti/<int:pk>/', dettaglio_prodotto, name='dettaglio_prodotto'),
]