# 功能：实现Aplec线索计算服务
# Author:supersunshinefk
# encoding = utf-8
import requests
import json
import datetime
import time
import threading
import config
import copy
import pymysql
import ast
import pandas as pd


class Aplec(object):
    def __init__(self):
        super(Aplec, self).__init__()
        self.P1 = config.P1
        self.P2 = config.P2
    # aprus线索计算与判断

    def compute(self, aprus_id):
        start_time_tag = True
        start_time = None

        while True:
            if start_time_tag:
                start_t_flag = str(time.strftime('%Y-%m-%d %H:', time.localtime(time.time()))) + '00:00'
                start_t = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                start_t_flag_p = int(time.mktime(time.strptime(start_t_flag, "%Y-%m-%d %H:%M:%S")))
                start_t_p = int(time.mktime(time.strptime(start_t, "%Y-%m-%d %H:%M:%S")))

                if (start_t_p - start_t_flag_p) <= 900:
                    start_time = (datetime.datetime.strptime(start_t_flag, "%Y-%m-%d %H:%M:%S") +
                                  datetime.timedelta(minutes=-15)).strftime("%Y-%m-%d %H:%M:%S")
                    self.del_repeat_data(start_time)
                if ((start_t_p - start_t_flag_p) > 900) and ((start_t_p - start_t_flag_p) <= 1800):
                    start_time = start_t_flag
                    self.del_repeat_data(start_time)
                if ((start_t_p - start_t_flag_p) > 1800) and ((start_t_p - start_t_flag_p) <= 2700):
                    start_time = (datetime.datetime.strptime(start_t_flag, "%Y-%m-%d %H:%M:%S") +
                                  datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
                    self.del_repeat_data(start_time)
                if ((start_t_p - start_t_flag_p) > 2700) and ((start_t_p - start_t_flag_p) <= 3600):
                    start_time = (datetime.datetime.strptime(start_t_flag, "%Y-%m-%d %H:%M:%S") +
                                  datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
                    self.del_repeat_data(start_time)

                start_time_tag = False
				
            start_time_P2 = copy.deepcopy(start_time)
            end_time_p = self.delayed_time(start_time_P2, self.P2)
            end_time_p = int(time.mktime(time.strptime(end_time_p, "%Y-%m-%d %H:%M:%S")))

            while True:
                self.sleep_time(start_time, self.P1)
                start_time, results_p1 = self.p1_compute(aprus_id, start_time)

                if (results_p1[3] > 0) and (results_p1[3] < 1):

                    self.sleep_time(start_time, self.P1)
                    # #
                    current_time_p2_1 = time.time()
                    if current_time_p2_1 >= end_time_p:
                        start_time, results_p2 = self.p2_compute(aprus_id, start_time_P2)

                        if (results_p2[3] > 0) and (results_p2[3] < 1):
                            self.sleep_time(start_time, self.P1)
                            start_time, results_p2_p1 = self.p2_p1_compute(aprus_id, start_time)
                            break
                        else:
                            break
                    # #
                    start_time, results_p1_p1 = self.p1_p1_compute(aprus_id, start_time)

                    if (results_p1_p1[3] > 0) and (results_p1_p1[3] < 1):
                        current_time_p2_2 = time.time()

                        if current_time_p2_2 >= end_time_p:
                            start_time, results_p2 = self.p2_compute(aprus_id, start_time_P2)

                            if (results_p2[3] > 0) and (results_p2[3] < 1):
                                self.sleep_time(start_time, self.P1)
                                start_time, results_p2_p1 = self.p2_p1_compute(aprus_id, start_time)
                                break
                            else:
                                break
                    else:
                        break
                else:
                    break

    def del_repeat_data(self, start_time_dele):
        current_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        db = pymysql.connect(host=config.HOST, user=config.USER, db=config.DB, passwd=config.PASSWORD,
                             port=config.PORT, charset=config.CHARSET)
        cursor = db.cursor()
        try:
            delete_sql = 'DELETE FROM aplec_clue WHERE (created >= %s AND created <= %s);'
            cursor.execute(delete_sql, [start_time_dele, current_time])
            db.commit()
        except Exception as err:
            print("删除历史计算数据失败！")

    def p1_compute(self,aprus_id, start_time):
        results_p1 = self.p1_cycle(aprus_id, start_time)
        self.p1_save_data(aprus_id, results_p1[6], results_p1)
        return results_p1[6], results_p1

    def p1_p1_compute(self, aprus_id, start_time):
        results_p1_p1 = self.p1_p1_cycle(aprus_id, start_time)
        self.p1_save_data(aprus_id, results_p1_p1[6], results_p1_p1)
        return results_p1_p1[6], results_p1_p1

    def p2_compute(self, aprus_id, start_time):
        results_p2 = self.p2_cycle(aprus_id, start_time)
        self.p2_save_data(aprus_id, results_p2[6], results_p2)
        return results_p2[6], results_p2

    def p2_p1_compute(self, aprus_id, start_time):
        results_p2_p1 = self.p2_p1_cycle(aprus_id, start_time)
        self.p1_save_data(aprus_id, results_p2_p1[6], results_p2_p1)
        return results_p2_p1[6], results_p2_p1

    # 等待时间
    def sleep_time(self, start_time, cycle):
        end_time_p = self.delayed_time(start_time, cycle)
        end_time_p = int(time.mktime(time.strptime(end_time_p, "%Y-%m-%d %H:%M:%S")))
        current_time = time.time()
        if end_time_p > current_time:
            time.sleep(end_time_p - current_time)

    # 用与推进时间周期
    def delayed_time(self, start_time, delayed_time):
        end_time = (datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") +
                    datetime.timedelta(seconds=delayed_time)).strftime("%Y-%m-%d %H:%M:%S")
        return end_time

    def p1_save_data(self, aprus_id, start_time, results_p1):
        msg_count = dict()
        msg_count["n_count_p1"] = results_p1[0]
        msg_count["i_count_p1"] = results_p1[1]
        msg_count["r_count_p1"] = results_p1[2]
        # 在本轮大循环未到达4小时之前，始终使用上一个周期使用的 self.comp_index_P2
        description = "{'P':'P1', 'count':{'N':%d,'I':%d,'R':%d}, 'general':%.2f}" % \
                      (msg_count["n_count_p1"],
                       msg_count["i_count_p1"],
                       msg_count["r_count_p1"],
                       results_p1[3])
        code_p1 = dict()
        code_p1["P"] = 'P1'
        code_p1["code"] = results_p1[4]["error code"]
        code_p1["msg"] = results_p1[4]["error msg"]
        code_p1 = str(code_p1)
        e_value = "{'P':'P1','e_value':%.2f}" % (results_p1[3])
        self.save_data(aprus_id, start_time, code_p1, e_value, description, results_p1[5])

    def p2_save_data(self, aprus_id, start_time, results_p2):
        msg_count = dict()
        msg_count["n_count_p2"] = results_p2[0]
        msg_count["i_count_p2"] = results_p2[1]
        msg_count["r_count_p2"] = results_p2[2]
        description = "{'P':'P2', 'count':{'N':%d,'I':%d,'R':%d}, 'general':%.2f}" % \
                      (msg_count["n_count_p2"],
                       msg_count["i_count_p2"],
                       msg_count["r_count_p2"],
                       results_p2[3])
        code_p2 = dict()
        code_p2["P"] = 'P2'
        code_p2["code"] = results_p2[4]["error code"]
        code_p2["msg"] = results_p2[4]["error msg"]
        code_p2 = str(code_p2)
        # 指数值
        e_value = "{'P':'P2','e_value':%.2f}" % (results_p2[3])
        self.save_data(aprus_id, start_time, code_p2, e_value, description, results_p2[5])

    def p1_cycle(self, aprus_id, start_time):
        p1_prob = 0.01

        msg_count = self.count(aprus_id, start_time, self.P1)

        if msg_count == 1:
            return 1
        n_count_p1, i_count_p1, r_count_p1 = msg_count[0], msg_count[1], msg_count[2]

        comp_index_P1 = (2 ** (1 - (r_count_p1 / 15)) + (2 ** n_count_p1) +
                         ((-i_count_p1) * (2 ** 6)) + (
                                     n_count_p1 * i_count_p1 * (n_count_p1 + i_count_p1) / 6 * (2 ** 6)) - 1)

        if comp_index_P1 <= 0:
            p1_data = {"error msg": "Aprus Error Quotation", "error code": "LA:E8000"}
            p1_prob = 99

        elif comp_index_P1 > 607:
            p1_data = {"error msg": "Aprus Unexceptional Reboot", "error code": "LA:E8001"}
            p1_prob = 99

        elif comp_index_P1 == 2:
            p1_data = {"error msg": "Aprus Hardware error/Power Off/Network Lost", "error code": "LA:E8002"}
            p1_prob = 99

        elif (comp_index_P1 > 1) and (comp_index_P1 < 2) or \
             (comp_index_P1 > 32) and (comp_index_P1 < 33):
            p1_data = {"error msg": "Aprus Network Error", "error code": "LA:E8003"}
            p1_prob = 99

        elif (comp_index_P1 == 1) or (comp_index_P1 == 32):
            p1_data = {"error msg": "Aprus Physical I/O Error/Data Collection Fail", "error code": "LA:E8004"}
            p1_prob = 99

        elif (comp_index_P1 > 33) and (comp_index_P1 <= 607):
            p1_prob = self.Calculateprob(start_time, aprus_id, comp_index_P1)
            p1_data = {"error msg": "Incomplete Nominal Information", "error code": "LA:E8006"}

        elif (comp_index_P1 > 3) and (comp_index_P1 < 32):
            p1_data = {"error code": "AN:00000", "error msg": "Aprus Status Normal"}
            p1_prob = 1

        elif (comp_index_P1 > 0) and (comp_index_P1 < 1):
            p1_prob = self.Calculateprob(start_time, aprus_id, comp_index_P1)
            # p1_data = {"error code": "LS:00000", "error msg": "p1适配器异常概率{0}%".format(p1_prob)}
            p1_data = {"error code": "LS:00000", "error msg": "Aprus Status Pending"}

        else:
            p1_data = {"error code": "LN:00000", "error msg": "Aprus Status Unknown"}

        results = [n_count_p1, i_count_p1, r_count_p1, comp_index_P1, p1_data, p1_prob, msg_count[3]]
        return results

    def p1_p1_cycle(self, aprus_id, start_time):
        p1_p1_prob = 0.01

        msg_count = self.count(aprus_id, start_time, self.P1)

        if msg_count == 1:
            return 1
        n_count_p1_p1, i_count_p1_p1, r_count_p1_p1 = msg_count[0], msg_count[1], msg_count[2]
        comp_index_P1_P1 = (2 ** (1 - (r_count_p1_p1 / 15)) + (2 ** n_count_p1_p1) + ((-i_count_p1_p1) * (2 ** 6)) +
                            (n_count_p1_p1 * i_count_p1_p1 * (n_count_p1_p1 + i_count_p1_p1) / 6 * (2 ** 6)) - 1)

        if comp_index_P1_P1 <= 0:
            p1_p1_data = {"error msg": "Aprus Error Quotation", "error code": "LA:E8000"}
            p1_p1_prob = 99

        elif comp_index_P1_P1 > 607:
            p1_p1_data = {"error msg": "Aprus Unexceptional Reboot", "error code": "LA:E8001"}
            p1_p1_prob = 99

        elif comp_index_P1_P1 == 2:
            p1_p1_data = {"error msg": "Aprus Hardware error/Power Off/Network Lost", "error code": "LA:E8002"}
            p1_p1_prob = 99

        elif (comp_index_P1_P1 > 33) and (comp_index_P1_P1 <= 607):
            p1_p1_prob = self.Calculateprob(start_time, aprus_id, comp_index_P1_P1)
            p1_p1_data = {"error msg": "Aprus Hardware error/Power Off/Network Lost", "error code": "LA:E8006"}

        elif (comp_index_P1_P1 > 0) and (comp_index_P1_P1 < 1):

            p1_p1_prob = self.Calculateprob(start_time, aprus_id, comp_index_P1_P1)
            # p1_p1_data = {"error code": "LS:00000", "error msg": "p1_p1适配器异常概率{0}%".format(p1_p1_prob)}
            p1_p1_data = {"error code": "LS:00000", "error msg": "Aprus Status Pending"}

        elif (comp_index_P1_P1 > 3) and (comp_index_P1_P1 < 32):
            p1_p1_data = {"error code": "AN:00000", "error msg": "Aprus Status Normal"}
            p1_p1_prob = 1
        else:
            p1_p1_data = {"error code": "LN:00000", "error msg": "Aprus Status Unknown"}

        results = [n_count_p1_p1, i_count_p1_p1, r_count_p1_p1, comp_index_P1_P1, p1_p1_data, p1_p1_prob, msg_count[3]]
        return results

    def p2_cycle(self, aprus_id, start_time):
        p2_prob = 0.01

        msg_count = self.count(aprus_id, start_time, self.P2)

        if msg_count == 1:
            return 1
        n_count_p2, i_count_p2, r_count_p2 = msg_count[0], msg_count[1], msg_count[2]

        comp_index_P2 = (2 ** (1 - (r_count_p2 / 244)) + (2 ** n_count_p2) +
                         ((-i_count_p2) * (2 ** 6)) + (
                                     n_count_p2 * i_count_p2 * (n_count_p2 + i_count_p2) / 6 * (2 ** 6)) - 1)

        if (comp_index_P2 > 3) and (comp_index_P2 < 32):
            p2_data = {"error code": "AN:00000", "error msg": "Aprus Status Normal"}
            p2_prob = 1
        elif (comp_index_P2 > 33) and (comp_index_P2 <= 607):
            p2_prob = self.Calculateprob(start_time, aprus_id, comp_index_P2)
            p2_data = {"error msg": "Incomplete Nominal Information", "error code": "LA:E8006"}
        elif (comp_index_P2 > 0) and (comp_index_P2 < 1):
            p2_prob = self.Calculateprob(start_time, aprus_id, comp_index_P2)
            # p2_data = {"error code": "LS:00000", "error msg": "p2适配器异常概率{0}%".format(p2_prob)}
            p2_data = {"error code": "LS:00000", "error msg": "Aprus Status Pending"}
        else:
            p2_data = {"error code": "LN:00000", "error msg": "Aprus Status Unknown"}

        results = [n_count_p2, i_count_p2, r_count_p2, comp_index_P2, p2_data, p2_prob, msg_count[3]]
        return results

    def p2_p1_cycle(self, aprus_id, start_time):
        p2_p1_prob = 0.01

        msg_count = self.count(aprus_id, start_time, self.P1)

        if msg_count == 1:
            return 1
        n_count_p2_p1, i_count_p2_p1, r_count_p2_p1 = msg_count[0], msg_count[1], msg_count[2]

        comp_index_P2_P1 = (2 ** (i_count_p2_p1 - (r_count_p2_p1 / 15)) + (2 ** n_count_p2_p1) + ((-i_count_p2_p1) *
                                                                                                  (2 ** 6)) + (
                            (n_count_p2_p1 * i_count_p2_p1 * (n_count_p2_p1 + i_count_p2_p1) / 6 * (2 ** 6))) - 1)

        if (comp_index_P2_P1 > 0) and (comp_index_P2_P1 < 1):
            p2_p1_data = {"error msg": "Nominal Quotation Lost", "error code": "LA:E8005"}
            p2_p1_prob = 99
        elif (comp_index_P2_P1 > 33) and (comp_index_P2_P1 <= 607):
            p2_p1_prob = self.Calculateprob(start_time, aprus_id, comp_index_P2_P1)
            p2_p1_data = {"error msg": "Incomplete Nominal Information", "error code": "LA:E8006"}
        elif (comp_index_P2_P1 > 3) and (comp_index_P2_P1 < 32):
            p2_p1_data = {"error code": "AN:00000", "error msg": "Aprus Status Normal"}
            p2_p1_prob = 1
        else:
            p2_p1_data = {"error code": "LN:00000", "error msg": "Aprus Status Unknown"}
        results = [n_count_p2_p1, i_count_p2_p1, r_count_p2_p1, comp_index_P2_P1, p2_p1_data, p2_p1_prob, msg_count[3]]
        return results

    # 概率计算
    def Calculateprob(self, start_time, aprus_id, Z_value):
        start_time_c = ((datetime.datetime.strptime(start_time.split(" ")[0], "%Y-%m-%d") +
                         datetime.timedelta(days=-1)).strftime("%Y-%m-%d")) + " 00:00:00"
        end_time_c = start_time.split(" ")[0] + " 00:00:00"

        db = pymysql.connect(host=config.HOST, user=config.USER, db=config.DB, passwd=config.PASSWORD,
                             port=config.PORT, charset=config.CHARSET)
        cursor = db.cursor()

        try:
            sql = 'select * from aplec_clue where aprus_id = %s and created >= %s and created <= %s'
            db.ping(reconnect=True)
            cursor.execute(sql, [aprus_id, start_time_c, end_time_c])
            results = cursor.fetchall()
        except Exception as err:
            print("aplec_clue表中数据未获取到！")
            return 0  # 最开始未获取到一天数据 设定概率值为零

        data = list()
        for row in results:
            single_data = dict()
            single_data["aprus_id"] = row[1]
            single_data["description"] = ast.literal_eval(row[2])
            single_data["code"] = ast.literal_eval(row[3])
            single_data["e_value"] = ast.literal_eval(row[4])
            single_data["prob"] = row[5]
            single_data["created"] = str(row[6])
            data.append(single_data)
        db.close()
        code_dict_p = {"e_value": [data[i]["e_value"]["e_value"] for i in range(len(data))],
                       "code": [data[i]["code"]["code"][0:2] for i in range(len(data))]}
        code_z = pd.DataFrame(code_dict_p)
        try:
            popu = len(code_z[code_z["code"].isin(["LA", ])])
            la = (code_z[code_z["code"].isin(["LA", ])]["e_value"].isin([str(Z_value), ]).value_counts()[True])
            priori_prob = la / popu
            mo = (code_z["code"].isin(["LA"])).value_counts()[True]
            de = (code_z["e_value"].isin([str(Z_value), ])).value_counts()[True]
            other_prob = mo / de
            fianl = round((priori_prob * other_prob), 2)
        except Exception as e:
            fianl = 0.01
        return fianl * 100

    # 记录周期时长,逆向设定开始时间与结束时间
    def time_cycle(self, start_t, cycle_time):

        end_time = (datetime.datetime.strptime(start_t, "%Y-%m-%d %H:%M:%S") +
                    datetime.timedelta(seconds=cycle_time)).strftime("%Y-%m-%d %H:%M:%S")
        end_timestamp = str(end_time)
        # 作为开始时间
        return end_timestamp

    def save_data(self,aprus_id, start_time, code, e_value, description, prob):

        prob = '%.2f' % prob
        created = start_time

        end_time = (datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") +
                    datetime.timedelta(days=-config.save_time)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = str(end_time)
        db = pymysql.connect(host=config.HOST, user=config.USER, db=config.DB, passwd=config.PASSWORD,
                             port=config.PORT, charset=config.CHARSET)
        cursor = db.cursor()

        try:
            delete_sql = 'delete from aplec_clue  where (aprus_id = %s) and created <= %s;'
            cursor.execute(delete_sql, [aprus_id, end_time])
            db.commit()
        except Exception as err:
            print("删除超出最大存储时限的计算数据失败！")

        try:
            insert_sql = 'INSERT INTO aplec_clue(aprus_id, description, code, e_value, probability, created) \
                          VALUES (%s, %s, %s, %s, %s, %s)'
            db.ping(reconnect=True)
            cursor.execute(insert_sql, [aprus_id, description, code, e_value, prob, created])
            db.commit()
        except Exception as err:
            print("存储计算数据失败！")
        cursor.close()

    def count(self, aprus_id, start_time, cycle_time):
        # start_time + P1 周期 = end_time ,逆向设定开始时间与结束时间
        end_time = self.time_cycle(start_time, cycle_time)
        try:
            n_param = {
                "aprus_id": aprus_id,
                "page_index": 100,
                "page_size": 1,
                "start_time": start_time,
                "end_time": end_time,
                "topic": "n"}
            n_res = requests.post(config.apix_url, data=n_param)
            n_json_data = json.loads(n_res.text)
            n_count = n_json_data["result"]["total_records"]
        except Exception as e:
            print("请求获取%s的%s数据失败！" % (aprus_id, 'n_count'))
            return 1
        try:
            i_param = {
                "aprus_id": aprus_id,
                "page_index": 100,
                "page_size": 1,
                "start_time": start_time,
                "end_time": end_time,
                "topic": "i"}
            i_res = requests.post(config.apix_url, data=i_param)
            i_json_data = json.loads(i_res.text)
            i_count = i_json_data["result"]["total_records"]
        except Exception as e:
            print("请求获取%s的%s数据失败！" % (aprus_id, 'i_count'))
            return 1

        try:
            r_param = {
                "aprus_id": aprus_id,
                "page_index": 100,
                "page_size": 1,
                "start_time": start_time,
                "end_time": end_time,
                "topic": "r"}
            r_res = requests.post(config.apix_url, data=r_param)
            r_json_data = json.loads(r_res.text)
            r_count = r_json_data["result"]["total_records"]
        except Exception as e:
            print("请求获取%s的%s数据失败！" % (aprus_id, 'r_count'))
            return 1
        msg_count = [n_count, i_count, r_count, end_time]
        return msg_count

    def start_main(self):
        thread_list = list()
        thread_aprus_id = list()
        try:
            r1 = requests.post(config.APIQ_URL_login, data=config.login_param)
            dic1 = json.loads(r1.text)
        except Exception as err:
            print("请求apiq的登录鉴权失败！")
            return 1
        token = dic1["data"]["token"]
        headers = {'Authorization': 'Bearer ' + token}
        apiq_data = {"is_all": "1"}
        try:
            result = requests.post(config.apiq_url_get_aprus, headers=headers, data=apiq_data)
            requests_data = json.loads(result.content.decode('utf-8'))
        except Exception as err:
            print("请求获取apiq接口的适配器ID数据失败！")
            return 1
        for single_data in requests_data['data']:
            if single_data['type'] is config.aprus_id_type:
                thread_aprus_id.append(single_data['aprus_id'])
        if thread_aprus_id is None:
            print("未获取到适配器id")

        while True:
            for aprus_id in thread_aprus_id:
                thread = threading.Thread(target=self.compute, args=(aprus_id,))
                thread_list.append(thread)
            for t in thread_list:
                t.setDaemon(True)
                t.start()
            t.join()

            break


if __name__ == '__main__':
    aprus = Aplec()
    aprus.start_main()
