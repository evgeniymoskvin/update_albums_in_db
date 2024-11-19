import mimetypes
import time

from django.shortcuts import render
from django.core.management import execute_from_command_line
from django.views import View
from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, renderers
from rest_framework.decorators import action

from dotenv import load_dotenv

import os

from .models import ArchiveFilesModel
from .functions import md5, update_date, creation_date, update_db, check_albums_from_db
import warnings

load_dotenv()
FOLDER_PATH = os.getenv('FOLDER_PATH')
warnings.filterwarnings("ignore", category=RuntimeWarning)


class IndexView(View):
    def get(self, request):
        update_db()
        return HttpResponse(status=200)


class CheckFilesFromDBView(View):
    def get(self, request):
        check_albums_from_db()
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
