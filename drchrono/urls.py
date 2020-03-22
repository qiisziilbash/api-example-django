

from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

import views


urlpatterns = [
    url('ajax/visitPatient/', views.visit_patient, name='visitPatient'),

    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),


]