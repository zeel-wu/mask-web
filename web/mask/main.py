import ast
import logging
import os

from web.config import STATIC_PATH
from web.core.utils import Excel, allowed_file, merge_and_deduplicate
from web.mask.EXCEL import csv_mask, XlsxExcel, txt_mask, XlsExcel
from web.mask.db_mask import MysqlTool, PgTool
from web.mask.mask import use_range_to_file


class MaskMange(object):
    @staticmethod
    def distribute_file(file_path, filename):
        logging.info(f'filepath = {file_path}')
        file_suffix = str(filename).split('.')[-1]
        logging.info('file_suffix===========')
        logging.info(file_suffix)
        if file_suffix == 'xls':
            status, res = XlsExcel.do_mask(use_range_to_file, file_path)
        elif file_suffix == 'xlsx':

            excel = XlsxExcel(file_path)
            # file_name = excel.to_do(mask_re, filename)
            status, res = excel.func_yield_mask(use_range_to_file)
        elif file_suffix == 'csv':
            status, res = csv_mask(use_range_to_file, file_path)
        else:
            status, res = txt_mask(use_range_to_file, file_path)
        if status is False:
            logging.info(f'ERROR: \n {res}')
        return status, res


class ExcelManage(object):
    @staticmethod
    def export(datas):
        from web.core.utils import get_current_time
        excel_list = []
        for str_data in datas:
            data = ast.literal_eval(str_data)
            db = data["db"]
            table = data["table"]
            index = data["index"]
            contents = data["contents"]
            sensitive_data = data["sensitive_data"]
            # sensitive_data_type = data["sensitive_data_type"]
            li = [db, table, index, contents, sensitive_data]
            excel_list.append(li)
        file_name = f"sensitive_data_{get_current_time()}.xlsx"
        Excel.create_excel(
            columns=['库名', '表名', '字段名称', '字段内容', '敏感内容'],
            content=excel_list,
            filename=file_name)
        return file_name


def process_files_in_folder(files):
    result_list = []
    for file_obj in files:
        # 处理文件，这里可以根据实际需求进行操作
        if file_obj and allowed_file(file_obj.filename):
            filename = file_obj.filename
            logging.info(filename)
            file_path = os.path.normpath(filename)
            file_path = os.path.join(STATIC_PATH, file_path)
            with open(file_path, 'wb') as f:
                while True:
                    chunk = file_obj.stream.read(8192)  # 以流式方式读取文件内容
                    if not chunk:
                        break
                    f.write(chunk)

            # future = executor.submit(MaskMange.distribute_file, file_path, filename)
            status, res = MaskMange.distribute_file(file_path, filename)
            result = merge_and_deduplicate(res) if res else []
            result_list.append({
                'filename': filename,
                'status': status,
                'result': result
            })
            try:
                os.remove(file_path)
            except Exception as e:
                logging.info(e)
        else:
            continue

    return result_list


def normal_process_files_in_folder(file_obj):
    filename = file_obj.filename
    result_dict = {'filename': filename}
    # 处理文件，这里可以根据实际需求进行操作
    if file_obj and allowed_file(file_obj.filename):
        logging.info(filename)

        file_path = os.path.normpath(filename)
        file_path = os.path.join(STATIC_PATH, file_path)
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                while True:
                    chunk = file_obj.stream.read(8192)  # 以流式方式读取文件内容
                    if not chunk:
                        break
                    f.write(chunk)
        try:
            # future = executor.submit(MaskMange.distribute_file, file_path, filename)
            status, res = MaskMange.distribute_file(file_path, filename)
            logging.info('res!!!!!!!!!!!!')
            logging.info(res)
            result = merge_and_deduplicate(res) if res and isinstance(res, list) else res
            print('merge-result==========')
            print(result)
            result_dict['status'] = status
            result_dict['result'] = result
        except Exception as e:
            os.remove(file_path)
            logging.info(e)
        else:
            try:
                os.remove(file_path)
            except Exception as e:
                logging.info(e)
    else:
        result_dict['status'] = False
        result_dict['result'] = '文件不支持！'
    return result_dict


def recurise_process_files(folder_path):
    """递归遍历文件夹

    :param folder_path: 文件目录路径
    :return:
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            logging.info(file_path)  # 处理文件，这里可以根据实际需求进行操作


def use_thread_process_file(files):
    result_list = []
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = [executor.submit(normal_process_files_in_folder, f) for f in files]
        for future in concurrent.futures.as_completed(future_to_url):
            # url = future_to_url[future]
            # logging.info(url)
            logging.info('start scan *************')
            # try:
            data = future.result()
            if data:
                result_list.append(
                    {
                        'filename': data.get('filename'),
                        'status': data.get('status'),
                        'result': data.get('result')
                    }
                )
    return result_list


class DbManage(object):
    @staticmethod
    def run(conf):
        db = conf.get('db')
        table = conf.get('table')
        db_obj = MysqlTool(
            host=conf.get('host'),
            user=conf.get('user'),
            password=conf.get('password'),
            port=conf.get('port'),
            db=conf.get('db')
        )
        if not db_obj.db:
            return "连接失败"
        if table:
            instructions = db_obj.batch_update(db, table)
        else:
            tables = db_obj.get_table(db)
            instructions = [db_obj.batch_update(db, table) for table in tables]
        return instructions

    @staticmethod
    def find(conf):
        host = conf.get('host')
        db = conf.get('db')
        table = conf.get('table')
        dtype = conf.get('db_type')
        status = True
        try:
            if dtype == 'mysql' or dtype == 'tidb':
                db_obj = MysqlTool(
                    host=host,
                    user=conf.get('user'),
                    password=conf.get('password'),
                    port=conf.get('port'),
                    db=db,
                    dtype=dtype
                )
            elif dtype == 'postgresql':
                db_obj = PgTool(
                    host=host,
                    user=conf.get('user'),
                    password=conf.get('password'),
                    port=conf.get('port'),
                    db=db,
                    dtype=dtype
                )
            else:
                db_obj = None
        except Exception as e:
            return False, str(e)
        if not db_obj.db:
            return False, "连接失败"
        if table:
            with db_obj as db_obj:
                result = db_obj.find_sensitive_data(db, table)
        else:
            with db_obj as db_obj:
                result = []
                tables = db_obj.get_table(db)
                logging.info(f'表共有{len(tables)}个 &&&&')
                for table in tables:
                    logging.info(f'当前 {table} &&&')
                    final = db_obj.find_sensitive_data(db, table)
                    result.extend(final)
        logging.info("find db ending======================")
        return status, result

    @staticmethod
    def db_encrypt(conf, data):
        db_obj = MysqlTool(
            host=conf.get('host'),
            user=conf.get('user'),
            password=conf.get('password'),
            port=conf.get('port'),
            db=conf.get('db')
        )
        if not db_obj.db:
            msg = "Connection failure！"
        else:
            try:
                with db_obj as db_obj:
                    msg = db_obj.db_encrypt(data)
            except Exception as e:
                msg = e
        return msg
