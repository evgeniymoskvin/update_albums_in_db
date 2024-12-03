from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class ArchiveFilesModel(models.Model):
    """Таблица альбомов """
    album_name = models.CharField(unique=True, verbose_name='Наименование альбома', max_length=128, null=True,
                                  blank=True)
    file_path = models.CharField(verbose_name='Путь к файлу', max_length=2500, null=True, blank=True)
    file_size = models.FloatField(verbose_name='Размер файла', max_length=50, null=True, blank=True)
    md5_file = models.CharField(unique=True, verbose_name='md5 файла', max_length=250, null=True, blank=True)
    data_create = models.DateTimeField(verbose_name='Дата создания', null=True, blank=True)
    date_update = models.DateTimeField(verbose_name='Дата последнего обновления', null=True, blank=True)
    file_was_deleted = models.BooleanField(verbose_name='Файл был удален', default=False)

    class Meta:
        managed = False
        verbose_name = _('архивный файл')
        verbose_name_plural = _('архивные файлы')
        db_table = 'get_inventory_app_archivefilesmodel'

    def __str__(self):
        return f'{self.album_name} (md5:{self.md5_file}) {self.file_path}'


class ArchiveEditableFilesModel(models.Model):
    """Таблица альбомов """
    album_name = models.CharField(unique=True, verbose_name='Наименование архива', max_length=128, null=True,
                                  blank=True)
    file_path = models.CharField(verbose_name='Путь к файлу', max_length=2500, null=True, blank=True)
    file_size = models.FloatField(verbose_name='Размер файла', max_length=50, null=True, blank=True)
    md5_file = models.CharField(unique=True, verbose_name='md5 файла', max_length=250, null=True, blank=True)
    data_create = models.DateTimeField(verbose_name='Дата создания', null=True, blank=True)
    date_update = models.DateTimeField(verbose_name='Дата последнего обновления', null=True, blank=True)
    file_was_deleted = models.BooleanField(verbose_name='Файл был удален', default=False)

    class Meta:
        managed = False
        verbose_name = _('файл в редактируемом формате')
        verbose_name_plural = _('файлы в редактируемом формате')
        db_table = 'get_inventory_app_archiveeditablefilesmodel'

    def __str__(self):
        return f'{self.album_name} (md5:{self.md5_file}) {self.file_path}'


class CountsFilesInArchive(models.Model):
    """Счетчик количества файлов в архиве"""

    count_pdf = models.IntegerField(verbose_name='Количество pdf файлов', null=True, blank=True)
    count_editable = models.IntegerField(verbose_name='Количество zip файлов', null=True, blank=True)
    count_of_add_files = models.IntegerField(verbose_name='Количество добавленных файлов', null=True, blank=True)
    date_log = models.DateTimeField(verbose_name='Дата и время обновления', auto_now_add=True, null=False)

    class Meta:
        verbose_name = _('количество файлов')
        verbose_name_plural = _('количество файлов')
        managed = False
        db_table = 'get_inventory_app_countsfilesinarchive'


    def __str__(self):
        return f'{self.date_log} - {self.count_pdf} - {self.count_editable}'
