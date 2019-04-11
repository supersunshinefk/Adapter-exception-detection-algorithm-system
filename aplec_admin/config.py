# encoding = utf-8
import redis

# 登录鉴权
apip_url_login = "http://pro.kps.mixiot.top/proqy/api/apip/get_token"
apip_param_login = {"app_id": "8001", "app_secret": "W7Xxf#Cb7eiApqxzgc*3xfyx27Qc!y7q"}


# 存储至redis的有效时间的队列名
Get_token_name = 'get:apip:token:aplec'

# 反向控制APIP
apip_url_control = "http://pro.kps.mixiot.top/proqy/api/apip/apip_push2"


# mysql配置
HOST = "127.0.0.1"
USER = 'root'
DB = 'aplec'
PASSWORD = 'passw0rd'
PORT = 3306
CHARSET = "UTF8"

# redis 配置
REDIS_HOST = "127.0.0.1"
REDIS_DB = 0
REDIS_PORT = 6379

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


# 用于获取适配器信息
APIQ_URL_login = "http://admin.kps.mixiot.top/api/login/"
login_param = {'username': 'admin', 'password': 'mix123456', 'system': 'PRO'}
apiq_url_get_aprus_message = "http://admin.kps.mixiot.top/api/aprus/get"







