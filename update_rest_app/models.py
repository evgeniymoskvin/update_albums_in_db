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
