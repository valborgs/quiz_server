"""
URL configuration for quizapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('quiz/', include('quiz.urls')),
    path('recommendation/', include('movie_recommendation.urls')),
    path('worldcup/', include('movie_worldcup.urls')),
    path('counchillor/', include('counchillor.urls')),
    path('api/', include('upbit_gateway.urls')),
    path('api/pdf/', include('pdfredactor.urls')),
    path('api/pdf-redeem/', include('redactor_pro_code_issuance.urls')),
    path('api/', include('guestbook.urls')),
    path('', include('home.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_URL) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
