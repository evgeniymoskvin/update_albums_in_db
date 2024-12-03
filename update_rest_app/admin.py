from django.contrib import admin
from .models import ArchiveFilesModel, ArchiveEditableFilesModel, CountsFilesInArchive
# Register your models here.

class ArchiveFilesAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'file_path']
    list_filter = ('file_path',)
    ordering = ['-id']
class ArchiveEditableFilesAdmin(admin.ModelAdmin):
    search_fields = ['album_name', 'file_path']
    list_filter = ('file_path',)
    ordering = ['-id']


admin.site.register(ArchiveFilesModel, ArchiveFilesAdmin)
admin.site.register(ArchiveEditableFilesModel, ArchiveEditableFilesAdmin)
admin.site.register(CountsFilesInArchive)