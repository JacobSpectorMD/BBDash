from django.conf.urls import url
import utilization.views as views

urlpatterns = [
    url(r'units/', views.units, name="units"),
    url(r'providers/', views.providers, name="providers"),
    url(r'utilization_data/', views.utilization_data, name="utilization_data"),
    url(r'file_upload/', views.file_upload, name='file_upload'),
]
