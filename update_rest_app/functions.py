import ast
from datetime import datetime
import warnings
import os
import platform
import logging
import hashlib
from .models import ArchiveFilesModel, ArchiveEditableFilesModel, CountsFilesInArchive
from dotenv import load_dotenv
from django.db import IntegrityError

load_dotenv()
FOLDER_PATHS = os.getenv('FOLDER_PATHS')
ENABLE_MD5 = os.getenv('ENABLE_MD5')
logging.basicConfig(level=logging.NOTSET, filename="update_albums.log", filemode="w+")


# warnings.filterwarnings("ignore", category=RuntimeWarning)


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
    hash_md = hash_md5.hexdigest()
    print(f'md5 ({hash_md}) time: {format(end_time - start_time)}')
    return hash_md


def update_db():
    start_time = datetime.now()
    print('------')
    print('Update files list')
    logging.info(f'Обновление списка файлов из папки начато. {start_time}')

    count_files_added = 0
    count_files_updated = 0
    count_pdf = 0
    count_editable = 0

    folder_paths_list = [str(i)[1:-1] for i in FOLDER_PATHS[1:-1].split(",") if i.strip()]
    problem_list = []
    for folder_path in folder_paths_list:
        print(f'folder_path: {folder_path}')
        logging.info(f'folder_path: {folder_path}')
        start_time_os_walk = datetime.now()
        folder_walk = os.walk(folder_path, onerror=None, followlinks=False)
        for folder in folder_walk:
            print('------')
            # print(f'os.wolk: {folder}')
            print(f'folder: {folder[0]}')
            logging.info(f'folder: {folder[0]}')
            for file in folder[2]:
                if str(file).endswith('.pdf'):
                    count_pdf += 1
                    print('------')
                    print(file)
                    start_time_file = datetime.now()
                    if os.path.isfile(os.path.join(str(folder[0]), file)):
                        full_path = os.path.join(str(folder[0]), file)
                        current_file_size = os.path.getsize(full_path)
                        current_creation_date = creation_date(full_path)
                        current_update_date = update_date(full_path)
                        md5_file = md5(full_path)
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
                            logging.info(f'Добавлен файл: {new_archive}')
                        except IntegrityError as e:
                            if 'album_name' in str(e.args).lower():
                                update_archive_data = ArchiveFilesModel.objects.get(album_name=file)
                                update_archive_data.file_path = full_path
                                update_archive_data.file_size = current_file_size
                                update_archive_data.data_create = current_creation_date
                                if (md5_file != update_archive_data.md5_file):
                                    update_archive_data.md5_file = md5_file
                                    update_archive_data.date_update = current_update_date
                                    try:
                                        update_archive_data.save()
                                        print(f'{file} ({full_path}) обновлены данные')
                                        logging.info(f'{file} ({full_path}) обновлены данные')
                                        count_files_updated += 1
                                    except:
                                        problem_list.append((update_archive_data.album_name, update_archive_data.file_path))
                                        logging.error(f'{file} {full_path} Ошибка обновления данных')
                            elif 'md5_file' in str(e.args).lower():
                                print(f'{file} дубляж')
                        except Exception as e:
                            print(e)
                        print('file time: {}'.format(datetime.now() - start_time_file))
                        logging.info(f'Время обработки файла {format(datetime.now() - start_time_file)}')
                elif str(file).endswith('.zip') or str(file).endswith('.rar') or str(file).endswith('.7z'):
                    """Файл в редактируемом формате"""
                    print('------')
                    print(file)
                    count_editable += 1
                    start_time_file = datetime.now()
                    if os.path.isfile(os.path.join(str(folder[0]), file)):
                        full_path = os.path.join(str(folder[0]), file)
                        current_file_size = os.path.getsize(full_path)
                        current_creation_date = creation_date(full_path)
                        current_update_date = update_date(full_path)
                        md5_file = md5(full_path)
                        try:
                            new_archive = ArchiveEditableFilesModel(album_name=file,
                                                                    file_path=full_path,
                                                                    file_size=current_file_size,
                                                                    md5_file=md5_file,
                                                                    data_create=current_creation_date,
                                                                    date_update=current_update_date
                                                                    )
                            new_archive.save()
                            count_files_added += 1
                            print(f'Добавлен файл: {new_archive}')
                            logging.info(f'Добавлен файл: {new_archive}')
                        except IntegrityError as e:
                            if 'album_name' in str(e.args).lower():
                                update_archive_data = ArchiveEditableFilesModel.objects.get(album_name=file)
                                update_archive_data.file_path = full_path
                                update_archive_data.file_size = current_file_size
                                update_archive_data.data_create = current_creation_date
                                print(type(update_archive_data.date_update), update_archive_data.date_update)
                                print(type(current_update_date), current_update_date)
                                if (md5_file != update_archive_data.md5_file):
                                    update_archive_data.md5_file = md5_file
                                    update_archive_data.date_update = current_update_date
                                    try:
                                        update_archive_data.save()
                                        print(f'{file} ({full_path}) обновлены данные')
                                        logging.info(f'{file} ({full_path}) обновлены данные')
                                        count_files_updated += 1
                                    except:
                                        problem_list.append((update_archive_data.album_name, update_archive_data.file_path))
                                        logging.error(f'{file} {full_path} Ошибка обновления данных')
                            elif 'md5_file' in str(e.args).lower():
                                print(f'{file} дубляж')
                        except Exception as e:
                            print(e)
                        print('file time: {}'.format(datetime.now() - start_time_file))
                        logging.info(f'Время обработки файла {format(datetime.now() - start_time_file)}')

            print(f'Всего файлов в папке обработано {len(folder[2])}')
            logging.info(f'Всего файлов в папке обработано {len(folder[2])}')
    count_files = count_pdf + count_editable
    print(f'Добавлено новых: {count_files_added}')
    logging.info(f'Добавлено новых: {count_files_added}')
    print(f'Обновлено: {count_files_updated}')
    logging.info(f'Обновлено: {count_files_updated}')
    print(f'Обработано файлов: {count_files}')
    logging.info(f'Обработано файлов: {count_files}')
    print(f'Обратить внимание: {problem_list}')
    logging.warning(f'Обратить внимание: {problem_list}')
    end_time = datetime.now()
    new_count = CountsFilesInArchive(count_pdf=count_pdf,
                                     count_editable=count_editable,
                                     count_of_add_files=count_files_added
                                     )
    new_count.save()
    print('Время выполнения: {}'.format(end_time - start_time))
    logging.info(f'Время выполнения: {format(end_time - start_time)}')
    return f'Добавлено новых: {count_files_added} \n Обновлено: {count_files_updated} \n Обработано файлов: {count_files} \n  Время выполнения: {format(end_time - start_time)}'


def check_albums_from_db():
    start_time = datetime.now()
    print('------')
    print('Check files from db')
    logging.info(f'Обновление данных по записям из БД')
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
        logging.warning(f'Не найдено {len(lost_albums)} альбомов')
        for lost_album in lost_albums:
            print(lost_album)
            logging.warning(f'{lost_album}')
    end_time = datetime.now()
    print(f'Время выполнения: {format(end_time - start_time)}')
    logging.info(f'Время выполнения: {format(end_time - start_time)}')
    return f'Всего альбомов в базе данных: {len(all_albums_in_db.filter(file_was_deleted=False))}, \n Не найдено {len(lost_albums)} альбомов: \n {lost_albums}'


def check_editable_from_db():
    start_time = datetime.now()
    print('------')
    print('Check files from db')
    logging.info(f'Обновление данных по записям из БД')
    all_albums_in_db = ArchiveEditableFilesModel.objects.all()
    lost_albums = []
    print(f'Всего альбомов в базе данных: {len(all_albums_in_db.filter(file_was_deleted=False))}')
    for album in all_albums_in_db:
        print(album)
        if not os.path.exists(album.file_path):
            album.file_was_deleted = True
            album.save()
            lost_albums.append(album.album_name)
    if len(lost_albums) > 0:
        print(f'Не найдено {len(lost_albums)} альбомов')
        logging.warning(f'Не найдено {len(lost_albums)} альбомов')
        for lost_album in lost_albums:
            print(lost_album)
            logging.warning(f'{lost_album}')
    end_time = datetime.now()
    print(f'Время выполнения: {format(end_time - start_time)}')
    logging.info(f'Время выполнения: {format(end_time - start_time)}')
    return f'Всего альбомов в базе данных: {len(all_albums_in_db.filter(file_was_deleted=False))}, \n Не найдено {len(lost_albums)} альбомов: \n {lost_albums}'
