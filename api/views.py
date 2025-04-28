from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from stroke_app.models import (
    Patient, StrokeCase, VitalSigns, LabResult, 
    ImagingStudy, NIHSSScore, Consultation, Alert
)
from .serializers import (
    PatientSerializer, StrokeCaseSerializer, VitalSignsSerializer, LabResultSerializer,
    ImagingStudySerializer, NIHSSScoreSerializer, ConsultationSerializer, AlertSerializer
)
from .permissions import IsTechnician, IsNeurologist

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

class StrokeCaseViewSet(viewsets.ModelViewSet):
    serializer_class = StrokeCaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_technician():
            return StrokeCase.objects.filter(technician=user)
        elif user.is_neurologist():
            return StrokeCase.objects.all()
        return StrokeCase.objects.none()

class VitalSignsViewSet(viewsets.ModelViewSet):
    serializer_class = VitalSignsSerializer
    permission_classes = [permissions.IsAuthenticated, IsTechnician]
    
    def get_queryset(self):
        return VitalSigns.objects.filter(case_id=self.kwargs.get('case_id'))
    
    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        case = StrokeCase.objects.get(id=case_id)
        serializer.save(case=case)

class LabResultViewSet(viewsets.ModelViewSet):
    serializer_class = LabResultSerializer
    permission_classes = [permissions.IsAuthenticated, IsTechnician]
    
    def get_queryset(self):
        return LabResult.objects.filter(case_id=self.kwargs.get('case_id'))
    
    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        case = StrokeCase.objects.get(id=case_id)
        serializer.save(case=case)

class ImagingStudyViewSet(viewsets.ModelViewSet):
    serializer_class = ImagingStudySerializer
    permission_classes = [permissions.IsAuthenticated, IsTechnician]
    
    def get_queryset(self):
        return ImagingStudy.objects.filter(case_id=self.kwargs.get('case_id'))
    
    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        case = StrokeCase.objects.get(id=case_id)
        serializer.save(case=case)

class NIHSSScoreViewSet(viewsets.ModelViewSet):
    serializer_class = NIHSSScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NIHSSScore.objects.filter(case_id=self.kwargs.get('case_id'))
    
    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        case = StrokeCase.objects.get(id=case_id)
        serializer.save(case=case, assessed_by=self.request.user)

class ConsultationViewSet(viewsets.ModelViewSet):
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, IsNeurologist]
    
    def get_queryset(self):
        return Consultation.objects.filter(case_id=self.kwargs.get('case_id'))
    
    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        case = StrokeCase.objects.get(id=case_id)
        serializer.save(case=case, neurologist=self.request.user)

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_technician():
            return Alert.objects.filter(case__technician=user)
        elif user.is_neurologist():
            return Alert.objects.filter(case__neurologist=user) | Alert.objects.filter(created_by__user_type='technician')
        return Alert.objects.none()

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tpa_eligibility(request, case_id):
    case = StrokeCase.objects.get(id=case_id)
    vitals = VitalSigns.objects.filter(case=case).first()
    lab_results = LabResult.objects.filter(case=case).first()
    nihss = NIHSSScore.objects.filter(case=case).first()
    
    # Default to eligible
    eligible = True
    reasons = []
    
    # Check time window
    if not case.is_within_treatment_window():
        eligible = False
        reasons.append("Patient outside 4.5 hour treatment window")
    
    # Check blood pressure
    if vitals and (vitals.blood_pressure_systolic > 185 or vitals.blood_pressure_diastolic > 110):
        eligible = False
        reasons.append(f"Blood pressure exceeds threshold: {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic} mmHg")
    
    # Check lab values
    if lab_results:
        if lab_results.inr and lab_results.inr > 1.7:
            eligible = False
            reasons.append(f"INR exceeds threshold: {lab_results.inr}")
        
        if lab_results.glucose_level and (lab_results.glucose_level < 50 or lab_results.glucose_level > 400):
            eligible = False
            reasons.append(f"Glucose level outside acceptable range: {lab_results.glucose_level} mg/dL")
        
        if lab_results.platelet_count and lab_results.platelet_count < 100000:
            eligible = False
            reasons.append(f"Platelet count below threshold: {lab_results.platelet_count}/μL")
    
    # Check NIHSS score
    if nihss and nihss.score < 4:
        eligible = False
        reasons.append(f"NIHSS score below threshold: {nihss.score}")
    
    return Response({
        'eligible': eligible,
        'reasons': reasons
    })