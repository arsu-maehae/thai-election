from django import forms

class VoterLoginForm(forms.Form):
    national_id = forms.CharField(
        label='รหัสประชาชน',
        max_length=13,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'กรอกรหัสประชาชน 13 หลัก',
            'maxlength': '13',
            'pattern': '[0-9]{13}',
            'inputmode': 'numeric',
            'autocomplete': 'off',
        })
    )

    def clean_national_id(self):
        nid = self.cleaned_data['national_id'].strip()
        if not nid.isdigit() or len(nid) != 13:
            raise forms.ValidationError('รหัสประชาชนต้องมี 13 หลัก')
        return nid