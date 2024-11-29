"""
URL configuration for update_albums_in_db project.

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
from . import views

urlpatterns = [
    path('check-os_walk', views.IndexView.as_view(), name='update-index-files'),
    path('check_from_db', views.CheckFilesFromDBView.as_view(), name='check-albums-from-db'),
    path('check_editable_from_db', views.CheckEditableFromDBView.as_view(), name='check-editable-from-db'),
    path('download_album_api/<int:pk>', views.GetFileView.as_view(), name='download-album'),
    path('download_editable_api/<int:pk>', views.GetEditableFileView.as_view(), name='download-editable'),
]
