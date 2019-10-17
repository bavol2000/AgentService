# -*- coding: utf-8 -*-
import win32serviceutil
import win32service
import win32event
import win32timezone
import servicemanager
import winerror
import inspect
import logging
import wmi


import os, sys, re, platform, socket, time, json, threading
import psutil, schedule, requests
from subprocess import Popen, PIPE

AGENT_VERSION = "1.0"
token = 'HPcWR7l4NJNJ'
server_ip = '192.168.5.6'

wmi_class=wmi.WMI()

def getLogger():
    loggeringget = logging.getLogger('[AgentService]')
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    handler = logging.FileHandler(os.path.join(dirpath, "AgentService.log"))
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    loggeringget.addHandler(handler)
    loggeringget.setLevel(logging.INFO)
    return loggeringget


logger = getLogger()


def clean_log():
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    with open("{0}\\AgentService.log".format(dirpath),"w+") as f:
        f.write("")
    f.close()
    logging.info("clean agent log")


def get_ip():
    try:
        hostname = socket.getfqdn(socket.gethostname())
        ipaddr = socket.gethostbyname(hostname)
    except Exception as msg:
        logger.info(msg)
        ipaddr = ''
    return ipaddr


def get_mac():
    try:
        net_if_addrs = psutil.net_if_addrs()
        for values in net_if_addrs.items():
            for v in values:
                if get_ip() in str(v):
                    macaddr = v[0].address
    except Exception as msg:
        logger.info(msg)
        macaddr = ""
    return macaddr


def get_oray():
    with open(r'C:\Program Files (x86)\Oray\SunLogin\SunloginClient\config.ini','r') as f:
        datas = f.readlines()
        for line in datas:
            if "password" in line:
                oray_password=line.strip("password=").strip("\n")
            if "fastcode=k" in line:
                oray_id=line.strip("fastcode=k").strip("\n")            

    f.close()
    oray = {"id": oray_id, "password": oray_password}
    return oray


def get_dmi():
    p = Popen('dmidecode', stdout=PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout


def parser_dmi(dmidata):
    pd = {}
    line_in = False
    for line in dmidata.split('\n'):
        if line.startswith('System Information'):
             line_in = True
             continue
        if line.startswith('\t') and line_in:
                 k,v = [i.strip() for i in line.split(':')]
                 pd[k] = v
        else:
            line_in = False
    return pd

#Linux Centos
# def get_mem_total():
#     cmd = "grep MemTotal /proc/meminfo"
#     p = Popen(cmd, stdout=PIPE, shell = True)
#     data = p.communicate()[0]
#     mem_total = data.split()[1]
#     memtotal = int(round(int(mem_total)/1024.0/1024.0, 0))
#     return memtotal

#Windows
def get_mem_total():
    mem=psutil.virtual_memory()
    memtotal = int(round(mem.total/1024/1024/1024))
    return memtotal


def get_cpu_model():
    try:
        cpuinfo = os.popen("wmic cpu get name /value")
        cpu_model = str(cpuinfo.read()).strip().strip("Name=Intel(R) Xeon(R) CPU")
    except Exception as msg:
        logger.info(msg)
        cpu_model = ""
    return cpu_model


def get_cpu_cores():
    cpu_cores = {"physical": psutil.cpu_count(logical=False) if psutil.cpu_count(logical=False) else 0, "logical": psutil.cpu_count()}
    return cpu_cores


def parser_cpu(stdout):
    groups = [i for i in stdout.split('\n\n')]
    group = groups[-2]
    cpu_list = [i for i in group.split('\n')]
    cpu_info = {}
    for x in cpu_list:
        k, v = [i.strip() for i in x.split(':')]
        cpu_info[k] = v
    return cpu_info


def get_disk_info():
    ret = []
    cmd = "fdisk -l|egrep '^Disk\s/dev/[a-z]+:\s\w*'"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    for i in stdout.split('\n'):
        disk_info = i.split(",")
        if disk_info[0]:
            ret.append(disk_info[0])
    return ret


def post_data(url, data):
    try:
        r = requests.post(url, data)
        if r.text:
            logging.info(r.text)
            # logger.info(r.text)
        else:
            logging.info("Server return http status code: {0}".format(r.status_code))
    except Exception as msg:
        logging.info(msg)
    return True


def asset_info():
    data_info = dict()
    # data_info['memory'] = get_mem_total()
    # data_info['disk'] = str(get_disk_info())
    # cpuinfo = parser_cpu(get_cpu_model())
    # cpucore = get_cpu_cores()
    # data_info['cpu_num'] = cpucore['logical']
    # data_info['cpu_physical'] = cpucore['physical']
    # data_info['cpu_model'] = cpuinfo['model name']
    # data_info['ip'] = get_ip()
    # data_info['sn'] = parser_dmi(get_dmi())['Serial Number']
    # data_info['vendor'] = parser_dmi(get_dmi())['Manufacturer']
    # data_info['product'] = parser_dmi(get_dmi())['Version']
    # data_info['osver'] = platform.linux_distribution()[0] + " " + platform.linux_distribution()[1] + " " + platform.machine()
    # data_info['hostname'] = platform.node()
    # cpuinfo = parser_cpu(get_cpu_model())

    # cpucore = get_cpu_cores()
    # oray = get_oray()
    # data_info['oray_id'] = oray["id"]
    # data_info['oray_password'] = oray["password"]
    # data_info['memory'] = get_mem_total()
    # data_info['disk'] = "480G"
    # data_info['cpu_num'] = cpucore['logical']
    # data_info['cpu_physical'] = cpucore['physical']
    # data_info['cpu_model'] = get_cpu_model()
    # data_info['ip'] = get_ip()
    # data_info['mac'] = get_mac()
    data_info['vendor'] = "vendor"
    data_info['product'] = "product"
    data_info['osver'] = platform.platform(aliased=1,terse=1)
    data_info['hostname'] = platform.node()
    data_info['token'] = token
    data_info['agent_version'] = AGENT_VERSION
    # logger.info(json.dumps(data_info))
    return json.dumps(data_info)


def asset_info_post():
    pversion = platform.python_version()
    # pv = re.search(r'2.6', pversion)
    # if not pv:
    #     osenv = os.environ["LANG"]
    #     os.environ["LANG"] = "us_EN.UTF8"
    logger.info('----------------------------------------------------------')
    logger.info('Get the hardwave infos from host:')
    logger.info(json.loads(asset_info()))
    logger.info('----------------------------------------------------------')
    post_data("http://{0}/cmdb/collect".format(server_ip), asset_info())
    logger.info("http://{0}/cmdb/collect".format(server_ip))
    # if not pv:
    #     os.environ["LANG"] = osenv
    return True


def agg_sys_info():
    logger.info('----------------------------------------------------------')
    logger.info('Get the system infos from host:')
    sys_info = {'hostname': platform.node(),
                'cpu': get_sys_cpu(),
                'mem': get_sys_mem(),
                'disk': get_sys_disk(),
                'net': get_net_info(),
                'token': token}
    logger.info(sys_info)
    json_data = json.dumps(sys_info)
    logger.info('----------------------------------------------------------')
    post_data("http://{0}/monitor/received/sys/info/".format(server_ip), json_data)
    logger.info("http://{0}/monitor/received/sys/info/".format(server_ip))
    # logger.info(json_data)
    return True


def get_sys_cpu():
    sys_cpu = {}
    cpu_time = psutil.cpu_times_percent(interval=1)
    sys_cpu['percent'] = psutil.cpu_percent(interval=1)
    sys_cpu['lcpu_percent'] = psutil.cpu_percent(interval=1, percpu=True)
    sys_cpu['user'] = cpu_time.user
    # sys_cpu['nice'] = cpu_time.nice
    sys_cpu['nice'] = "nice"
    sys_cpu['system'] = cpu_time.system
    sys_cpu['idle'] = cpu_time.idle
    # sys_cpu['iowait'] = cpu_time.iowait
    sys_cpu['iowait'] = "iowait"
    # sys_cpu['irq'] = cpu_time.irq
    sys_cpu['irq'] = "irq"
    # sys_cpu['softirq'] = cpu_time.softirq
    sys_cpu['softirq'] = "softirq"
    # sys_cpu['guest'] = cpu_time.guest
    sys_cpu['guest'] = "guest"
    return sys_cpu


def get_sys_mem():
    sys_mem = {}
    mem = psutil.virtual_memory()
    sys_mem["total"] = mem.total/1024/1024
    sys_mem["percent"] = mem.percent
    sys_mem["available"] = mem.available/1024/1024
    sys_mem["used"] = mem.used/1024/1024
    sys_mem["free"] = mem.free/1024/1024
    # sys_mem["buffers"] = mem.buffers/1024/1024
    sys_mem["buffers"] = 1024
    # sys_mem["cached"] = mem.cached/1024/1024
    sys_mem["cached"] = 1024
    return sys_mem


def parser_sys_disk(mountpoint):
    partitions_list = {}
    d = psutil.disk_usage(mountpoint)
    partitions_list['mountpoint'] = mountpoint
    partitions_list['total'] = round(d.total/1024/1024/1024.0, 2)
    partitions_list['free'] = round(d.free/1024/1024/1024.0, 2)
    partitions_list['used'] = round(d.used/1024/1024/1024.0, 2)
    partitions_list['percent'] = d.percent
    return partitions_list


def get_sys_disk():
    sys_disk = {}
    partition_info = []
    partitions = psutil.disk_partitions()
    for p in partitions:
        partition_info.append(parser_sys_disk(p.mountpoint))
    sys_disk = partition_info
    return sys_disk


# 函数获取各网卡发送、接收字节数
def get_nic():

    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称

    recv = {}
    sent = {}

    for key in key_info:
        recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
        sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)  # 各网卡发送的字节数

    return key_info, recv, sent


# 函数计算每秒速率
def get_nic_rate(func):

    key_info, old_recv, old_sent = func()  # 上一秒收集的数据
    time.sleep(1)
    key_info, now_recv, now_sent = func()  # 当前所收集的数据

    net_in = {}
    net_out = {}

    for key in key_info:
        net_in.setdefault(key, (now_recv.get(key) - old_recv.get(key)) / 1024)  # 每秒接收速率
        net_out.setdefault(key, (now_sent.get(key) - old_sent.get(key)) / 1024) # 每秒发送速率

    return key_info, net_in, net_out


def get_net_info():
    net_info = []
    key_info, net_in, net_out = get_nic_rate(get_nic)
    for key in key_info:
        in_data = net_in.get(key)
        out_data = net_out.get(key)
        net_info.append({"nic_name": key, "traffic_in": in_data, "traffic_out": out_data})
    return net_info





def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def get_pid():
    this_file = inspect.getfile(inspect.currentframe())
    BASE_DIR = os.path.dirname(os.path.abspath(this_file))
    pid =str(os.getpid())
    with open(BASE_DIR+"/adminsetd.txt", "w+") as pid_file:
        pid_file.writelines(pid)
        pid_file.close()
    logger.info(pid)









class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'AgentService' #服务名称
    _svc_display_name_ = 'AgentService'
    _svc_description_ = 'AgentService1.3'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True

    def SvcDoRun(self):
        # import readconfig
        # import regMeal
        logger.info('service is start...')
        schedule.every(10).seconds.do(run_threaded, asset_info_post)
        schedule.every(10).seconds.do(run_threaded, agg_sys_info)
        schedule.every(60).seconds.do(run_threaded, clean_log)
        while self.run:
            # print(time.time())
            logger.info('service is running...')
            # paraList = readconfig.readConfig()
            # bFlag = regMeal.main(paraList[0],paraList[1],paraList[2])
            # dirpath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
            # with open(dirpath+r"\AgentPython.txt", 'a') as f:
            #     f.write("\ntest")
            #     f.close()
            # get_pid()
            # asset_info_post()
            # agg_sys_info()
            
            # schedule.every(10).seconds.do(run_threaded, asset_info_post)
            # schedule.every(10).seconds.do(run_threaded, agg_sys_info)
            # schedule.every(3600).seconds.do(run_threaded, clean_log)
            # schedule.every().monday.at("00:20").do(run_threaded, clean_log)
            # schedule.run_pending()
            schedule.run_pending()
            time.sleep(5)

    def SvcStop(self):
        logger.info('service is stop.')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     try:
    #         evtsrc_dll = os.path.abspath(servicemanager.__file__)
    #         servicemanager.PrepareToHostSingle(AgentService)
    #         servicemanager.Initialize('AgentService', evtsrc_dll)
    #         servicemanager.StartServiceCtrlDispatcher()
    #     except win32service.error as details:
    #         logger.info(details)
    #         if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
    #             win32serviceutil.usage()
    # else:
    win32serviceutil.HandleCommandLine(AgentService)



