import datetime
import hashlib
import hmac
import json
from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth

from drchrono.forms import *
from drchrono.endpoints import AppointmentEndpoint, APIException
from .utils import DoctorBasics, KioskBasics, decorate_appointments
from .settings import WEBHOOK_TOKEN


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a doctor into the kiosk or dashboard, and saves the token.
    """

    template_name = 'setup.html'


class DoctorDashboard(View, DoctorBasics):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_dashboard.html'

    def get(self, request):
        """
        redirects to kiosk if access token is not valid for doctor operations otherwise renders doctor's dashboard
        """
        if self.is_doctor():
            doctor = self.get_doctor()
            appointments = self.get_customized_appointments(str(datetime.date.today()))

            return render(request, self.template_name, {
                'doctor': doctor,
                'appointments': appointments
            })
        else:
            return redirect('kiosk')


class KioskWelcome(TemplateView, DoctorBasics):
    """
    This is a kiosk view that patients can check in
    """
    template_name = 'kiosk_welcome.html'

    def get_context_data(self, **kwargs):
        kwargs = super(KioskWelcome, self).get_context_data(**kwargs)
        kwargs['doctor'] = self.get_doctor()

        return kwargs


class KioskCheckIn(View, DoctorBasics, KioskBasics):
    """
    This is a Check in view that patients can find their appointment with their personal information
    """
    template_name = 'kiosk_checkin.html'
    form_class = KioskCheckInForm

    def get(self, request):
        """renders form for the get requests"""

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Verify the patient's information and redirects to demographics
        first and last names are compared in lower case to make it easier for patients
        """
        form = self.form_class(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            social_security_number_4 = form.cleaned_data['social_security_number_4']

            patients = self.get_patients(first_name, last_name)

            # Filters the current patient
            patient_user = self.verify_patient(patients, first_name, last_name)

            if not patient_user:
                form.add_error('first_name', 'No patient is found with provided information!')
            else:
                appointments = self.get_appointments(str(datetime.date.today()), patient_user['id'])

                # if ssn verification passed, gets the earliest appointment in order to check in
                form, appointment = self.verify_appointment(form, patient_user, appointments)

            if not form.errors:
                return redirect('{}?{}'.format(reverse('kioskDemographics'), urlencode({
                    'first_name': first_name,
                    'last_name': last_name,
                    'social_security_number_4': social_security_number_4,
                    'appointment': appointment
                })))

        return render(request, self.template_name, {'form': form})


class KioskDemographics(View, DoctorBasics, KioskBasics):
    """
    This is a Check in view that patients can find their appointment with their personal information
    """
    template_name = 'kiosk_demographics.html'
    form_class = KioskDemographicsForm

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
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            social_security_number_4 = form.cleaned_data['social_security_number_4']

            address = form.cleaned_data['address']
            cell_phone = form.cleaned_data['cell_phone']
            email = form.cleaned_data['email']
            emergency_contact_name = form.cleaned_data['emergency_contact_name']
            emergency_contact_phone = form.cleaned_data['emergency_contact_phone']

            patients = self.get_patients(first_name, last_name)

            # Filters the current patient
            patient_user = self.verify_patient(patients, first_name, last_name)

            if not patient_user:
                form.add_error('first_name', 'No patient is found with provided information!')
            else:
                appointments = self.get_appointments(str(datetime.date.today()), patient_user['id'])

                # if ssn verification passed, gets the earliest appointment in order to check in
                form, appointment = self.verify_appointment(form, patient_user, appointments)

            if not form.errors:
                # TODO : update the patient and appointment
                return render(request, 'kiosk_success.html', {})

        return render(request, self.template_name, {'form': form},)


def visit_patient(request):
    """
    This is an ajax call to update appointment status from 'Checked In' to 'In Session'
    :param request: request from doctor containing appointment_id
    :return: success msg with some appointment details
    """

    appointment_id = request.POST.get('appointment_id', '')

    if not appointment_id:
        return JsonResponse({'msg': 'No appointment_id in the the request body'})

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']
    appointment_api = AppointmentEndpoint(access_token)

    try:
        appointment_api.update(appointment_id, {'status': 'In Session'})
        appointment = appointment_api.fetch(appointment_id)
        if appointment:
            appointment = decorate_appointments([appointment], access_token)
    except APIException:
        return JsonResponse({'msg': 'Could not update the appointment in the api'})

    return JsonResponse({
        'msg': 'Success',
        'appointment': appointment
    })


def get_appointment(request):
    """
    This is an ajax call to get an appointment from drchrono api
    :param request: containing appointment_id in the request body
    :return: success msg with appointment data or API error
    """

    appointment_id = request.POST.get('appointment_id', '')

    if not appointment_id:
        return JsonResponse({'msg': 'No appointment_id in the the request body'})

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']
    appointment_api = AppointmentEndpoint(access_token)

    try:
        appointment = appointment_api.fetch(appointment_id)
        if appointment:
            appointment = decorate_appointments([appointment], access_token)

    except APIException:
        return JsonResponse({'msg': 'No appointment is returned from api'})

    return JsonResponse({
        'msg': 'Success',
        'appointment': appointment
    })


def finalize_appointment(request):
    """
    This is an ajax call to finalize the appointment in progress
    :param request: contains appointment_id and appointment notes
    :return: success msg or exception
    """

    appointment_id = request.POST.get('appointment_id', '')
    notes = request.POST.get('notes', '').trim()

    if not (appointment_id and notes):
        return JsonResponse({'msg': 'No appointment_id or notes in the the request body'})

    access_token = UserSocialAuth.objects.get(provider='drchrono').extra_data['access_token']
    appointment_api = AppointmentEndpoint(access_token)

    try:
        appointment_api.update(appointment_id, {'status': 'Complete', 'notes': notes})
    except APIException:
        return JsonResponse({'msg': 'Could not update the appointment in the api'})

    return JsonResponse({
        'msg': 'Success'
    })


@csrf_exempt
def web_hook_listener(request):
    """ This function listens to drchrono's webhook and redirects requests that have no 'msg' field to the /setup """
    if request.method == "GET":
        if 'msg' in request.GET:
            byte_token = bytearray()
            byte_token.extend(map(ord, WEBHOOK_TOKEN))
            secret_token = hmac.new(byte_token, request.GET['msg'].encode('utf-8'), hashlib.sha256).hexdigest()
        else:
            return redirect('setup')

        return JsonResponse({
            'secret_token': secret_token
        })

    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        content = body['receiver']
        print(content)
        return JsonResponse({
            'msg': 'Thanks; I will take care of the update'
        })
