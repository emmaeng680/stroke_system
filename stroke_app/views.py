from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import (
    Patient, StrokeCase, VitalSigns, LabResult, 
    ImagingStudy, NIHSSScore, Consultation, Alert
)
from .forms import (
    PatientForm, StrokeCaseForm, VitalSignsForm, LabResultForm,
    ImagingStudyForm, NIHSSScoreForm, ConsultationForm, AlertForm
)

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from datetime import timedelta


@login_required
def dashboard(request):
    user = request.user
    context = {
        'title': 'Dashboard',
        'current_time': timezone.now(),
    }
    
    if user.is_technician():
        active_cases = StrokeCase.objects.filter(technician=user, status='active')
        context['active_cases'] = active_cases
        context['recent_cases'] = StrokeCase.objects.filter(technician=user).order_by('-created_at')[:5]
    
    elif user.is_neurologist():
        pending_consultations = StrokeCase.objects.filter(status='active')
        context['pending_consultations'] = pending_consultations
        context['recent_consultations'] = Consultation.objects.filter(neurologist=user).order_by('-timestamp')[:5]
    
    context['unread_alerts'] = Alert.objects.filter(
        case__in=StrokeCase.objects.filter(technician=user) if user.is_technician() else 
        StrokeCase.objects.filter(neurologist=user), 
        is_read=False
    )
    
    return render(request, 'stroke_app/dashboard.html', context)


@login_required
def patient_list(request):
    patients = Patient.objects.all().order_by('-created_at')
    return render(request, 'stroke_app/patient_list.html', {
        'patients': patients,
        'title': 'Patients'
    })

@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.name} has been created successfully.')
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = PatientForm()
    
    return render(request, 'stroke_app/patient_form.html', {
        'form': form,
        'title': 'Create New Patient'
    })

@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    cases = StrokeCase.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'stroke_app/patient_detail.html', {
        'patient': patient,
        'cases': cases,
        'title': f'Patient: {patient.name}'
    })

@login_required
def case_create(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    
    if not request.user.is_technician():
        messages.error(request, 'Only technicians can create new cases.')
        return redirect('patient_detail', patient_id=patient_id)
    
    if request.method == 'POST':
        form = StrokeCaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.patient = patient
            case.technician = request.user
            case.save()
            messages.success(request, f'New stroke case created for {patient.name}.')
            return redirect('case_detail', case_id=case.id)
    else:
        form = StrokeCaseForm()
    
    return render(request, 'stroke_app/case_form.html', {
        'form': form,
        'patient': patient,
        'title': f'New Case for {patient.name}'
    })

@login_required
def case_detail(request, case_id):
    case = get_object_or_404(StrokeCase, id=case_id)
    vitals = VitalSigns.objects.filter(case=case).first()
    lab_results = LabResult.objects.filter(case=case).first()
    imaging = ImagingStudy.objects.filter(case=case)
    nihss_scores = NIHSSScore.objects.filter(case=case).order_by('-timestamp')
    consultations = Consultation.objects.filter(case=case).order_by('-timestamp')
    alerts = Alert.objects.filter(case=case).order_by('-created_at')
    
    # Calculate time since symptom onset
    time_diff = timezone.now() - case.symptom_onset_time
    hours_since_onset = time_diff.total_seconds() / 3600
    
    # Determine if within treatment window for tPA
    within_treatment_window = hours_since_onset <= 4.5
    
    context = {
        'case': case,
        'vitals': vitals,
        'lab_results': lab_results,
        'imaging': imaging,
        'nihss_scores': nihss_scores,
        'consultations': consultations,
        'alerts': alerts,
        'hours_since_onset': round(hours_since_onset, 1),
        'within_treatment_window': within_treatment_window,
        'title': f'Case #{case.id} - {case.patient.name}'
    }
    
    return render(request, 'stroke_app/case_detail.html', context)

@login_required
def add_vital_signs(request, case_id):
    case = get_object_or_404(StrokeCase, id=case_id)
    
    if not request.user.is_technician():
        messages.error(request, 'Only technicians can add vital signs.')
        return redirect('case_detail', case_id=case_id)
    
    if request.method == 'POST':
        form = VitalSignsForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.case = case
            vitals.save()
            
            # Create alert if blood pressure exceeds tPA threshold
            if vitals.blood_pressure_systolic > 185 or vitals.blood_pressure_diastolic > 110:
                Alert.objects.create(
                    case=case,
                    title='High Blood Pressure Alert',
                    message=f'Blood pressure is {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic} mmHg, exceeding tPA threshold.',
                    severity='high',
                    created_by=request.user
                )
            
            messages.success(request, 'Vital signs recorded successfully.')
            return redirect('case_detail', case_id=case_id)
    else:
        form = VitalSignsForm()
    
    return render(request, 'stroke_app/add_vitals.html', {
        'form': form,
        'case': case,
        'title': 'Add Vital Signs'
    })

@login_required
def add_lab_results(request, case_id):
    case = get_object_or_404(StrokeCase, id=case_id)
    
    if not request.user.is_technician():
        messages.error(request, 'Only technicians can add lab results.')
        return redirect('case_detail', case_id=case_id)
    
    if request.method == 'POST':
        form = LabResultForm(request.POST)
        if form.is_valid():
            lab_result = form.save(commit=False)
            lab_result.case = case
            lab_result.save()
            
            # Create alerts for critical lab values
            if lab_result.glucose_level and (lab_result.glucose_level < 50 or lab_result.glucose_level > 400):
                Alert.objects.create(
                    case=case,
                    title='Abnormal Glucose Level',
                    message=f'Glucose level is {lab_result.glucose_level} mg/dL, outside normal range for tPA.',
                    severity='high',
                    created_by=request.user
                )
            
            if lab_result.inr and lab_result.inr > 1.7:
                Alert.objects.create(
                    case=case,
                    title='Elevated INR',
                    message=f'INR is {lab_result.inr}, exceeding threshold for tPA.',
                    severity='high',
                    created_by=request.user
                )
            
            if lab_result.platelet_count and lab_result.platelet_count < 100000:
                Alert.objects.create(
                    case=case,
                    title='Low Platelet Count',
                    message=f'Platelet count is {lab_result.platelet_count}/μL, below threshold for tPA.',
                    severity='high',
                    created_by=request.user
                )
            
            messages.success(request, 'Lab results recorded successfully.')
            return redirect('case_detail', case_id=case_id)
    else:
        form = LabResultForm()
    
    return render(request, 'stroke_app/add_labs.html', {
        'form': form,
        'case': case,
        'title': 'Add Lab Results'
    })

@login_required
def add_imaging(request, case_id):
    case = get_object_or_404(StrokeCase, id=case_id)
    
    if not request.user.is_technician():
        messages.error(request, 'Only technicians can add imaging studies.')
        return redirect('case_detail', case_id=case_id)
    
    if request.method == 'POST':
        form = ImagingStudyForm(request.POST)
        if form.is_valid():
            imaging = form.save(commit=False)
            imaging.case = case
            imaging.save()
            
            # Create alert for neurologist to review imaging
            Alert.objects.create(
                case=case,
                title='New Imaging Available',
                message=f'New {imaging.get_study_type_display()} has been uploaded and requires review.',
                severity='medium',
                created_by=request.user
            )
            
            messages.success(request, 'Imaging study added successfully.')
            return redirect('case_detail', case_id=case_id)
    else:
        form = ImagingStudyForm()
    
    return render(request, 'stroke_app/add_imaging.html', {
        'form': form,
        'case': case,
        'title': 'Add Imaging Study'
    })

@login_required
def add_nihss(request, case_id):
    case = get_object_or_404(StrokeCase, id=case_id)
    
    if request.method == 'POST':
        form = NIHSSScoreForm(request.POST)
        if form.is_valid():
            nihss = form.save(commit=False)
            nihss.case = case
            nihss.assessed_by = request.user
            nihss.save()
            
            # Create alert if NIHSS score is concerning
            if nihss.score >= 4:
                Alert.objects.create(
                    case=case,
                    title='Significant NIHSS Score',
                    message=f'NIHSS score of {nihss.score} recorded, indicating moderate to severe stroke.',
                    severity='medium',
                    created_by=request.user
                )
            
            messages.success(request, 'NIHSS score recorded successfully.')
            return redirect('case_detail', case_id=case_id)
    else:
        form = NIHSSScoreForm()
    
    return render(request, 'stroke_app/add_nihss.html', {
        'form': form,
        'case': case,
        'title': 'Add NIHSS Score'
    })

@login_required
def add_consultation(request, case_id):
    case = get_object_or_404(StrokeCase, id=case_id)
    
    if not request.user.is_neurologist():
        messages.error(request, 'Only neurologists can add consultations.')
        return redirect('case_detail', case_id=case_id)
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.case = case
            consultation.neurologist = request.user
            consultation.save()
            
            # Update case with neurologist if not already assigned
            if not case.neurologist:
                case.neurologist = request.user
                case.save()
            
            # Create alert for technician about consultation
            Alert.objects.create(
                case=case,
                title='Consultation Completed',
                message=f'Neurologist consultation completed by {request.user.get_full_name()}. ' + 
                        ('tPA recommended.' if consultation.tpa_recommended else 'tPA not recommended.'),
                severity='high',
                created_by=request.user
            )
            
            messages.success(request, 'Consultation recorded successfully.')
            return redirect('case_detail', case_id=case_id)
    else:
        form = ConsultationForm()
    
    vitals = VitalSigns.objects.filter(case=case).first()
    lab_results = LabResult.objects.filter(case=case).first()
    imaging = ImagingStudy.objects.filter(case=case)
    nihss_scores = NIHSSScore.objects.filter(case=case).order_by('-timestamp')
    
    return render(request, 'stroke_app/add_consultation.html', {
        'form': form,
        'case': case,
        'vitals': vitals,
        'lab_results': lab_results,
        'imaging': imaging,
        'nihss_scores': nihss_scores,
        'title': 'Add Consultation'
    })

@login_required
def mark_alert_read(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.is_read = True
    alert.save()
    return redirect('case_detail', case_id=alert.case.id)

# Modify the patient_list view to include search functionality
@login_required
def patient_list(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        patients = Patient.objects.filter(
            Q(name__icontains=search_query) | 
            Q(medical_history__icontains=search_query)
        ).order_by('-created_at')
    else:
        patients = Patient.objects.all().order_by('-created_at')
    
    return render(request, 'stroke_app/patient_list.html', {
        'patients': patients,
        'title': 'Patients',
        'search_query': search_query
    })


