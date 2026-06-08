from django.urls import path
from . import views

urlpatterns = [
    path('doctors/search/', views.doctor_search, name='doctor_search'),
    path('doctors/<int:pk>/slots/', views.doctor_slots, name='doctor_slots'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('voice/query/', views.voice_query, name='voice_query'),
    path('voice/reply/', views.voice_reply, name='voice_reply'),
]
