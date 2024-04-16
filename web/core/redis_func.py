import json
import time

import redis


def redis_connect():
    from web.config import REDIS_HOST, REDIS_PORT
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password='')
    cache = redis.Redis(connection_pool=pool)
    return cache


def redis_pipeline():
    pipeline = redis_connect().pipeline()
    return pipeline


def incr_id():
    """利用redis实现自增整数

    """
    cache = redis_connect()
    inc_num = cache.hincrby("inc_num", "a", )  # 每次返回一个整数,逐渐增加1
    return inc_num


class UserSignManage(object):
    cache = redis_connect()

    @classmethod
    def insert_data(cls, user_id):
        # bitmap  key
        bit_key = f"sign{time.strftime('%Y%m%d', time.localtime(time.time()))}"

        cls.cache.setbit(bit_key, user_id, 1)

    @classmethod
    def get_data(cls, date=''):
        dates = cls.cache.keys(f'sign{date}*')
        return [i.decode('utf-8').split("sign")[1] for i in dates] if dates else []

    @classmethod
    def get_today_status(cls):
        today = time.strftime('%Y%m%d', time.localtime(time.time()))
        result = cls.cache.keys(f'sign{today}*')
        if result:
            return True
        else:
            return False


class KeyManage(object):
    cache = redis_connect()

    @classmethod
    def set_key(cls, item, key='sensitive_data', expire=None):
        item = json.dumps(item, ensure_ascii=False)
        if cls.cache.set(key, item):  # 设置缓存值，永不过期
            return True
        else:
            return False

    @classmethod
    def get_key(cls, key='sensitive_data'):
        cached_value = cls.cache.get(key)  # 获取缓存值
        if cached_value:
            cached_value = json.loads(cached_value)
            return cached_value
        else:
            return None
