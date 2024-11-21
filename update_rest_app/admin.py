from django.contrib import admin
from .models import ArchiveFilesModel
# Register your models here.

class ArchiveFilesAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'file_path']
    list_filter = ('file_path',)
    ordering = ['-id']


admin.site.register(ArchiveFilesModel, ArchiveFilesAdmin)