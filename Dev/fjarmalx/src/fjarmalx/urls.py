"""fjarmalx URL Configuration
"""
from django.contrib import admin
from django.urls import path
from fjarmal.views import home
from fjarmal.views import market
from fjarmal.views import about
from fjarmal.views import data
from fjarmal.views import strat
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('marketport/', market),
    path('strat/', strat),
    path('about/', about),
    path('help/', data),
    path('<slug:input_symbol>', home)
]
