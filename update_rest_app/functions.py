import ast
from datetime import datetime
import warnings
import os
import platform
import hashlib
from .models import ArchiveFilesModel
from dotenv import load_dotenv
from django.db import IntegrityError

load_dotenv()
FOLDER_PATHS = os.getenv('FOLDER_PATHS')
ENABLE_MD5 = os.getenv('ENABLE_MD5')
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
    start_time = datetime.now()
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
        # hash_md5.update(f)
    end_time = datetime.now()
    print('md5 time: {}'.format(end_time - start_time))
    return hash_md5.hexdigest()


def update_db():
    start_time = datetime.now()
    print('------')
    print('Update files list')
    count_files_added = 0
    count_files_updated = 0
    count_files = 0
    print(FOLDER_PATHS)
    print(type(FOLDER_PATHS))
    folder_paths_list = [str(i)[1:-1] for i in FOLDER_PATHS[1:-1].split(",") if i.strip()]
    print(folder_paths_list)
    for folder_path in folder_paths_list:
        print(f'folder_path: {folder_path}')
        start_time_os_walk = datetime.now()
        folder_walk = os.walk(folder_path, onerror=None, followlinks=False)
        print('os.walk time: {}'.format(datetime.now() - start_time_os_walk))
        for folder in folder_walk:
            print('------')
            print(f'os.wolk: {folder}')
            print(f'folder: {folder[0]}')
            for file in folder[2]:
                print('------')
                start_time_file = datetime.now()
                count_files += 1
                if os.path.isfile(os.path.join(str(folder[0]), file)):
                    full_path = os.path.join(str(folder[0]), file)
                    current_file_size = os.path.getsize(full_path)
                    current_creation_date = creation_date(full_path)
                    current_update_date = update_date(full_path)
                    if ENABLE_MD5:
                        md5_file = md5(full_path)
                    else:
                        md5_file = None
                    try:
                        new_archive = ArchiveFilesModel(album_name=file,
                                                        file_path=full_path,
                                                        file_size=current_file_size,
                                                        md5_file=md5_file,
                                                        data_create=current_creation_date,
                                                        date_update=current_update_date
                                                        )
                        new_archive.save()
                        count_files_added += 1
                        print(f'Добавлен файл: {new_archive}')
                    except IntegrityError as e:
                        if 'album_name' in str(e.args).lower():
                            update_archive_data = ArchiveFilesModel.objects.get(album_name=file)
                            update_archive_data.file_path = full_path
                            update_archive_data.file_size = current_file_size
                            update_archive_data.md5_file = md5_file
                            update_archive_data.data_create = current_creation_date
                            update_archive_data.date_update = current_update_date
                            update_archive_data.save()
                            print(f'{file} обновлены данные')
                            count_files_updated += 1
                    print('file time: {}'.format(datetime.now() - start_time_file))
            print(f'Всего файлов в папке обработано {len(folder[2])}')
    print(f'Добавлено новых: {count_files_added}')
    print(f'Обновлено: {count_files_updated}')
    print(f'Обработано файлов: {count_files}')
    end_time = datetime.now()
    print('Время выполнения: {}'.format(end_time - start_time))

def check_albums_from_db():
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
