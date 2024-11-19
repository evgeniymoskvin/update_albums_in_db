from django.contrib import admin
from .models import ArchiveFilesModel
# Register your models here.

class ArchiveFilesAdmin(admin.ModelAdmin):
    search_fields = ['album_name']
    list_filter = ('file_path',)
    ordering = ['album_name']


admin.site.register(ArchiveFilesModel, ArchiveFilesAdmin)