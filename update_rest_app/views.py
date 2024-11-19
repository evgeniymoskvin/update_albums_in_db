import glob
import mimetypes
import time

from django.shortcuts import render
from django.core.management import execute_from_command_line
from django.views import View
from django.db import IntegrityError
from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, renderers
from rest_framework.decorators import action

from dotenv import load_dotenv
from datetime import datetime
import os
import platform
import hashlib
from .models import ArchiveFilesModel
import warnings

load_dotenv()
FOLDER_PATH = os.getenv('FOLDER_PATH')
warnings.filterwarnings("ignore", category=RuntimeWarning)


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return datetime.fromtimestamp(os.path.getctime(path_to_file))
    else:
        stat = os.stat(path_to_file)
        try:
            return datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return datetime.fromtimestamp(stat.st_mtime)


def update_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return datetime.fromtimestamp(os.path.getmtime(path_to_file))
    else:
        stat = os.stat(path_to_file)
        try:
            return datetime.fromtimestamp(stat.st_ctime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return datetime.fromtimestamp(stat.st_mtime)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def update_db():
    folder_walk = os.walk(FOLDER_PATH, onerror=None, followlinks=False)
    print('------')
    print('Update files list')
    for folder in folder_walk:
        print('------')
        print(f'folder: {folder[0]}')
        for file in folder[2]:
            if os.path.isfile(os.path.join(str(folder[0]), file)):
                full_path = os.path.join(str(folder[0]), file)
                try:
                    new_archive = ArchiveFilesModel(album_name=file,
                                                    file_path=full_path,
                                                    file_size=os.path.getsize(full_path),
                                                    md5_file=md5(full_path),
                                                    data_create=creation_date(full_path),
                                                    date_update=update_date(full_path)
                                                    )
                    new_archive.save()
                    print(f'Добавлен файл: {new_archive}')
                except IntegrityError as e:
                    if 'album_name' in str(e.args).lower():
                        update_archive_data = ArchiveFilesModel.objects.get(album_name=file)
                        update_archive_data.file_path = full_path
                        update_archive_data.file_size = os.path.getsize(full_path)
                        update_archive_data.md5_file = md5(full_path)
                        update_archive_data.data_create = creation_date(full_path)
                        update_archive_data.date_update = update_date(full_path)
                        update_archive_data.save()
                        print(f'{file} обновлены данные')
        print(f'Всего файлов в папке обработано {len(folder[2])}')


class IndexView(View):
    def get(self, request):
        update_db()
        return HttpResponse(status=200)


class CheckFilesFromDBView(View):
    def get(self, request):
        print('------')
        print('Check files from db')
        all_albums_in_db = ArchiveFilesModel.objects.all()
        lost_albums = []
        print(f'Всего альбомов в базе данных: {len(all_albums_in_db.filter(file_was_deleted=False))}')
        for album in all_albums_in_db:
            if not os.path.exists(album.file_path):
                album.file_was_deleted = True
                album.save()
                lost_albums.append(album.album_name)
        if len(lost_albums) > 0:
            print(f'Не найдено {len(lost_albums)} альбомов')
            for lost_album in lost_albums:
                print(lost_album)
        return HttpResponse(status=200)


class GetFileView(View):
    @action(methods=['get'], detail=True)
    def get(self, request, pk):
        try:
            obj = ArchiveFilesModel.objects.get(id=pk)
            print(obj)
            if os.path.exists(obj.file_path):
                file_handle = open(obj.file_path, 'rb')
                mime_type, _ = mimetypes.guess_type(obj.file_path)
                response = FileResponse(file_handle, content_type=mime_type)
                response['Content-Disposition'] = 'attachment; filename="%s"' % obj.album_name
                return response
            else:
                return HttpResponse('File not found', status=500)
        except Exception as e:
            print(e)
            return HttpResponse('Объект не найден в базе данных', status=404)
