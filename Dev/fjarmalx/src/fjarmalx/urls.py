"""fjarmalx URL Configuration
"""
from django.contrib import admin
from django.urls import path
from fjarmal.views import home
from fjarmal.views import market
from fjarmal.views import about
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('marketport/', market),
    path('about/', about),
    path('<slug:input_symbol>', home)
]
