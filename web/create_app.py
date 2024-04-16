import logging
import re
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, render_template, session, jsonify, send_file
from markupsafe import Markup
from web.config import UPLOAD_FOLDER, STATIC_PATH, LOG_PATH, SECRET_KEY
from web.core.redis_func import KeyManage
from web.core.utils import get_current_time, Excel
from web.mask.main import DbManage, use_thread_process_file

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
# 配置日志记录器
log_filename = f'{LOG_PATH}/app.log'
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=log_filename, level=logging.INFO, format=log_format)
if not app.debug:
    # 如果不处于调试模式，将日志输出到 stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)
executor = ThreadPoolExecutor()
future_dict = {}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/file/mask', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist("file")
        app.logger.info(files)
        logging.info('files!!!!!!')
        logging.info(files)
        if files:
            result = use_thread_process_file(files)
            return jsonify({
                'status_code': 200,
                'result': {
                    '扫描结果': result
                }
            })
    return render_template('upload.html')


@app.route('/download/file', methods=['GET'])
def download_file():
    db_mask_result = KeyManage.get_key()
    print('###############db_mask_result###############')
    excel_list = [list(d.values()) for d in db_mask_result]
    file_name = f"{get_current_time()}.xlsx"
    Excel.create_excel(
        columns=['库名', '表名', '主键名', '字段名', '字段内容', '敏感内容'],
        content=excel_list,
        filename=file_name)
    logging.info('find db excel save success!!!')
    return send_file(f"{STATIC_PATH}/{file_name}", as_attachment=True)


@app.route('/db/mask', methods=['GET', 'POST'])
def database_mask():
    if request.method == 'POST':
        host = request.form['host']
        port = request.form['port']
        user = request.form['username']
        password = request.form['password']
        db = request.form.get('db')
        table = request.form.get("table")
        info = {
            'host': host,
            'port': int(port),
            'user': user,
            'password': password,
            'db': db,
            'table': table
        }
        logging.info(f"'{info}'")
        session['db_info'] = info
        status, result = DbManage.find(info)
        KeyManage.set_key(result)
        print(status)
        if status:
            return render_template("detail.html", count=len(result), data=result)
        else:
            return jsonify({
                "status_code": 500,
                "msg": str(result)
            })

    return render_template('db_mask.html')


@app.route('/db/encrypt', methods=['GET'])
def db_encrypt():
    # data = request.args.get('filename')
    checked_result = KeyManage.get_key()
    db_info = session.get('db_info')  # 从会话中获取表单数据
    logging.info(f"'{db_info}'")
    res = DbManage.db_encrypt(db_info, checked_result)
    return jsonify({
        'msg': str(res),
        'status_code': 200
    })


@app.route('/check-task/<int:task_id>')
def check_task_status(task_id):
    logging.info(f'future_dict=={future_dict}')
    future = future_dict.get(task_id)
    if future.done():
        status, file_name = future.result()
        if status:
            msg = {'status': 'completed', 'file_name': file_name}
        else:
            msg = {'status': 'error', 'msg': file_name}
    else:
        msg = {'status': 'processing'}

    return msg


# 定义自定义过滤器来将敏感数据部分高亮显示
@app.template_filter('highlight_sensitive_data')
def highlight_sensitive_data(text, sensitive_data):
    for d in sensitive_data:
        if d in text:
            text = re.sub(r'{}'.format(re.escape(d)), '<span style="background-color: yellow;">{}</span>'.format(d),
                          text)
            # re.sub(pattern, encoded_info, encrypted_string)
    return Markup(text)


@app.route('/check/mask', methods=['GET'])
def check_mask():
    """
        数据库扫描结果--->手动检查删除--->从列表中删除对应数据--->生产文件（持久化存储）
    [{
            "db": db,
            "table": table,
            "index": columns[index],
            "contents": value,
            "sensitive_data": sensitive_data,
            }]
    :return:
    """
    db_mask_result = KeyManage.get_key()
    primary_id = request.args.get('primary_id')
    column = request.args.get('column')
    content = request.args.get('content')
    for item in db_mask_result:
        if item['primary_key'] == primary_id and item['column'] == column:
            item['sensitive_data'].remove(content)
    if db_mask_result:
        KeyManage.set_key(db_mask_result)
    print('************db_mask_result************')
    return jsonify(success=True)
