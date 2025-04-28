from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StrokeCase, VitalSigns, LabResult, NIHSSScore, ImagingStudy, Consultation, Alert

@receiver(post_save, sender=StrokeCase)
def create_case_alert(sender, instance, created, **kwargs):
    if created:
        Alert.objects.create(
            case=instance,
            title="New Stroke Case Created",
            message=f"A new stroke case has been created for patient {instance.patient.name}.",
            severity="medium",
            created_by=instance.technician
        )

@receiver(post_save, sender=Consultation)
def update_case_status(sender, instance, created, **kwargs):
    """Update the case status when a consultation is provided"""
    if created:
        case = instance.case
        if not case.neurologist:
            case.neurologist = instance.neurologist
            case.save(update_fields=['neurologist'])
        
        # Create alert for the technician
        Alert.objects.create(
            case=case,
            title="Consultation Provided",
            message=f"Dr. {instance.neurologist.get_full_name()} has provided consultation for this case.",
            severity="high",
            created_by=instance.neurologist
        )