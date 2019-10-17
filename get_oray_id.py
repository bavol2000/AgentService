import os


def get_oray_id():
    with open(r'C:\Program Files (x86)\Oray\SunLogin\SunloginClient\config.ini','r') as f:
        datas=f.readlines()
        for line in datas:
            if "password" in line:
                oray_password=line.strip("password=").strip("\n")

            if "fastcode=k" in line:
                oray_id=line.strip("fastcode=k").strip("\n")            

    f.close()
    return {"id":oray_id,"password":oray_password}

print(get_oray_id())
