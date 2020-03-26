from django import forms


class KioskCheckInForm(forms.Form):
    """checkin confirmation form"""
    first_name = forms.CharField(label='First Name', max_length=100, required=True)
    last_name = forms.CharField(label='Last Name', max_length=100, required=True)
    social_security_number_4 = forms.CharField(label='Last 4 digits of SSN', max_length=11, required=True)


class KioskDemographicsForm(forms.Form):
    """patient demographic form"""
    # 'first_name': 'Michelle',
    first_name = forms.CharField(label='First Name', max_length=100, required=True)
    last_name = forms.CharField(label='Last Name', max_length=100, required=True)
    social_security_number_4 = forms.CharField(label='Last 4 digits of SSN', max_length=11, required=True)

    address = forms.CharField(label='Address', max_length=100, required=True)
    cell_phone = forms.CharField(label='Cell Phone', max_length=11, required=True)
    email = forms.CharField(label='Email', max_length=11, required=True)
    emergency_contact_name = forms.CharField(label='Emergency Contact Name', max_length=11, required=True)
    emergency_contact_phone = forms.CharField(label='Emergency Contact Phone', max_length=11, required=True)
