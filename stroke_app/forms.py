from django import forms
from .models import (
    Patient, StrokeCase, VitalSigns, LabResult, 
    ImagingStudy, NIHSSScore, Consultation, Alert
)

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'sex', 'medical_history']
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 4}),
        }

class StrokeCaseForm(forms.ModelForm):
    class Meta:
        model = StrokeCase
        fields = ['chief_complaint', 'symptom_onset_time']
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'rows': 3}),
            'symptom_onset_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic', 
            'heart_rate', 'respiratory_rate', 'oxygen_saturation', 'temperature'
        ]
        labels = {
            'blood_pressure_systolic': 'Systolic BP (mmHg)',
            'blood_pressure_diastolic': 'Diastolic BP (mmHg)',
            'heart_rate': 'Heart Rate (bpm)',
            'respiratory_rate': 'Respiratory Rate (breaths/min)',
            'oxygen_saturation': 'Oxygen Saturation (%)',
            'temperature': 'Temperature (°C)'
        }

class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = [
            'cbc_status', 'bmp_status', 'glucose_level', 
            'inr', 'platelet_count', 'coagulation_status'
        ]
        labels = {
            'cbc_status': 'Complete Blood Count Status',
            'bmp_status': 'Basic Metabolic Panel Status',
            'glucose_level': 'Glucose Level (mg/dL)',
            'inr': 'INR',
            'platelet_count': 'Platelet Count (/μL)',
            'coagulation_status': 'Coagulation Status'
        }

class ImagingStudyForm(forms.ModelForm):
    class Meta:
        model = ImagingStudy
        fields = ['study_type', 'findings', 'image_url']
        widgets = {
            'findings': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'study_type': 'Imaging Type',
            'findings': 'Findings/Description',
            'image_url': 'Image URL (Simulated)'
        }

class NIHSSScoreForm(forms.ModelForm):
    class Meta:
        model = NIHSSScore
        fields = ['score']
        labels = {
            'score': 'NIHSS Score'
        }

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['diagnosis', 'treatment_recommendation', 'tpa_recommended', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment_recommendation': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'tpa_recommended': 'Recommend tPA Administration'
        }

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['title', 'message', 'severity']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }