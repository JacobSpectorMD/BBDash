from django.conf.urls import url
from utilization.views import *

urlpatterns = [
    url(r'^$', utilization, name="utilization"),
    url(r'sort/', sort, name="sort"),
    url(r'utilization_data/', utilization_data, name="utilization_data"),
    url(r'file_upload/', file_upload, name='file_upload'),
]
