"""gunicorn + gevent 的配置文件"""
from gevent import monkey
monkey.patch_all()

# 多进程
import multiprocessing

# 绑定ip + 端口
bind = '0.0.0.0:5000'

# 进程数 = cup数量
workers = multiprocessing.cpu_count()

timeout = 18000  # Set a reasonable timeout for requests

keepalive = 500   # Set a reasonable keepalive value

# 指定每个工作的线程数
threads = 8

# 等待队列最大长度，超过这个长度的链接将被拒绝连接
backlog = 2048 * 2

# 工作模式--协程
# worker_class = 'gevent'

# 最大客户客户端并发数量，对使用协程的 worker 的工作有影响
# 服务器配置设置的值  1000：中小型项目  上万并发： 中大型
worker_connections = 500

# 进程名称
proc_name = 'gunicorn.pid'

# 进程 pid 记录文件
pidfile = 'log/gunicorn.pid'

# 日志等级
loglevel = 'warning'

# 日志文件名
logfile = 'log/gunicorn_log.log'

# 设置访问日志
accesslog = 'log/gunicorn_acess.log'

# 设置错误信息日志
errorlog  = 'log/gunicorn_error.log'