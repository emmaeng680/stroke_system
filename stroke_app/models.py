from django.db import models
from django.utils import timezone
from accounts.models import User

class Patient(models.Model):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.age}, {self.get_sex_display()})"

class StrokeCase(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('referred', 'Referred'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='technician_cases')
    neurologist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='neurologist_cases', null=True, blank=True)
    chief_complaint = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    symptom_onset_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Case #{self.id} - {self.patient.name}"
    
    def is_within_treatment_window(self):
        # Check if within 4.5 hours from symptom onset
        time_diff = timezone.now() - self.symptom_onset_time
        return time_diff.total_seconds() <= 4.5 * 3600

class VitalSigns(models.Model):
    case = models.ForeignKey(StrokeCase, on_delete=models.CASCADE, related_name='vitals')
    blood_pressure_systolic = models.IntegerField()
    blood_pressure_diastolic = models.IntegerField()
    heart_rate = models.IntegerField()
    respiratory_rate = models.IntegerField()
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Vitals for {self.case} at {self.timestamp}"
    
    def is_blood_pressure_high(self):
        return self.blood_pressure_systolic > 185 or self.blood_pressure_diastolic > 110

class LabResult(models.Model):
    case = models.ForeignKey(StrokeCase, on_delete=models.CASCADE, related_name='lab_results')
    cbc_status = models.CharField(max_length=50, default="normal")
    bmp_status = models.CharField(max_length=50, default="normal")
    glucose_level = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    inr = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    platelet_count = models.IntegerField(null=True, blank=True)
    coagulation_status = models.CharField(max_length=50, default="normal")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lab results for {self.case} at {self.timestamp}"
    
    def is_eligible_for_tpa(self):
        if self.inr and self.inr > 1.7:
            return False
        if self.glucose_level and (self.glucose_level < 50 or self.glucose_level > 400):
            return False
        if self.platelet_count and self.platelet_count < 100000:
            return False
        return True

class ImagingStudy(models.Model):
    TYPE_CHOICES = (
        ('ct', 'CT Scan'),
        ('mri', 'MRI'),
        ('other', 'Other'),
    )
    
    case = models.ForeignKey(StrokeCase, on_delete=models.CASCADE, related_name='imaging_studies')
    study_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    findings = models.TextField()
    image_url = models.CharField(max_length=255, blank=True, null=True)  # Simulated - would store path or reference
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Imaging studies"
    
    def __str__(self):
        return f"{self.get_study_type_display()} for {self.case} at {self.timestamp}"

class NIHSSScore(models.Model):
    case = models.ForeignKey(StrokeCase, on_delete=models.CASCADE, related_name='nihss_scores')
    score = models.IntegerField()
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"NIHSS Score: {self.score} for {self.case} at {self.timestamp}"

class Consultation(models.Model):
    case = models.ForeignKey(StrokeCase, on_delete=models.CASCADE, related_name='consultations')
    neurologist = models.ForeignKey(User, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    treatment_recommendation = models.TextField()
    tpa_recommended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Consultation for {self.case} by {self.neurologist.get_full_name()}"

class Alert(models.Model):
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    case = models.ForeignKey(StrokeCase, on_delete=models.CASCADE, related_name='alerts')
    title = models.CharField(max_length=100)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.severity}) - {self.case}"