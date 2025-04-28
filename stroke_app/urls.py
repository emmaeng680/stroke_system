from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Case URLs
    path('patients/<int:patient_id>/newcase/', views.case_create, name='case_create'),
    path('cases/<int:case_id>/', views.case_detail, name='case_detail'),
    
    # Clinical Data URLs
    path('cases/<int:case_id>/vitals/add/', views.add_vital_signs, name='add_vitals'),
    path('cases/<int:case_id>/labs/add/', views.add_lab_results, name='add_labs'),
    path('cases/<int:case_id>/imaging/add/', views.add_imaging, name='add_imaging'),
    path('cases/<int:case_id>/nihss/add/', views.add_nihss, name='add_nihss'),
    
    # Consultation URLs
    path('cases/<int:case_id>/consult/add/', views.add_consultation, name='add_consultation'),
    
    # Alert URLs
    path('alerts/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
]