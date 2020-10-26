import json

from social_django.models import UserSocialAuth
from drchrono.endpoints import *


def convert_time(time_in_2400):
    """converts HH:MM -> H:MM PM
    examples:
        "14:20" -> "2:20 PM"
        "12:20" -> "12:20 PM"
        "11:30" -> "11:30 AM"
    """
    hour = int(time_in_2400.split(':')[0])
    minute = int(time_in_2400.split(':')[1])

    suffix = "PM" if hour >= 12 else "AM"
    if hour > 12:
        hour = hour % 12

    return "{:02d}:{:02d} {}".format(hour, minute, suffix)


def get_earliest_appointment(appointments):
    """ this function gets some appointments and returns the first one that is ready to be checked in"""
    if not appointments:
        return None
    else:
        earliest_appointment = None

        # TODO: assumed that appointments are sorted based on their scheduled time; if not sort before
        for appointment in appointments:
            if appointment['status'] != 'Checked In' or \
                    appointment['status'] != 'In Session' or \
                    appointment['status'] != 'Complete' or \
                    appointment['status'] != 'Cancelled':
                earliest_appointment = appointment

    return earliest_appointment


def decorate_appointments(appointments, access_token):
    """
    This functions gets appointments in drchrono's format and customize it by adding useful fields to them
    that are suitable for presentation in doctor's dashboard
    :param appointments: in drchrono format
    :param access_token: doctor's access_token in order tov pull up the information of appointment's patients
    :return: list of customized appointments (returns 1 appointment instead of list if only 1 retrieved)
    """
    patient_api = PatientEndpoint(access_token)

    results = []

    for appointment in appointments:
        patient = patient_api.fetch(appointment['patient'])
        time = convert_time(appointment['scheduled_time'].split('T')[1])

        record = {
            'patient': patient['first_name'] + ' ' + patient['last_name'],
            'patient_race': patient['race'],
            'id': appointment['id'],
            'time': time,
            'status': appointment['status'] or 'Other',
            'notes': appointment['notes'],
            # TODO : these are just random numbers, pull correct ones from status transition
            'hours': 14,
            'minutes': 15
        }

        results.append(record)

    if len(results) == 1:
        return results[0]
    else:
        return results


class KioskBasics:
    """ this class contains basic functions necessary for kiosk views to verify patient"""

    def verify_patient(self, patients, first_name, last_name):
        """ verifies if there is a patient in patients with given first and last names"""
        patient_user = None
        if patients:
            for patient in patients:
                # first and last names are compared in lower case to make it easier for patients
                if patient['first_name'].lower() == first_name.lower() and \
                        patient['last_name'].lower() == last_name.lower():
                    patient_user = patient
                    break
        return patient_user

    def verify_appointment(self, form, patient, appointments):
        """ verifies patient's ssn and returns the earliest valid appointment for check in"""
        appointment = None

        social_security_number_4 = form.cleaned_data['social_security_number_4']

        # TODO check ssn >> remove true
        if social_security_number_4 == patient['social_security_number'][:4] or True:
            appointment = get_earliest_appointment(appointments)

            if not appointment:
                form.add_error('first_name', 'No appointment is found to be checked in!')
        else:
            form.add_error('social_security_number', 'Incorrect Social Security Number!')

        return form, appointment


class DoctorBasics:
    """ this class contains basic functions necessary for other views in order to communicate with drchrono api """

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        access_token = ''
        try:
            oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
            access_token = oauth_provider.extra_data['access_token']
        except:
            return access_token

        return access_token

    def get_doctor(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)

        return next(api.list())

    def get_appointment_api(self):
        """
        this function creates an instance of appointment api with access token and returns the api
        :return: appointment api
        """
        access_token = self.get_token()
        appointment_api = AppointmentEndpoint(access_token)

        return appointment_api

    def get_patient_api(self):
        """
        this function creates an instance of patient api with access token and returns the api
        :return: patient api
        """
        access_token = self.get_token()
        patient_api = PatientEndpoint(access_token)

        return patient_api

    def get_patients(self, first_name, last_name):
        """ gets all patients filtered by first and last names"""
        patients = self.get_patient_api().list({
            'first_name': first_name,
            'last_name': last_name}
        )

        return patients

    def get_appointments(self, date, patient_id=None):
        """
        gets all the appointments in given date;
        only gets a specific patients's appointments if patient_id is passed
        """
        if patient_id:
            appointments = self.get_appointment_api().list({
                'patient': patient_id
            }, date=date)
        else:
            appointments = self.get_appointment_api().list(date=date)

        return appointments

    def get_customized_appointments(self, date, patient_id=None):
        """
        this function return customized appointments that are suitable for presentation in doctor dashboard
        :param date: returns appointments in this date
        :param patient_id : optional > returns only patient's appointments
        :return: list of customized appointments (returns 1 appointment instead of list if only 1 retrieved)
        """
        appointments = self.get_appointments(date, patient_id)

        appointments = decorate_appointments(appointments, self.get_token())

        return appointments

    def get_permissions(self):
        """
        This function checks the level of request permissions
        :return: [] if no access at all; ['kiosk'] if this is kiosk; ['kiosk', 'dashboard'] if this is doctor
        """
        permissions = []
        appointment_profile_api = AppointmentProfileEndpoint(self.get_token())

        # check for kiosk permission, kiosk should be able to access doctor information
        try:
            doctor = self.get_doctor()
        except APIException:
            return permissions

        permissions.append('kiosk')

        # check for dashboard permission; dashboard should be able to access appointment profiles
        try:
            appointment_profile_api.fetch(doctor['id'])
        except NotFound:
            permissions.append('dashboard')
        except Forbidden:
            return permissions

        return permissions

