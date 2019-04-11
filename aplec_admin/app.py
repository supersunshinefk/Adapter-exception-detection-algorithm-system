from flask import Flask
import config
import ast
import pymysql
from flask_cors import CORS
from flask import request, jsonify
import json
import requests
import redis
import constants
import time
import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)


# 获取aplec计算数据
@app.route('/aplec_qy/aplec/get_aplec_data', methods=['POST'])
def get_aplec_data():
    get_aplec_data = list()
    total = 0
    try:
        pages = int(request.form['page_index'])
    except Exception as e:
        context = {"code": 400, "msg": "page_index参数缺失！"}
        return jsonify(context)
    try:
        items = int(request.form['page_size'])
    except Exception as e:
        context = {"code": 400, "msg": "page_size参数缺失！"}
        return jsonify(context)
    created_time = int(request.form['created_time'])
    aprus_id_keys = request.form['aprus_id']
    aprus_id_keys = aprus_id_keys.replace(' ', '')

    probability = request.form['prob']
    probability_keys = probability.split('%')[0]
    print('created_time------>>>>', created_time)
    print("items------->>>", items)
    print("pages------->>>", pages)
    print("probability_keys----->>>", probability_keys)
    # print("data_dict--->>>", data_dict)
    # data_dict = {"items": 10,"pages": 1}

    start_t = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    end_time = (datetime.datetime.strptime(start_t, "%Y-%m-%d %H:%M:%S") + 
                datetime.timedelta(hours=-created_time)).strftime("%Y-%m-%d %H:%M:%S")
    end_time = str(end_time)
    if pages is 1:
        pages_count = pages - 1
    else:
        pages_count = items * (pages - 1)

    try:
        db = pymysql.connect(host=config.HOST, user=config.USER, db=config.DB, passwd=config.PASSWORD,
                             port=config.PORT, charset=config.CHARSET)
        cursor = db.cursor()
    except Exception as e:
        data = {"code": 500, "msg": "数据库连接失败！"}
        return jsonify(data)

    try:
        sql = 'SELECT * FROM aplec_clue WHERE (created >= "' +str(end_time) + '" and created <= "' + str(start_t) + '") AND ' \
              '(aprus_id LIKE "%%' + aprus_id_keys + '%%") AND probability >= "' + probability_keys + '" AND ' \
              '(code LIKE "%%LS:%%" OR code LIKE "%%LA:%%" OR code LIKE "%%AN:%%") ORDER BY created ' \
              'DESC, probability DESC LIMIT ' + str(pages_count) + ', ' + str(items) + ';'
        # print("sql-->>>", sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            single_data = dict()
            single_data["aprus_id"] = row[1]
            single_data["description"] = ast.literal_eval(row[2])
            single_data["code"] = ast.literal_eval(row[3])
            single_data["e_value"] = ast.literal_eval(row[4])
            single_data["probability"] = '%.2f%%' % row[5]
            single_data["created"] = str(row[6])
            get_aplec_data.append(single_data)
    except Exception as e:
        data = {"code": 400, "msg": "未查询到%s相关的适配器ID数据！" % aprus_id_keys}
        return jsonify(data)

    try:
        sql = 'SELECT count(*) FROM aplec_clue WHERE (created >= "' + str(end_time) + '" and created <= "' + str(start_t) + '") AND ' \
              '(aprus_id LIKE "%%' + aprus_id_keys + '%%") AND probability >= "' + probability_keys + '" AND ' \
              '(code LIKE "%%LS:%%" OR code LIKE "%%LA:%%" OR code LIKE "%%AN:%%") ORDER BY created ' \
              'DESC, probability DESC;'
        # print("count_sql--->>>", sql)
        cursor.execute(sql)
        count = cursor.fetchall()
        for count_single in count:
            total = count_single[0]
    except Exception as e:
        data = {"code": 400, "msg": "未查询到%s相关的适配器ID数据！" % aprus_id_keys}
        return jsonify(data)

    db.close()
    data = {
        "code": 200,
        "msg": "执行成功",
        "page_index": pages,
        "page_size": items,
        "total_records": total,
        "result": get_aplec_data
    }

    return jsonify(data)


# aplec反向控制APIP
@app.route('/aplec_qy/aplec/aplec_control', methods=['POST'])
def reverse_control():

    try:
        i_type = request.form['i_type']
    except Exception as e:
        data = {"code": 400, "msg": "i_type参数缺失！"}
        return jsonify(data)
    try:
        command = request.form['command']
    except Exception as e:
        data = {"code": 400, "msg": "command参数缺失！"}
        return jsonify(data)

    data_dict = dict()
    data_dict["i_type"] = i_type
    data_dict["command"] = command
    try:
        apip_token = config.redis_conn.get(config.Get_token_name)
    except Exception as e:
        data = {"code": 500, "msg": "连接redis数据库失败!"}
        return jsonify(data)
    if apip_token is None:
        try:
            login_url = config.apip_url_login
            login_param = config.apip_param_login

            r1 = requests.post(login_url, data=login_param)
            dic1 = json.loads(r1.text)
        except Exception as e:
            data = {"code": 500, "msg": "获取apip token失败!"}
            return jsonify(data)

        apip_token = dic1["msg"]
        try:
            pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
            r = redis.StrictRedis(connection_pool=pool)

            r.set(config.Get_token_name, apip_token)
            r.expire(config.Get_token_name, constants.TOKEN_VALID_TIME)

            apip_token = config.redis_conn.get(config.Get_token_name)
        except Exception as e:
            data = {"code": 500, "msg": "连接redis数据库失败!"}
            return jsonify(data)

    apip_token = apip_token.decode("utf-8")
    data_dict["access_token"] = apip_token

    url = config.apip_url_control
    result = requests.post(url, data=data_dict)
    result = json.loads(result.text)

    if result["code"] is 200:
        data = {"code": 200, "msg": "apip反向控制操作成功!"}
        return jsonify(data)
    elif result["code"] != 200:
        data = {"code": result["code"], "msg": result["msg"]}
        return jsonify(data)
    data = {"code": 400, "msg": "apip反向控制操作失败!"}
    return jsonify(data)


@app.route('/aplec_qy/aplec/aprus_message', methods=['POST'])
def aprus_message():
    try:
        aprus_id = request.form['aprus_id']
    except Exception as e:
        context = {"code": 400, "msg": "aprus_id参数缺失！"}
        return jsonify(context)
    try:
        r1 = requests.post(config.APIQ_URL_login, data=config.login_param)
        dic1 = json.loads(r1.text)
    except Exception as e:
        context = {"code": 400, "msg": "apiq登录鉴权失败！"}
        return jsonify(context)
    token = dic1["data"]["token"]
    headers = {'Authorization': 'Bearer ' + token}
    apiq_data = {"aprus_id": aprus_id}
    try:
        result = requests.post(config.apiq_url_get_aprus_message, headers=headers, data=apiq_data)
        requests_data = json.loads(result.content.decode('utf-8'))
    except Exception as e:
        context = {"code": 400, "msg": "获取aprus_id信息失败！"}
        return jsonify(context)
    data = {"code": 200, "msg": "执行成功", "result": requests_data["data"][0]}
    return jsonify(data)


if __name__ == "__main__":
    app.run()
