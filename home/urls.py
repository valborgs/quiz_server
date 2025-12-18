from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('pdf-redactor-pc/', views.PdfRedactorPcView.as_view(), name='pdf_redactor_pc'),
]
