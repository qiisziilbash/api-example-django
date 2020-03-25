

from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

admin.autodiscover()

from . import views


urlpatterns = [
    path('', views.webhook_verify, name='whVerify'),

    url('ajax/visitPatient/', views.visit_patient, name='visitPatient'),
    url('ajax/getAppointment/', views.get_appoinntment, name='getAppointment'),
    url('ajax/finalizeAppointment/', views.finalize_appointment, name='finalizeAppointment'),

    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='doctor'),

    url(r'^kiosk/$', views.KioskWelcome.as_view(), name='kiosk'),
    url(r'^kiosk/checkin/$', views.KioskCheckIn.as_view(), name='kioskCheckin'),
    url(r'^kiosk/demographics/$', views.KioskDemographics.as_view(), name='kioskDemographics'),

    url(r'^admin/', admin.site.urls),
    url(r'', include('social.apps.django_app.urls', namespace='social')),


]