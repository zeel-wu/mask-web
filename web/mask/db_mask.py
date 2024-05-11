from enum import Enum
import psycopg2
import pymysql
import logging

from web.config import STATIC_PATH
from web.mask.aes_crypt import chain_encrypt, encrypt_sensitive_info
from web.mask.mask import nlp_find_data_to_db

"""
连接数据库
    |
获取所有库信息
    |
获取库里的表信息
    |
获取表里的主键和其他表字段信息
    |
获取字段内容
    |
是否命中，命中则加密
    |
根据主键信息批量更新表字段内容
"""


class DB(Enum):
    MYSQL = 'mysql'
    POSTGRESQL = 'postgresql'
    TIDB = 'tidb'


class DBManage(object):

    def __init__(self, host, port, user, password, db=None, dtype=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        if dtype == DB.MYSQL.value or dtype == DB.TIDB.value:
            self.db_obj = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                charset='utf8mb4',
                connect_timeout=3600
            )
        elif dtype == DB.POSTGRESQL.value:
            self.db_obj = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                connect_timeout=3600
            )
        else:
            raise ValueError('未指定数据库类型！！')
        self.cursor = self.db_obj.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.db_obj:
            self.db_obj.close()


class MysqlTool(DBManage):
    default_db = {'information_schema', 'mysql', 'performance_schema', 'sys', 'INFORMATION_SCHEMA',
                  'PERFORMANCE_SCHEMA', 'METRICS_SCHEMA'}

    def get_database(self):
        self.cursor.execute("SELECT schema_name from information_schema.schemata ")
        database_list = self.cursor.fetchall()
        result = []
        for line in database_list:
            if line[0] not in MysqlTool.default_db:  # 排除默认的数据库
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
        print('get_column')
        print(result)
        return result

    #  获取字段内容
    def get_content(self, database, table, column):
        # self.cursor.execute("select `%s` from `%s`.`%s` LIMIT 0,1" % (column, database, table))
        self.cursor.execute("select `%s` from `%s`.`%s`" % (column, database, table))
        content = self.cursor.fetchall()

        if content:
            return content[0][0]

    def get_primary_key(self, db, table):
        find_primary_key_sql = f"select column_name from information_schema.columns where table_schema='{db}' and table_name= '{table}' and column_key='PRI'"
        self.cursor.execute(find_primary_key_sql)
        p_key = self.cursor.fetchone()
        return p_key[0] if p_key else ''

    # 获取表总数
    def count_max(self, column, table):
        sql_count = f"select count(`{column}`) from `{table}`"
        self.cursor.execute(sql_count)
        count = self.cursor.fetchone()
        logging.info(count[0])
        return count[0]

    def get_all_contents(self, db, table, db_cols, count=0):
        column_list = [f"`{columns}`" for columns in db_cols]
        strs = ','.join(column_list)
        weigh = 100
        limits = count // weigh
        if count % weigh != 0:
            limits += 1
        for i in range(limits):
            self.cursor.execute(f"SELECT {strs} FROM {db}.{table} LIMIT {weigh} OFFSET {i * weigh}")
            rows = self.cursor.fetchall()
            yield rows

    def masked_content(self, db, table):
        instructions = []
        new_list = []
        flag = False
        primary_key = self.get_primary_key(db, table)
        db_cols = self.get_column(db, table)
        contents = self.get_all_contents(db, table, db_cols)
        for content_tuple in contents:
            content_dict = dict(zip(db_cols, content_tuple))
            new_dict = {primary_key: content_dict[primary_key]}
            desc_dict = {'库名': db, '表名': table}
            for index, value in content_dict.items():

                if value and index != primary_key:
                    # mask_content = mask(value) # 脱敏
                    # 加密
                    mask_content = chain_encrypt(value)
                    if mask_content == value:
                        continue
                    else:
                        flag = True
                        desc_dict.update({'字段': index})
                        new_dict[index] = mask_content
                        logging.info(f'加密前：表{table}-{index}: {value}, 加密后：表{table}-{index}:{mask_content}')
                    instructions.append(desc_dict)
            new_list.append(new_dict)
        return flag, new_list

    def batch_update(self, db, table):
        primary_key = self.get_primary_key(db, table)
        count, update_list = self.masked_content(db, table)
        logging.info(f"要执行的更新语句一共={len(update_list)}条")
        print(f"要执行的更新语句一共={len(update_list)}条")
        counts = 1
        if count:
            for content_dict in update_list:
                data = ','.join([f"`{key}`='{value}'" for key, value in content_dict.items() if key != primary_key])
                sql_update = f"update {table} set {data} where `{primary_key}`= '{content_dict[primary_key]}'"
                with open(f'{STATIC_PATH}/dbscan.txt', 'a+', encoding='UTF-8') as file:
                    file.write(str(sql_update) + "\r\n")
                logging.info(sql_update)
                logging.info(f'开始执行第{counts}条：{sql_update}', )
                try:
                    self.cursor.execute(sql_update)
                    self.db.commit()
                    print('success!!!!!!!')
                    logging.info(f'第{counts}条已更新')
                    counts = counts + 1
                except Exception as e:
                    print(e)
                    self.db.rollback()
                finally:

                    logging.info(f'已完成{counts - 1}条')
            return f'{db}库中{table}敏感数据已加密.'
        else:
            msg = f'{db}库中{table}表无敏感信息.'
            return msg

    def find_sensitive_data(self, db, table):
        result = []
        primary_key = self.get_primary_key(db, table)
        print(primary_key)
        count = self.count_max(primary_key, table)
        print('count')
        print(count)
        if not count:
            return result
        columns = self.get_column(db, table)
        primary_key_index = columns.index(primary_key)
        logging.info(f'primary==={primary_key}')
        for contents in self.get_all_contents(db, table, columns, count=int(count)):
            for content_tuple in contents:
                # content_dict = dict(zip(columns, content_tuple))
                for index in range(len(content_tuple)):
                    if content_tuple[index]:
                        value = str(content_tuple[index])
                        sensitive_data = nlp_find_data_to_db(value)
                        if sensitive_data:
                            target_dict = {
                                "db": db,  # 表名
                                "table": table,  # 库名
                                "primary_key": content_tuple[primary_key_index],  # 主键名
                                "column": columns[index],  # 列名
                                "contents": value,  # 对应字段
                                "sensitive_data": sensitive_data,  # 对应敏感字段
                            }
                            # li = [db, table, columns[index], value, ','.join(sensitive_data),
                            #       content_tuple[primary_key_index]]
                            # excel_list.append(li)
                            result.append(target_dict)
                        else:
                            continue
                    else:
                        continue
        print('-----------------------')
        print(result)
        logging.info(f'find_sensitive_data {table} success')
        return result

    def db_encrypt(self, datas):
        counts = 0
        print(datas)
        for dict_data in datas:
            db = dict_data.get('db')
            table = dict_data.get('table')
            column = dict_data.get('column')
            contents = dict_data.get('contents')
            sensitive_data = dict_data.get('sensitive_data')
            primary_key_value = dict_data.get('primary_key')
            encrypt_data = encrypt_sensitive_info(contents, sensitive_data)
            primary_key = self.get_primary_key(db, table)
            if isinstance(primary_key_value, int):
                sql_update = f"UPDATE `{db}`.{table} SET {column}='{encrypt_data}' WHERE {primary_key}={primary_key_value};"
            else:
                sql_update = f"UPDATE `{db}`.{table} SET {column}='{encrypt_data}' WHERE {primary_key}='{primary_key_value}';"
            try:
                self.cursor.execute(sql_update)
            except Exception as e:
                print(e)
                logging.error(e)
                self.db.rollback()
                continue
            if counts == 1000:
                self.db.commit()
                counts = 0
            else:
                counts += 1
        self.db.commit()
        self.cursor.close()
        msg = '脱敏成功！'
        return msg


class PgTool(MysqlTool):
    def get_database(self):
        self.cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;")
        results = [row[0] for row in self.cursor.fetchall()]
        return results

    #  获取表名
    def get_table(self, database):
        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        result = [row[0] for row in self.cursor.fetchall()]
        return result

    #  获取字段名
    def get_column(self, database, table):
        self.cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
        column_list = [row[0] for row in self.cursor.fetchall()]
        return column_list

    #  获取字段内容
    def get_content(self, database, table, column):
        # self.cursor.execute("select `%s` from `%s`.`%s` LIMIT 0,1" % (column, database, table))
        self.cursor.execute("select `%s` from `%s`.`%s`" % (column, database, table))
        content = self.cursor.fetchall()

        if content:
            return content[0][0]

    def get_primary_key(self, db, table):
        find_primary_key_sql = f"SELECT column_name FROM information_schema.key_column_usage WHERE table_name='{table}'"
        self.cursor.execute(find_primary_key_sql)
        p_key = [row[0] for row in self.cursor.fetchall()]
        return p_key[0] if p_key else ''

    def count_max(self, column, table):
        sql_count = f"SELECT COUNT(*) FROM {table}"
        self.cursor.execute(sql_count)
        count = self.cursor.fetchone()
        logging.info(count[0])
        return count[0]

    def get_all_contents(self, db, table, db_cols, count=0):
        strs = ','.join(db_cols)
        weigh = 100
        limits = count // weigh
        if count % weigh != 0:
            limits += 1
        for i in range(limits):
            self.cursor.execute(f"SELECT {strs} FROM {table} LIMIT {weigh} OFFSET {i * weigh}")
            rows = self.cursor.fetchall()
            yield rows

    def find_sensitive_data(self, db, table):
        result = []
        primary_key = self.get_primary_key(db, table)
        print(primary_key)
        count = self.count_max(primary_key, table)
        print('count')
        print(count)
        if not count:
            return result
        columns = self.get_column(db, table)
        primary_key_index = columns.index(primary_key)
        logging.info(f'primary==={primary_key}')
        for contents in self.get_all_contents(db, table, columns, count=int(count)):
            for content_tuple in contents:
                # content_dict = dict(zip(columns, content_tuple))
                for index in range(len(content_tuple)):
                    if content_tuple[index]:
                        value = str(content_tuple[index])
                        sensitive_data = nlp_find_data_to_db(value)
                        if sensitive_data:
                            target_dict = {
                                "db": db,  # 表名
                                "table": table,  # 库名
                                "primary_key": content_tuple[primary_key_index],  # 主键名
                                "column": columns[index],  # 列名
                                "contents": value,  # 对应字段
                                "sensitive_data": sensitive_data,  # 对应敏感字段
                            }
                            # li = [db, table, columns[index], value, ','.join(sensitive_data),
                            #       content_tuple[primary_key_index]]
                            # excel_list.append(li)
                            result.append(target_dict)
                        else:
                            continue
                    else:
                        continue
        print('-----------------------')
        print(result)
        logging.info(f'find_sensitive_data {table} success')
        return result


if __name__ == '__main__':
    print(DB.MYSQL.value)
    print(type(DB.MYSQL.value))
