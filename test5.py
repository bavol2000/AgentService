#encoding=utf-8
import servicemanager
import inspect
import os
def clean_log():
    this_file = inspect.getfile(inspect.currentframe())
    dirpath = os.path.abspath(os.path.dirname(this_file))
    with open("{0}\\AgentService.log".format(dirpath),"w+") as f:
        f.write("")
    f.close()



clean_log()

