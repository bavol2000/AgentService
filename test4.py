# -*- coding: utf-8 -*-
import win32api, win32service,win32serviceutil
import os
from collections.abc import Iterable
import json
import psutil
import socket
import inspect
import logging
import requests
import time
import win32serviceutil
import servicemanager

# with open(r"D:\Program Files (x86)\Python\Python37\Lib\site-packages\PyInstaller\utils\cliutils\file_version_info.txt",'r') as f:
#   lines= f.readlines()
#   for line in lines:
#     print(line)


""" 
Read all properties of the given file return them as a dictionary. 
"""
file_path=r"C:\Program Files (x86)\Oray\SunLogin\SunloginClient\SunloginClient.exe"
propNames = ('Comments', 'InternalName', 'ProductName',
  'CompanyName', 'LegalCopyright', 'ProductVersion',
  'FileDescription', 'LegalTrademarks', 'PrivateBuild',
  'FileVersion', 'OriginalFilename', 'SpecialBuild')

props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

try:
  # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
  fixedInfo = win32api.GetFileVersionInfo(file_path, '\\')
  #print(win32api.GetFileVersionInfo(r"D:\PycharmProjects\AgentServer\dist\agent.exe",'\\'))
  #print(win32api.GetFileAttributes(r"C:\Program Files (x86)\Oray\SunLogin\SunloginClient\SunloginClient.exe", '\\'))
  props['FixedFileInfo'] = fixedInfo
  props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
      fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
      fixedInfo['FileVersionLS'] % 65536)

  # \VarFileInfo\Translation returns list of available (language, codepage)
  # pairs that can be used to retreive string info. We are using only the first pair.
  lang, codepage = win32api.GetFileVersionInfo(file_path, '\\VarFileInfo\\Translation')[0]

  # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
  # two are language/codepage pair returned from above

  strInfo = {}
  for propName in propNames:
    strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
    ## print str_info
    strInfo[propName] = win32api.GetFileVersionInfo(file_path, strInfoPath)

  props['StringFileInfo'] = strInfo
except:
  pass
if not props["StringFileInfo"]:
  pass
 # print(None, None)
else:
  pass
#  print(props["StringFileInfo"]["CompanName"], props["StringFileInfo"]["ProductName"])



def get_cpu_model():
  cpuinfo = os.popen("wmic cpu get name /value")
  cpu_model = str(cpuinfo.read()).strip().strip("Name=Intel(R) Xeon(R) CPU")
  return cpu_model




# this_file = inspect.getfile(inspect.currentframe())
# dirpath = os.path.abspath(os.path.dirname(this_file))
# print("{0}\{1}\AgentService.log".format(dirpath,dirpath))

# os.system("cd.>%s\\AgentService.log", dirpath)
# logging.info("clean agent log")
def clean_log():
  this_file = inspect.getfile(inspect.currentframe())
  dirpath = os.path.abspath(os.path.dirname(this_file))
  with open("{0}\\AgentService.log".format(dirpath), "w+") as f:
    f.write("")
  f.close()
  logging.info("clean agent log")

# verinfo = win32api.GetFileVersionInfo(r'C:\Program Files (x86)\Oray\SunLogin\SunloginClient\SunloginClient.exe','\\')
# fileinfo = win32api.Ver
#
# for line in verinfo.items():
#   print(line)


# info = servicemanager._GetServiceShortName("AgentService")
# print(win32serviceutil.QueryServiceStatus("fdasfdas"))


# print(win32serviceutil.GetServiceClassString(AgentService))
def check_install():
  # 检测本机是否已安装AgentService服务
  # scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
  # sc_handle = win32service.OpenService(scm,"AgentService",win32service.SERVICE_ALL_ACCESS)
  # print(win32service.QueryServiceStatus(sc_handle))
  # print(win32service.CloseServiceHandle(sc_handle))
  service_list = []
  for service in psutil.win_service_iter():
      service_list.append(service.name())
  if "AgentService" in service_list:
    # 获取本机服务的版本,通过获取服务名称的描述来获取,TODO:通过文件版本来实现
    print(psutil.win_service_get("AgentService").description())
    print("已安装")
  else:
    print("未安装")



def check_version():
  try:
    r = requests.post(url, data)
    if r.text:
      logging.info(r.text)
    else:
      logging.info("Server return http status code: {0}".format(r.status_code))
  except Exception as msg:
    logging.info(msg)


def update_version():
  # 版本升级
  pass

def getFileVersion(file_name):
  # 获取文件的版本号
    info = win32api.GetFileVersionInfo(file_name, os.sep)
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    version = '%d.%d.%d.%04d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
    return version
print(psutil.win_service_get("AgentService").binpath())

path = psutil.win_service_get("AgentService").binpath()

info = win32api.GetFileVersionInfo(r""+path, "\\")
ms = info['FileVersionMS']
ls = info['FileVersionLS']
version = '%d.%d.%d.%04d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
print(os.path.dirname(path))







# print(getFileVersion(r"C:\Program Files (x86)\Oray\SunLogin\SunloginClient\SunloginClient.exe"))