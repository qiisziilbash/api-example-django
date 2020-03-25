from drchrono.endpoints import PatientEndpoint


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


def get_customized_appointments(appointments, access_token):
    """
    this function customize the appointments that are suitable for presentation in doctor dashboard
    :param appointments: in drchrono format
    :param access_token: access_token for drchrono api
    :return: list of customized appointments (returns 1 appointment insted of list if only 1 received)
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


def get_earliest_appointment(appointments):
    pass