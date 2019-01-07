"""aviatickets URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from django.conf.urls import url

from ticketsapi.views import flights_view, flights_difference_view


urlpatterns = [
    # path('admin/', admin.site.urls),
    url('flights.(getAll)', flights_view),
    url('flights.(getMostExpensive)', flights_view),
    url('flights.(getCheapest)', flights_view),
    url('flights.(getLongest)', flights_view),
    url('flights.(getFastest)', flights_view),
    url('flights.(getOptimal)', flights_view),
    path('flights.getDifference', flights_difference_view)
]
