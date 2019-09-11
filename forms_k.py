from django import forms
from django.forms import CheckboxInput
from captcha.fields import ReCaptchaField
from tools.widgets import PhoneInput
from contact.models import FeedbackMessage, EmailForwarding

class ContactFeedBackForm(forms.ModelForm):
    captcha = ReCaptchaField()
    politics= forms.BooleanField(required = True,label = """<label class="confirm_pol" style="color: black;font-size: 15px";>
        Я соглашаюсь с
        <a style = "text-decoration: underline;color: #3508e6;cursor: pointer; "href="http://disneytermsofuse.com/russian/" target="_blank" class="link">условиями использования</a>
        и
         <a style = "text-decoration: underline;color: #3508e6;cursor: pointer; "href="https://privacy.thewaltdisneycompany.com/ru/current-privacy-policy-ru-ru/" target="_blank" class="link">политикой конфиденциальности</a>
        и
          <a style = "text-decoration: underline;color: #3508e6;cursor: pointer; "href="https://key.disney.ru/signup/information" target="_blank" class="link">даю согласие</a>
        на
        <a style = "text-decoration: underline;color: #3508e6;cursor: pointer; "href="https://key.disney.ru/signup/protection" target="_blank" class="link">обработку моих персональных данных</a>
    </label>""")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['business'].required = True
        self.fields['business'].label = "Выбрать бизнес-сегмент"
        self.fields['business'].choices = EmailForwarding.business_choices()
        self.fields['phone'].label_extra_class = 'js-phone-input'
        self.fields['politics'].required = True
    class Meta:
        model = FeedbackMessage
        exclude = ['pr']
        widgets = {
            'phone': PhoneInput(),
            'politics':CheckboxInput()
        }


class PressFeedBackForm(forms.ModelForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pr'].required = True
        self.fields['pr'].label = "Выбрать PR-отдел"
        self.fields['pr'].choices = EmailForwarding.pr_choices()
        self.fields['phone'].label_extra_class = 'js-phone-input'

    class Meta:
        model = FeedbackMessage
        exclude = ['business']
        widgets = {
            'phone': PhoneInput(),
        }
~                 
