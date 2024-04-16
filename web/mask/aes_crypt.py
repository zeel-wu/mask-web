#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import os.path
import re
from Crypto.Cipher import AES
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms

from web.config import AES_KEY_PATH, AES_IV


def get_aes_key(filename):
    with open(os.path.join(AES_KEY_PATH, filename), 'rb') as f:
        key = f.read()
    return key


def pad(data):
    pad_data = data
    for i in range(0, 16 - len(data)):
        pad_data = pad_data + ' '
    return pad_data


# 将明文用AES加密
def aes_encrypt(data, key=get_aes_key('aes_key.bin'), iv=AES_IV):
    # 对数据进行补齐处理
    data = data.encode('utf-8')
    length = len(data)
    padded_data = data + bytes([16 - length % 16]) * (16 - length % 16)
    # 创建加密对象
    AES_obj = AES.new(key, AES.MODE_CBC, iv.encode())
    # 完成加密
    AES_en_str = AES_obj.encrypt(padded_data)
    # 用base64编码一下
    AES_en_str = base64.b64encode(AES_en_str)
    # 最后将密文转化成字符串
    AES_en_str = AES_en_str.decode()
    return AES_en_str


def aes_decrypt(data, key=get_aes_key('aes_key.bin'), iv=AES_IV):
    # 解密过程逆着加密过程写
    # 将密文字符串重新编码成二进制形式
    data = data.encode()
    # 将base64的编码解开
    data = base64.b64decode(data)
    # 创建解密对象
    AES_de_obj = AES.new(key, AES.MODE_CBC, iv.encode())
    # 完成解密
    AES_de_str = AES_de_obj.decrypt(data)
    # # 去除补齐的数据
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(AES_de_str) + unpadder.finalize()
    AES_de_str = unpadded_data.strip()
    # 对明文解码
    AES_de_str = AES_de_str.decode()
    return AES_de_str


def mask_data(sensitive_info, param='*'):
    masked_str = sensitive_info[0] + param * (len(sensitive_info) - 1)
    return masked_str


def encrypt_sensitive_info(original_string, sensitive_info_list):
    encrypted_string = str(original_string)

    for sensitive_info in sensitive_info_list:
        # 将敏感信息加密
        encoded_info = mask_data(sensitive_info)
        # 构建正则表达式匹配模式
        pattern = re.escape(sensitive_info)

        # 替换原始字符串中的敏感信息
        encrypted_string = re.sub(pattern, encoded_info, encrypted_string)

    return encrypted_string


def chain_encrypt(text):
    from web.mask.mask import api
    json_res = api(text)
    set_word = set([i.get('word') for i in json_res])
    new_text = encrypt_sensitive_info(text, set_word)
    return new_text


