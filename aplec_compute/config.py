# encoding = utf-8
# 设定线索构造的时间周期时限
# P1周期
P1 = 15 * 60
# P2 周期
P2 = 4 * 60 * 60

# 适配器类型 '2'为模拟适配器，'1'为真实适配器
aprus_id_type = '1'

# apix获取报文数据
apix_url = "http://pro.kps.mixiot.top/v1/apix/latestGridsByDuration"

delayed_time = 15 * 60


# 获取APIQ 设备ID
APIQ_URL_login = "http://admin.kps.mixiot.top/api/login/"
login_param = {'username': 'admin', 'password': 'mix123456', 'system': 'PRO'}
apiq_url_get_aprus = "http://admin.kps.mixiot.top/api/aprus/get_list"


# mysql数据库配置
HOST = "127.0.0.1"
USER = 'root'
DB = 'aplec'
PASSWORD = 'passw0rd'
PORT = 3306
CHARSET = "UTF8"

# mysql保存计算数据时间 days
save_time = 7

# 程序结果解释
# 设定 概率值为零，表示未获取到一天的数据


