#encoding=utf-8
import win32serviceutil
import win32service
import win32event
import win32api
import servicemanager
import winerror
import inspect
import logging
from win32api import GetFileVersionInfo

import os, sys, re, platform, socket, time, json, threading
import psutil, schedule, requests


AGENT_VERSION = "1.0"
token = 'HPcWR7l4NJNJ'
server_ip = '192.168.5.6'



def getLogger():
    logger = logging.getLogger('[AgentUpdate]')
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    handler = logging.FileHandler(os.path.join(dirpath, "AgentUpdate.log"))
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = getLogger()


def clean_log():
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    with open("{0}\\AgentUpdate.log".format(dirpath),"w+") as f:
        f.write("")
    f.close()
    logger.info("clean agent log")


def post_data(url, data):
    try:
        r = requests.post(url, data)
        if r.text:
            logging.info(r.text)
        else:
            logging.info("Server return http status code: {0}".format(r.status_code))
    except Exception as msg:
        logging.info(msg)
    return True


def asset_info():
    data_info = dict()
    data_info['token'] = token
    data_info['agent_version'] = AGENT_VERSION
    logger.info(json.dumps(data_info))
    return json.dumps(data_info)

def agg_sys_info():
    logger.info('Get the system infos from host:')
    sys_info = {'agent_version': AGENT_VERSION}
    logger.info(sys_info)
    json_data = json.dumps(sys_info)
    logger.info('----------------------------------------------------------')
    post_data("http://{0}/monitor/received/sys/info/".format(server_ip), json_data)
    logger.info("http://{0}/monitor/received/sys/info/".format(server_ip))
    logger.info(json_data)
    return True


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def get_version():
    logger.info(AGENT_VERSION)
    return AGENT_VERSION

def check_install():
  # 检测本机是否已安装AgentService服务
    service_list = []
    for service in psutil.win_service_iter():
        service_list.append(service.name())
    if "AgentService" in service_list:
        return True
    else:
        return False


def get_local_version():
    #获取本机服务的版本
    if check_install():
        local_version = psutil.win_service_get("AgentService").description()
        logger.info("The Local_version is %s" % local_version)
        return local_version
    else:
        return ""

def getFileVersion(file_name):
    #获取文件的版本号
    info = win32api.GetFileVersionInfo(file_name, os.sep)
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    version = '%d.%d.%d.%04d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
    return version

def get_agent_version():
    logger.info('Get the AgentService infos from Server:')
    logger.info('----------------------------------------------------------')
    json_data = json.dumps({'token': 'HPcWR7l4NJNJ'})
    info = requests.post("http://{0}/cmdb/getversion/".format(server_ip),json_data)
    logger.info("The AgentVersion is %s"%info.text)
    return info.text

def update_version():
    #检测是否有安装服务
    if check_install():
        logger.info("local_agent_version is installed")
        #检测跟服务器的版本是否一致
        if get_agent_version() == get_local_version():
            logger.info("The Version is same")
        else:
            path = psutil.win_service_get("AgentService").binpath()
            logger.info("try stop local_agent_version")
            os.popen(path+" stop")
            time.sleep(5)
            os.popen(path+" remove")
    else:
        r = requests.get("http://{0}/static/dist/update/{1}.exe".format(server_ip, get_agent_version()))
        with open("%s.exe" % get_agent_version(), 'wb') as code:
            code.write(r.content)
        code.close()
        time.sleep(5)
        this_file = inspect.getfile(inspect.currentframe())
        dirpath = os.path.abspath(os.path.dirname(this_file))
        os.popen("{0}\\{1}.exe install".format(dirpath, get_agent_version()))
        time.sleep(5)
        os.popen("{0}\\{1}.exe start".format(dirpath, get_agent_version()))




class AgentUpdate(win32serviceutil.ServiceFramework):
    _svc_name_ = 'AgentUpdate' #服务名称
    _svc_display_name_ = 'AgentUpdate'
    _svc_description_ = 'AgentUpdate'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True

    def SvcDoRun(self):
        logger.info('service is run...')
        schedule.every(60).seconds.do(run_threaded, update_version)
        schedule.every(3600).seconds.do(run_threaded, clean_log)
        while self.run:
            logger.info('service is running...')
            # asset_info_post()
            # agg_sys_info()
            # schedule.every(3600).seconds.do(run_threaded, asset_info_post)
            # schedule.every(300).seconds.do(run_threaded, agg_sys_info)
            schedule.run_pending()
            time.sleep(30)

    def SvcStop(self):
        logger.info('service is stop.')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(AgentUpdate)
            servicemanager.Initialize('AgentUpdate', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(AgentUpdate)
