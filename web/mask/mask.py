#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import threading
from datetime import datetime
from functools import wraps

import requests


def api(context):
    # 获取文本信息
    entities = ''
    req_dict = {'content': context}
    url = ''  # 测试环境
    try:
        response = requests.post(url=url, json=req_dict)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("status") == 0:
                entities = response_json.get('entities')
    except Exception as e:
        print(e)
    # print('结果!!!')
    # print(entities)
    return entities


def nlp_find_data_to_db(text):
    text = str(text)
    from web.mask.zeelNLP.extractor import Extractor
    # results_dict = {}
    results_list = []

    ex = Extractor(text)
    emails = ex.extract_email(text)
    if emails:
        results_list.extend(emails)
    # 抽取手机号
    cellphones = ex.extract_cellphone(text)
    # 抽取身份证号
    ids = ex.extract_ids(text)
    if ids:
        results_list.extend(ids)
    # 抽取手机归属地、运营商
    # cell_locs = [ex.extract_cellphone_location(cell, 'CHN') for cell in cellphones]
    if cellphones:
        results_list.extend(cellphones)
        # results_dict['手机号对应信息'] = cell_locs
    # 抽取人名
    name = ex.extract_name(text)
    if name:
        results_list.extend(name)
    # 抽取地址信息
    locations = ex.extract_locations(text)
    if locations:
        results_list.extend(locations)
    # 抽取病历号
    medical_number = ex.extract_medical_numbers(text)
    if medical_number:
        results_list.extend(medical_number)
    # 抽取登记号
    register_number = ex.extract_register_numbers(text)
    if register_number:
        results_list.extend(register_number)
    return list(set(results_list))


def nlp_find_data_to_file(text):
    text = str(text)
    from web.mask.zeelNLP.extractor import Extractor
    results_dict = {}

    ex = Extractor(text)
    emails = ex.extract_email(text)
    if emails:
        results_dict['邮箱'] = emails
    # 抽取手机号
    cellphones = ex.extract_cellphone(text, nation='CHN')
    # 抽取身份证号
    ids = ex.extract_ids(text)
    if ids:
        results_dict['身份证号'] = ids
    # 抽取手机归属地、运营商
    cell_locs = [ex.extract_cellphone_location(cell, 'CHN') for cell in cellphones]
    if cellphones:
        results_dict['手机号'] = cellphones
        results_dict['手机号对应信息'] = cell_locs
    # 抽取人名
    name = ex.extract_name(text)
    if name:
        results_dict['人名'] = name
    # 抽取地址信息
    locations = ex.extract_locations(text)
    if locations:
        results_dict['地址'] = locations

    return results_dict


def use_range_to_db(long_text):
    res_list = []
    for text in long_text:
        if text:
            logging.info('text================')
            sen_data = use_range_to_db(text)
            if sen_data:
                res_list.append(sen_data)
    return res_list


def use_range_to_file(long_text):
    res_list = []
    for text in long_text:
        if text:
            logging.info('text================')
            sen_data = nlp_find_data_to_file(text)
            if sen_data:
                res_list.append(sen_data)
    return res_list


def use_nlp(long_text):
    result_list = []
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = [executor.submit(nlp_find_data_to_file(), txt) for txt in long_text]
        for future in concurrent.futures.as_completed(future_to_url):
            # url = future_to_url[future]
            # logging.info(url)
            logging.info('start find *************')
            # try:
            data = future.result()
            if data:
                logging.info(data)
                result_list.append(data)
    return result_list


def time_count(f):
    @wraps(f)
    def g(*args, **kwargs):
        start = datetime.now()
        f(*args, **kwargs)

        time = datetime.now() - start
        logging.info(f'用的时间为：{time}')

    return g


def do(context, row_pq):
    # 替换敏感信息内容
    if len(row_pq) == 0: return context
    p, q = row_pq[0][0], row_pq[0][1]
    row_pq.pop(0)
    return do(context[:p] + '*'.center(q - p, '*') + context[q:], row_pq)


def mask(context):
    # 存储长文本信息，及敏感信息位置开始矢量到末尾矢量
    row_pq = []
    for i in api(context):
        row_pq.append([i['start'], i['end']])
    return do(context, row_pq)


def get_sensitive_info(text):
    response = api(text)
    sensitive_data = ','.join(set([r.get('word') for r in response]))
    sensitive_data_type = ','.join(set([r.get('entityType') for r in response]))
    return sensitive_data, sensitive_data_type


def use_thread(strs):
    # 创建线程对象列表
    threads = []
    for txt in strs:
        thread = threading.Thread(target=api, args=(txt,))
        threads.append(thread)
    # 启动线程：通过调用线程对象的start()方法，启动线程并开始执行接口调用函数。
    # 启动线程
    for thread in threads:
        thread.start()
    # 等待线程完成：使用join()方法等待所有线程执行完毕。
    # 等待所有线程执行完毕
    for thread in threads:
        res = thread.join()
        print(res)


def use_future(long_txt):
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(api, txt): txt for txt in long_txt}
        for future in concurrent.futures.as_completed(future_to_url):
            # url = future_to_url[future]
            # print(url)
            try:
                data = future.result()
                print("data")
                print(data)
            except Exception as e:
                print(e)


