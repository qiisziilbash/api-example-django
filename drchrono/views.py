import datetime

from django.http import JsonResponse
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth

from utils import get_customized_appointments
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'setup.html'


class KioskWelcome(TemplateView):
    """
    This is a kiosk that patients can check in
    """
    template_name = 'kiosk_welcome.html'

    def get_context_data(self, **kwargs):
        kwargs = super(KioskWelcome, self).get_context_data(**kwargs)

        return kwargs


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def get_doctor(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    def get_appointments(self, date):
        access_token = self.get_token()
        appointment_api = AppointmentEndpoint(access_token)

        appointments = appointment_api.list(date=date)

        return get_customized_appointments(appointments, access_token)

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)

        doctor = self.get_doctor()
        appointments = self.get_appointments(str(datetime.date.today()))

        kwargs['doctor'] = doctor
        kwargs['appointments'] = appointments

        return kwargs


def visit_patient(request):
    """
    This is an anjax call to update appointment status from 'Checked In' to 'In Session'
    :param request: request from doctor
    :return: success msg with some appointment details
    """
    appointment_id = request.POST['appointmentID']

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']

    appointment_api = AppointmentEndpoint(access_token)

    appointment_api.update(appointment_id, {'status': 'In Session'})
    appointment = appointment_api.fetch(appointment_id)

    return JsonResponse({'msg': 'Success', 'patient': appointment['patient']})
