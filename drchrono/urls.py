

from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

admin.autodiscover()

from . import views


urlpatterns = [
    path('', views.web_hook_listener, name='webHookListener'),

    url('ajax/visitPatient/', views.visit_patient, name='visitPatient'),
    url('ajax/getAppointment/', views.get_appointment, name='getAppointment'),
    url('ajax/finalizeAppointment/', views.finalize_appointment, name='finalizeAppointment'),

    url(r'^setup/$', views.SetupView.as_view(), name='setup'),

    url(r'^dashboard/$', views.DoctorDashboard.as_view(), name='dashboard'),

    url(r'^kiosk/$', views.KioskWelcome.as_view(), name='kiosk'),
    url(r'^kiosk/checkin/$', views.KioskCheckIn.as_view(), name='kioskCheckin'),
    url(r'^kiosk/demographics/$', views.KioskDemographics.as_view(), name='kioskDemographics'),

    url(r'^admin/', admin.site.urls),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
