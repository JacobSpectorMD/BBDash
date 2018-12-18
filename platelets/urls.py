from django.conf.urls import url
from platelets.views import *

urlpatterns = [
    url(r'^$', platelets, name="platelets"),
]
