from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from two_factor.urls import urlpatterns as tf_urls
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include("homepage.urls")),
    url(r'', include(tf_urls)),
    url(r'', include(tf_twilio_urls)),
    url(r'^utilization/', include("utilization.urls")),
    url(r'^platelets/', include("platelets.urls")),
    url(r'^user/', include("user.urls"))
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
