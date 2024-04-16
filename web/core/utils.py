#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json
import os
import re
import chardet
import pymysql
import xlsxwriter

from web.config import ALLOWED_EXTENSIONS, STATIC_PATH


def gen_uuid():
    import uuid

    # 生成一个随机的UUID
    unique_id = uuid.uuid4()

    # 将UUID转换为字符串格式
    unique_id_str = str(unique_id)
    return unique_id_str


def get_current_time():
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return current_time


def file_transcoding(file):
    file.seek(0)

    sql_content = file.read()

    encoding = chardet.detect(sql_content)['encoding']

    sql_content = sql_content.decode(encoding).encode('utf-8')

    file.truncate()

    file.seek(0)

    file.write(sql_content)

    file.seek(0)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class DBTool(object):
    default_db = {'information_schema', 'mysql', 'performance_schema', 'sys', 'INFORMATION_SCHEMA',
                  'PERFORMANCE_SCHEMA', 'METRICS_SCHEMA'}

    def __init__(self, host, port, user, password, db=None):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

        self.db = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset='utf8mb4'
        )

        self.cursor = self.db.cursor()

    #  通过schemata获取所有数据库名称
    def get_database(self):
        self.cursor.execute("SELECT schema_name from information_schema.schemata ")
        database_list = self.cursor.fetchall()
        result = []
        for line in database_list:
            if line[0] not in DBTool.default_db:  # 排除默认的数据库
                result.append(line[0])
        return result

    #  获取表名
    def get_table(self, database):
        self.cursor.execute(
            "select table_name from information_schema.tables where table_schema= '%s' and table_name not in (select TABLE_NAME from information_schema.VIEWS) " % database)
        table_list = self.cursor.fetchall()
        result = []
        for line in table_list:
            if line[0] not in ['test']:
                result.append(line[0])
        return result

    #  获取字段名
    def get_column(self, database, table):
        self.cursor.execute(
            "select column_name from information_schema.columns where table_schema='%s' and table_name='%s'" % (
                database, table))
        column_list = self.cursor.fetchall()
        result = []
        for line in column_list:
            # if line[0] not in ['desc', ' prodline', 'keys', 'describe', 'group', 'case', 'key', 'option']:
            result.append(line[0])
        return result

    #  获取字段内容
    def get_content(self, database, table, column):
        # self.cursor.execute("select `%s` from `%s`.`%s` LIMIT 0,1" % (column, database, table))
        self.cursor.execute("select `%s` from `%s`.`%s`" % (column, database, table))
        content = self.cursor.fetchall()

        if content:
            return content[0][0]


class ReConstant(object):
    RE_VISIT_CARD_NO = r'[A-Z]{1}\d{9}'  # 就诊卡号
    # RE_NAME = r'^[\u4e00-\u9fa5]{2,4}$'  # 中文名
    # 去除 门\u95e8 文\u6587 全\u5168 阳\u9633 左右\u5de6\u53f3 项\u9879 高\u9ad8 常\u5e38 于\u4e8e 公司\u516c\u53f8 和\u548c 易\u6613 占\u5360 关\u5173 边史管段余窦时游周明花\u8fb9\u53f2\u7ba1\u6bb5\u4f59\u7aa6\u65f6
    # 黄包闻查明孔巩房 \u9ec4\u5305\u95fb\u67e5\u5b54\u5de9\u623f 关任舒曲\u5173\u4efb\u8212\u66f2 宋\u5b8b
    # 单程 \u5355\u7a0b 干毛强\u5e72\u6bdb\u5f3a 石植农沙南 \u77f3\u690d\u519c\u6c99\u5357
    # 连曾 \u8fde\u66fe 陈 \u9648 尚张官罗宫原陈白范 \u5c1a\u5f20\u5b98\u7f57\u5bab\u539f\u9648\u767d\u8303
    # 师安郁\u5e08\u5b89\u90c1 金\u91d1 康\u5eb7 畅向\u7545\u5411 \u65b9 成解\u6210\u89e3
    # 利满宁吉卫 \u5229\u6ee1\u5b81\u5409\u536b 江颜\u6c5f\u989c \u8bb8\u53f6\u6bd5\u9ebb
    # 施谢兰车景焦保甘应牛蒙梅屈衣鲍迟雷严路谷符楼申商乐米麦季辛赖莫苏桑
    # \u65bd\u8c22\u5170\u8f66\u666f\u7126\u4fdd\u7518\u5e94\u725b\u8499\u6885\u5c48\u8863\u9c8d\u8fdf\u96f7
    # \u4e25\u8def\u8c37\u7b26\u697c\u7533\u5546\u4e50\u7c73\u9ea6\u5b63\u8f9b\u8d56\u83ab\u82cf\u6851
    # 童冷温艾韦丁\u7ae5\u51b7\u6e29\u827e\u97e6\u4e01
    RE_NAME = r'[\u515a\u6b66\u534e\u5cb3\u738b\u674e\u5218\u6768\u8d75\u5434\u5f90\u5b59\u6731\u9a6c\u80e1\u90ed\u6797\u4f55\u6881\u90d1\u5510\u97e9\u66f9\u9093\u8427\u51af\u8521\u5f6d\u6f58\u8881\u8463\u5415\u9b4f\u848b\u7530\u675c\u6c88\u59dc\u5085\u949f\u5362\u6c6a\u6234\u5d14\u9646\u5ed6\u59da\u90b1\u4e18\u590f\u8c2d\u8d3e\u90b9\u718a\u5b5f\u79e6\u960e\u859b\u4faf\u9f99\u90dd\u90b5\u4e07\u987e\u8d3a\u5c39\u94b1\u6d2a\u9f9a\u6c64\u9676\u9ece\u6a0a\u4e54\u6bb7\u5e84\u7ae0\u9c81\u502a\u5e9e\u90a2\u4fde\u7fdf\u84dd\u8042\u9f50\u845b\u67f4\u4f0d\u8983\u9a86\u67f3\u6b27\u795d\u7eaa\u803f\u82a6\u82d7\u8a79\u6b27\u9773\u7941\u6d82\u88f4\u7fc1\u970d\u962e\u5c24\u67ef\u725f\u6ed5\u535c\u9976\u51cc\u76db\u5189\u55bb\u84b2\u7b80\u95f5\u90ac\u8d39\u5e2d\u664f\u968b\u53e4\u7a46\u59ec\u8c08\u67cf\u77bf\u9122\u6842\u7f2a\u5353\u891a\u683e\u621a\u5a04\u7504\u90ce\u6c60\u4e1b\u5c91\u82df\u81e7\u4f58\u535e\u865e\u5201\u5321\u6817\u4ec7\u7ec3\u695a\u63ed\u4f5f\u5c01\u71d5\u5deb\u6556\u909d\u4ef2\u8346\u50a8\u5b97\u82d1\u5bc7\u76d6\u5c60\u97a0\u8363\u4e95\u94f6\u595a\u96cd\u51bc\u6728\u90dc\u5ec9\u853a\u5180\u5e05][\u4e00-\u9fa5]{1,2}'  # 中文名
    RE_CARD_ID = r'\d{17}[\dXx]'  # 身份证号\d{17}[\dXx]|\d{15}
    RE_HEALTH_ID = r'\d{16}'  # 健康卡号
    RE_INSURANCE_NO = r'[A-Z]{2}\d{10}'  # 医保卡号
    # RE_CURRENT_ADDRESS = r'^[\u4e00-\u9fa5省市区县镇乡村{1,}\d\s\-]+[\u4e00-\u9fa5路街道巷号\d\s\-]+'  # 现住址
    # RE_CURRENT_ADDRESS = r'([^市]+自治州|.*?地区|.*?区|.+盟|市辖区|.*?市|.*?县)([^县]+县|.+区|.+市|.*?镇|.+海域|.+岛)?(.*)|(^[\\u2E80-\\u9FFF]+$)'  # 现住址
    # RE_CURRENT_ADDRESS = r'((?:[\u4E00-\u9FA5]{2,15}(?:省|自治区|北京|天津|上海|重庆))?[\u4E00-\u9FA5]{2,15}(?:市|自治州|地区|特别行政区)?[\u4E00-\u9FA5]{2,15}(?:区|县|市|旗|自治县|自治旗|林区|特区))([\u4E00-\u9FA5]{2,15}(?:街|路|巷|道|里|村|胡同|弄|庄|屯|口|层|楼|号|院|幢|栋|室))?$'  # 现住址
    # RE_CURRENT_ADDRESS = r'[\u4e00-\u9fa5]{2,5}(省|自治区|特别行政区|市)[\u4e00-\u9fa5]{2,5}(市|区|县|自治州|自治县|县级市|地区|盟|林区)?[\u4e00-\u9fa5]{0,}(街道|镇|乡)?[\u4e00-\u9fa5]{0,}(路|街|巷|弄)?[\u4e00-\u9fa5]{0,}(号|弄|村)?\d+[\u4e00-\u9fa5]{0,}'  # 现住址
    RE_CURRENT_ADDRESS = '([\u4e00-\u9fa5]{2,6}?(?:省|自治区|特别行政区|市)){1,5}([\u4e00-\u9fa5]{2,7}?(?:区|县|州)){0,1}([\u4e00-\u9fa5]{0,7}?(?:村|镇|街道)){0,8}?([\u4e00-\u9fa5]){0,}(路|街|巷|弄)?([\u4e00-\u9fa5]){0,}(号|弄|村)?(\d+[\u4e00-\u9fa5]){0,}'
    RE_PHONE = r'1[3-9]\d{9}'  # 手机号
    RE_EMAIL = r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*'  # 邮箱
    RE_WEIXIN = r'^[a-zA-Z0-9_]{6,20}$'  # 微信号


def linux_to_windows(linuxPath):
    linuxPathList = linuxPath.split('/')  # ['', 'e', 'Code', 'Shell', 'test.txt']
    del linuxPathList[0]  # ['e', 'Code', 'Shell', 'test.txt']
    linuxPathList[0] = linuxPathList[0] + ':'  # ['e:', 'Code', 'Shell', 'test.txt']
    windowsPath = '/'.join(linuxPathList)  # e:/Code/Shell/test.txt
    print(windowsPath)


def windows_to_linux(windowsPath):
    windowsPathTemp = windowsPath.split(':')[1]  # /Code/Shell/test.txt
    diskDrive = windowsPath.split(':')[0]  # e
    diskDrive = '/' + diskDrive  # /e
    linuxPath = diskDrive + windowsPathTemp  # /e/Code/Shell/test.txt
    print(linuxPath)


def check_re(content):
    if re.findall(pattern=ReConstant.RE_VISIT_CARD_NO, string=str(content)):
        field_type = "就诊卡号"
    elif re.findall(pattern=ReConstant.RE_NAME, string=str(content)):
        field_type = "中文名"
    elif re.findall(pattern=ReConstant.RE_CARD_ID, string=str(content)):
        field_type = "身份证号"
    elif re.findall(pattern=ReConstant.RE_HEALTH_ID, string=str(content)):
        field_type = "健康卡号"
    elif re.findall(pattern=ReConstant.RE_INSURANCE_NO, string=str(content)):
        field_type = "医保卡号"
    elif re.findall(pattern=ReConstant.RE_CURRENT_ADDRESS, string=str(content)):
        field_type = "现住址"
    elif re.findall(pattern=ReConstant.RE_PHONE, string=str(content)):
        field_type = "手机号"
    elif re.findall(pattern=ReConstant.RE_EMAIL, string=str(content)):
        field_type = "邮箱"
    elif re.findall(pattern=ReConstant.RE_HOSPITAL, string=str(content)):
        field_type = "医院"
    # elif re.findall(pattern=ReConstant.RE_WEIXIN, string=str(content)):
    #     field_type = "微信号"
    else:
        field_type = None
    return field_type


class Excel(object):
    """
    excel工具
    """

    num = 1

    @staticmethod
    def check_path(path=None, filename=None):
        """
        路径检查
        """
        folder_path = STATIC_PATH if not path else path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        path = os.path.join(folder_path, filename)

        if os.path.exists(path):
            index = filename.rfind('.')
            name = filename[:index]
            name += '({}).xlsx'.format(Excel.num)
            Excel.num += 1
            path = os.path.join(folder_path, name)
        return path

    @staticmethod
    def create_excel(columns, content, path=None, filename=None, sheet_name="Sheet1"):
        """
        创建excel
        :param columns: 标题行，例如[], 必传
        :param content: 正文内容，例如[[],[]], 必传
        :param path: 路径(相对路径)，例如/opt/hwop/alarms,不包含文件名
        :param filename: 文件名
        :param sheet_name: 工作簿名称
        :return:
        """
        if columns is None or content is None:
            raise ValueError

        file_path = Excel.check_path(path=path, filename=filename)
        try:
            workbook = xlsxwriter.Workbook(file_path,
                                           options={  # 全局设置
                                               'strings_to_numbers': True,  # str 类型数字转换为 int 数字
                                               'strings_to_urls': False,  # 自动识别超链接
                                               'constant_memory': False,  # 连续内存模式 (True 适用于大数据量输出)
                                           }
                                           )
            worksheet = workbook.add_worksheet(sheet_name)

            # 标题栏
            title_font = workbook.add_format({"bold": True})

            # 添加第一行为标题
            for i in range(len(columns)):
                worksheet.write(0, i, columns[i], title_font)

            # 写正文部分
            row = 1
            for j in range(len(content)):
                for k in range(len(content[j])):
                    if isinstance(content[j][k], list):
                        content[j][k] = ','.join(content[j][k])
                    worksheet.write(row, k, content[j][k])
                row += 1

            workbook.close()
        except Exception as e:
            print(e)
        return file_path


def compile_sensitive_data(content):
    content = "".join(content.split())
    sensitive_data = []
    # 编译正则表达式模式
    visit_pattern = re.compile(ReConstant.RE_VISIT_CARD_NO)
    cid_pattern = re.compile(ReConstant.RE_CARD_ID)
    name_pattern = re.compile(ReConstant.RE_NAME)
    hid_pattern = re.compile(ReConstant.RE_HEALTH_ID)
    ino_pattern = re.compile(ReConstant.RE_INSURANCE_NO)
    address_pattern = re.compile(ReConstant.RE_CURRENT_ADDRESS)
    phone_pattern = re.compile(ReConstant.RE_PHONE)
    email_pattern = re.compile(ReConstant.RE_EMAIL)
    hospital_pattern = re.compile(ReConstant.RE_HOSPITAL)
    # 就诊卡号
    for match in re.finditer(visit_pattern, content):
        sensitive_data.append(match.group())
    # 身份证
    for match in re.finditer(cid_pattern, content):
        sensitive_data.append(match.group())
    # 中文名
    for match in re.finditer(name_pattern, content):
        sensitive_data.append(match.group())
    # 健康卡号
    for match in re.finditer(hid_pattern, content):
        sensitive_data.append(match.group())
    # 医保卡号
    for match in re.finditer(ino_pattern, content):
        sensitive_data.append(match.group())
    # 住址
    for match in re.finditer(address_pattern, content):
        sensitive_data.append(match.group())
    # 手机号
    for match in re.finditer(phone_pattern, content):
        sensitive_data.append(match.group())
    # 邮箱
    for match in re.finditer(email_pattern, content):
        sensitive_data.append(match.group())
    # 医院
    for match in re.finditer(hospital_pattern, content):
        sensitive_data.append(match.group())

    return ','.join(set(sensitive_data))


def compile_sensitive_address(content):
    sensitive_data = []
    address_pattern = re.compile(ReConstant.RE_CURRENT_ADDRESS)
    for match in re.finditer(address_pattern, content):
        sensitive_data.append(match.group())
    return sensitive_data
def dump_file(content, filename, path=None):
    folder_path = STATIC_PATH if not path else path
    file_path = os.path.abspath(os.path.join(folder_path, filename))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False)
    return file_path


def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        load_data = json.load(f)
    return load_data


def scan_files(start_path):
    file_paths = set()
    for entry in os.scandir(start_path):
        if entry.is_file():
            file_paths.add(entry.path)
        elif entry.is_dir():
            file_paths.update(scan_files(entry.path))  # 递归调用的结果需要扩展到当前文件路径列表
    return file_paths


def check_path(file_path):
    from pathlib import Path

    path = Path(file_path)

    # 检查是否是文件
    if path.is_file():
        return 'file'

    # 检查是否是文件夹
    elif path.is_dir():
        return 'dir'

    # 如果都不是，说明路径不存在或者是其它类型的文件
    else:
        return False


def merge_dicts(dict1, dict2):
    """
    递归合并两个字典
    """
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            merge_dicts(dict1[key], value)
        elif key in dict1 and isinstance(dict1[key], list) and isinstance(value, list):
            dict1[key].extend(v for v in value if v not in dict1[key])
        else:
            dict1[key] = value


def merge_and_deduplicate(lst):
    result = {}
    for item in lst:
        for key, value in item.items():
            if key in result:
                if isinstance(result[key], list):
                    result[key].extend(v for v in value if v not in result[key])
                elif isinstance(result[key], dict):
                    merge_dicts(result[key], {key: value})
            else:
                result[key] = value

    return [{key: value} for key, value in result.items()]


def add_elements_and_yield(items, chunk_size=200):
    current_chunk = []
    for item in items:
        current_chunk.append(item)
        if len(current_chunk) == chunk_size:
            yield current_chunk
            current_chunk = []
    if current_chunk:
        yield current_chunk


