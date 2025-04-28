from rest_framework import serializers
from stroke_app.models import (
    Patient, StrokeCase, VitalSigns, LabResult, 
    ImagingStudy, NIHSSScore, Consultation, Alert
)
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'user_type', 'phone_number']
        read_only_fields = fields

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class StrokeCaseSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.name')
    technician_name = serializers.ReadOnlyField(source='technician.get_full_name')
    
    class Meta:
        model = StrokeCase
        fields = ['id', 'patient', 'patient_name', 'technician', 'technician_name', 'neurologist', 
                 'chief_complaint', 'status', 'symptom_onset_time', 'created_at', 'updated_at']
        read_only_fields = ['technician', 'technician_name']

class VitalSignsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSigns
        fields = '__all__'
        read_only_fields = ['case', 'timestamp']

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = '__all__'
        read_only_fields = ['case', 'timestamp']

class ImagingStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagingStudy
        fields = '__all__'
        read_only_fields = ['case', 'timestamp']

class NIHSSScoreSerializer(serializers.ModelSerializer):
    assessor_name = serializers.ReadOnlyField(source='assessed_by.get_full_name')
    
    class Meta:
        model = NIHSSScore
        fields = '__all__'
        read_only_fields = ['case', 'assessed_by', 'assessor_name', 'timestamp']

class ConsultationSerializer(serializers.ModelSerializer):
    neurologist_name = serializers.ReadOnlyField(source='neurologist.get_full_name')
    
    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ['case', 'neurologist', 'neurologist_name', 'timestamp']

class AlertSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['case', 'created_by', 'creator_name', 'created_at']