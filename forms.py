from django import forms


class MemberForm(forms.Form):
    name = forms.CharField()
    surname = forms.CharField()
    passport_number = forms.IntegerField()
    number_place = forms.IntegerField()
    email = forms.EmailField()

    def send_mail(self):
        print('sending to mail to ',self.cleaned_data['email'])


