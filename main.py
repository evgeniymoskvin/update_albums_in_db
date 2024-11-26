from django.shortcuts import render
import os
from django.core.management import execute_from_command_line
from dotenv import load_dotenv
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "update_albums_in_db.settings")

load_dotenv()
UPDATE_DB_PORT = os.getenv('UPDATE_DB_PORT')


# Create your views here.

def run_server():
    execute_from_command_line(["manage.py", "runserver", UPDATE_DB_PORT, "--noreload"])


if __name__ == "__main__":
    run_server()


# class AppServerSvc(win32serviceutil.ServiceFramework):
#     _svc_name_ = "Update_archive_db_service"
#     _svc_display_name_ = "Update_archive_db_service"
#
#     def __init__(self, args):
#         win32serviceutil.ServiceFramework.__init__(self, args)
#         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
#         socket.setdefaulttimeout(60)
#
#     def SvcStop(self):
#         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
#         win32event.SetEvent(self.hWaitStop)
#
#     def SvcDoRun(self):
#         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
#                               servicemanager.PYS_SERVICE_STARTED,
#                               (self._svc_name_, ''))
#         self.main()
#
#     def main(self):
#         execute_from_command_line(["manage.py", "runserver", UPDATE_DB_PORT, "--noreload"])
#
#
# if __name__ == '__main__':
#     win32serviceutil.HandleCommandLine(AppServerSvc)
