import datetime
import hashlib
import hmac
from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth

from drchrono.forms import *
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, PatientEndpoint
from .utils import get_customized_appointments, get_earliest_appointment
from .settings import WEBHOOK_TOKEN


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'setup.html'


class KioskWelcome(TemplateView):
    """
    This is a kiosk view that patients can check in
    """
    template_name = 'kiosk_welcome.html'

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

        access_token = self.get_token()
        api = DoctorEndpoint(access_token)

        return next(api.list())

    def get_context_data(self, **kwargs):
        kwargs = super(KioskWelcome, self).get_context_data(**kwargs)
        kwargs['doctor'] = self.get_doctor()

        return kwargs


class KioskCheckIn(View):
    """
    This is a Check in view that patients can find their appointment with their personal information
    """
    template_name = 'kiosk_checkin.html'
    form_class = KioskCheckInForm

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def get(self, request):
        """renders form for the get requests"""

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Verify the patient's information and redirects to demographics"""
        form = self.form_class(request.POST)

        if form.is_valid():
            appointment = None

            access_token = self.get_token()
            appointment_api = AppointmentEndpoint(access_token)
            patient_api = PatientEndpoint(access_token)

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            social_security_number_4 = form.cleaned_data['social_security_number_4']

            patients = patient_api.list({'first_name': first_name, 'last_name': last_name})

            # Filters the current patient and gets the earliest appointment in order to check in
            # first and last names are compared in lower case to make it easier for patients
            patient_user = None
            if patients:
                for patient in patients:
                    if patient['first_name'].lower() == first_name.lower() and \
                            patient['last_name'].lower() == last_name.lower():
                        patient_user = patient
                        break
            if not patient_user:
                form.add_error('first_name', 'No appointment is found with provided information!')
            else:
                # TODO check ssn >> remove true
                if social_security_number_4 == patient_user['social_security_number'][:4] or True:
                    appointments = appointment_api.list({'patient': patient_user['id']}, date=str(datetime.date.today()))
                    appointment = get_earliest_appointment(appointments)
                else:
                    form.add_error('social_security_number', 'Incorrect Social Security Number!')

            if not form.errors:
                return redirect('{}?{}'.format(reverse('kioskDemographics'), urlencode({
                    'first_name': first_name,
                    'last_name': last_name,
                    'social_security_number_4': social_security_number_4,
                })))

        return render(request, self.template_name, {'form': form})


class KioskDemographics(View):
    """
    This is a Check in view that patients can find their appointment with their personal information
    """
    template_name = 'kiosk_demographics.html'
    form_class = KioskDemographicsForm

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def get(self, request):
        """renders form for the get requests"""

        social_security_number_4 = request.GET.get('social_security_number_4', '')
        first_name = request.GET.get('first_name', '')
        last_name = request.GET.get('last_name', '')

        form = self.form_class(initial={
            'first_name': first_name,
            'last_name':last_name,
            'social_security_number_4': social_security_number_4
        })

        return render(request, self.template_name, {'form': form},)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            access_token = self.get_token()
            appointment_api = AppointmentEndpoint(access_token)
            patient_api = PatientEndpoint(access_token)

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            social_security_number_4 = form.cleaned_data['social_security_number_4']

            address = form.cleaned_data['address']
            cell_phone = form.cleaned_data['cell_phone']
            email = form.cleaned_data['email']
            emergency_contact_name = form.cleaned_data['emergency_contact_name']
            emergency_contact_phone = form.cleaned_data['emergency_contact_phone']

            patients = patient_api.list({'first_name': first_name, 'last_name': last_name})

            # Filters the current patient and gets the earliest appointment in order to check in
            # first and last names are compared in lower case to make it easier for patients

            patient_user = None
            if patients:
                for patient in patients:
                    if patient['first_name'].lower() == first_name.lower() and \
                            patient['last_name'].lower() == last_name.lower():
                        patient_user = patient
                        break

            if not patient_user:
                form.add_error('first_name', 'No appointment is found with provided information!')
            else:
                # TODO check ssn >> remove true
                if social_security_number_4 == patient_user['social_security_number'][:4] or True:
                    appointments = appointment_api.list({'patient': patient_user['id']},
                                                        date=str(datetime.date.today()))
                    appointment = get_earliest_appointment(appointments)
                else:
                    form.add_error('social_security_number', 'Incorrect Social Security Number!')

            if not form.errors:
                # TODO : update the patient and appointment
                return render(request, 'kiosk_success.html',{})
        return render(request, self.template_name, {'form': form},)


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_dashboard.html'

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
    appointment_id = request.POST['appointment_id']

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']

    appointment_api = AppointmentEndpoint(access_token)

    appointment_api.update(appointment_id, {'status': 'In Session'})
    appointment = appointment_api.fetch(appointment_id)
    appointment = get_customized_appointments([appointment], access_token)

    return JsonResponse({
        'msg': 'Success',
        'appointment': appointment
    })


def get_appoinntment(request):
    """
    This is an ajax call to get an appointment from drchrono api
    :param request: contains appointment id or (first_name, last_name, SSN)
    :return: success msg with appointment data
    """

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']

    appointment_api = AppointmentEndpoint(access_token)

    appointment = None

    if 'appointment_id' in request.POST:
        appointment_id = request.POST.get('appointment_id', 0)
        appointment = appointment_api.fetch(appointment_id)

    elif 'SSN' in request.POST:
        ssn = request.POST.get('SSN', 0)
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        patient_api = PatientEndpoint(access_token)
        patients = patient_api.list({'first_name': first_name, 'last_name':last_name})

        for patient in patients:
            #TODO check ssn
            if patient['first_name'] == first_name and patient['last_name'] == last_name:
                appointment = next(appointment_api.list({'patient': patient['id']}, date=str(datetime.date.today())))

    appointment = get_customized_appointments([appointment], access_token)

    return JsonResponse({
        'msg': 'Success',
        'appointment': appointment
    })


def finalize_appointment(request):
    """
    This is an ajax call to finalize the appointment in progress
    :param request: contains appointment id and appointment notes
    :return: success msg
    """
    # TODO : sanitize the notes string
    appointment_id = request.POST['appointment_id']
    notes = request.POST['notes']

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']

    appointment_api = AppointmentEndpoint(access_token)

    appointment_api.update(appointment_id, {'status': 'Complete', 'notes': notes})

    return JsonResponse({
        'msg': 'Success'
    })


def webhook_verify(request):
    print('heerrrrrrrrrrr')
    print('req:' + str(request.GET))
    # secret_token = hmac.new(WEBHOOK_TOKEN, request.GET['msg'], hashlib.sha256).hexdigest()
    return JsonResponse({
        'secret_token': ''
    })
