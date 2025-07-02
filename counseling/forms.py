from django import forms
from django import forms
from .models import StudentCounseling

class StudentCounselingForm(forms.ModelForm):
    class Meta:
        model = StudentCounseling
        fields = '__all__'
        widgets = {
            'counseling_date': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self,*args,**kwargs):
        super(StudentCounselingForm,self).__init__(*args,**kwargs)
        for field in self.fields.values():
            field.required=False



        
