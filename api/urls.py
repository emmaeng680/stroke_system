from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'cases', views.StrokeCaseViewSet, basename='case')

urlpatterns = [
    path('', include(router.urls)),
    path('cases/<int:case_id>/vitals/', views.VitalSignsViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cases/<int:case_id>/labs/', views.LabResultViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cases/<int:case_id>/imaging/', views.ImagingStudyViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cases/<int:case_id>/nihss/', views.NIHSSScoreViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cases/<int:case_id>/consultation/', views.ConsultationViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('cases/<int:case_id>/tpa-eligibility/', views.tpa_eligibility),
    path('alerts/', views.AlertViewSet.as_view({'get': 'list'})),
]