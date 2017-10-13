from optparse import OptionParser
from cantoolz.engine import *
import collections
#   collections 模块在内置的数据类型（str,int,list,tuple,dict）的基础上，
#   提供额外的数据类型，
#   1、namedtuple()
#       主要用来产生可以使用名称来访问元素的数据对象，通常用来
#       增强代码的可读性，在访问一些tuple类型的数据时尤其好用
#   2、duque
#       双端队列，能实现从队列头部快速增加和取出对象
#       方法：.popleft()   .appendleft()
#   3、Counter
#       计数器
#   4、OrderedDict
#       有序字典
#   5、defaultdict
#       带有默认值的字典

import re
#   re模块包含对正则表达式的支持

import http.server
#   Python的http服务有如下三种：
#   1、SimpleHTTPServer
#       包含执行get和head请求的SimpleHTTPRequestHandler类
#   2、BaseHTTPServer
#       提供基本的web服务和处理类，HTTPServer和BaseHTTPRequestHandler
#   3、CGIHTTPServer
#       包含处理post请求和执行CGIHTTPRequestHandler类

import socketserver
#   sockerserver简化了网络服务的编写，它有四个类：
#   TCPServer、UDPServer、UnixStreamServer、UnixDatagramServer
#   创建服务器的步骤：
#       首先，必须创建一个请求处理类，它是BaseRequestHandler的子类并重载他
#   的handle()方法。
#       然后，必须实例化一个服务器类，传入服务器的地址和请求处理程序类。
#       最后，调用handle_request()(一般是调用其他事件循环或者使用select() )
#   或server_forver()

import http.server
import json
#   json(JavaScript Object Notation)是一种轻量级的数据交换格式。它基于JavaScript
#   的一个子集。JSON采用完全独立于语言的文本格式，但是也使用了类似C语言家族的习惯。
#   这些特性使JSON成为理想的数据交换语言。易于人阅读和编写，也易于机器解析和生成
#   重要函数：
#   json.dumps()        把一个python对象编码转换成json字符串
#   json.loads()        把json格式的字符串解码转换成python对象
#   e.g.
#   data = {'a':123,'b':789,'c':456}
#   d = json.dumps(data)
#   >>>type(data)
#   >>><type 'dict'>
#   >>>type(d)
#   >>><type 'str'>

import ast
#   ast(Abstract Syntax Trees) 抽象语法树

import traceback
#   该模块被用来跟踪异常返回信息

######################################################
#                                                    # 
#          Yet Another Car Hacking Tool              #
#                   YACHT                            #
######################################################
#      Main Code Monkey    Alyosha Sintsov           #
#                              aka @asintsov         #
#      alex.sintsov@gmail.com                        #
######################################################
#                                                    #
# Want to be there as contributor?                   #
# Help us here: https://github.com/eik00d/CANToolz   #
#                                                    #
########### MAIN CONTRIBUTORS ########################
# - Boris Ryutin ( @dukebarman )                     #
#      Fist supporter and awesome guy                #
#                                                    #
#                                                    #
# - Sergey Kononenko ( @kononencheg )                #
#        Best developer, front-end ninja             #
######################################################
# We need:                                           #
#    - more hardware to support                      #
#    - unit tests                                    # 
#    - new modules!                                  #
#    - testers!                                      #
#    - doc writes                                    #
#    - bug fixers 8)                                 #
#                                                    #
#    With support of DEF CON RUSSIA                  #
#    https://defcon-russia.ru                        #
#                                                    #
######################################################



class ThreadingSimpleServer(socketserver.ThreadingMixIn,
                   http.server.HTTPServer):
    daemon_threads = True
    #集成TreadingMixIn类时需要处理异常关闭。daemon_threads指示服务器是否
    #要等待线程终止，要是线程相互独立，必须设置为True，默认是False

    # much faster rebinding
    allow_reuse_address = True
    pass

# WEB class
class WebConsole(http.server.SimpleHTTPRequestHandler):
    root = "web"
    can_engine = None

    def __init__(self, request, client_address, server):

        self.server = server
        self.protocol_version = 'HTTP/1.1'
        print(("[*] HTTPD: Received connection from %s" % (client_address[0])))
        http.server.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        resp_code = 500
        cont_type = 'text/plain'
        body = ""

        path_parts = self.path.split("/")

        if path_parts[1] == "api" and self.can_engine:
            cont_type = "application/json"
            cmd = path_parts[2]

            content_size = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_size).decode("ISO-8859-1")

            if cmd == "edit" and path_parts[3]:
                try:
                    paramz = json.loads(post_data)
                    if self.can_engine.edit_module(int(path_parts[3]), paramz) >= 0:
                        print(path_parts[3])
                        mode = 1 if self.can_engine.get_modules_list()[int(path_parts[3])][1].is_active else 0
                        print(mode)
                        if mode == 1:
                            self.can_engine.get_modules_list()[int(path_parts[3])][1].do_activate(0, 0)
                        if not self.can_engine._stop.is_set():
                            self.can_engine.get_modules_list()[int(path_parts[3])][1].do_stop(paramz)
                            self.can_engine.get_modules_list()[int(path_parts[3])][1].do_start(paramz)
                        if mode == 1:
                            self.can_engine.get_modules_list()[int(path_parts[3])][1].do_activate(0, 1)

                        new_params = self.can_engine.get_module_params(int(path_parts[3]))
                        body = json.dumps(new_params, ensure_ascii=False)
                        resp_code = 200
                    else:
                        body = "{ \"error\": \"module not found!\"}"
                        resp_code = 404
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()

            elif cmd == "cmd" and path_parts[3]:
                try:
                    paramz = json.loads(post_data).get("cmd")
                    text = self.can_engine.call_module(self.can_engine.find_module(str(path_parts[3])), str(paramz))
                    body = json.dumps({"response": str(text)})
                    resp_code = 200
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()

        self.send_response(resp_code)
        # this is new code ,if don't work ,delete it   --LouisozZ  **********************************************************************
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS,DELETE,PUT")
        self.send_header("Access-Control-Allow-Headers", "Test")
        # this is new code ,if don't work ,delete it   --LouisozZ  **********************************************************************
        
        self.send_header('X-Clacks-Overhead', 'GNU Terry Pratchett')
        self.send_header('Content-Type', cont_type)
        self.send_header('Connection', 'closed')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body.encode("ISO-8859-1"))

        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('X-Clacks-Overhead', 'GNU Terry Pratchett')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Connection', 'closed')
        self.end_headers()

    def do_GET(self):
        resp_code = 500
        cont_type = 'text/plain'
        body = ""

        path_parts = self.path.split("/")

        if path_parts[1] == "api" and self.can_engine:  # API Request
            cont_type = "application/json"
            cmd = path_parts[2]
            if cmd == "get_conf":
                response = {"queue": []}
                modz = self.can_engine.get_modules_list()
                try:
                    for name, module, params in modz:
                        response['queue'].append({'name': name, "params": params})

                    body = json.dumps(response, ensure_ascii=False)
                    resp_code = 200
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()
            elif cmd == "help" and path_parts[3]:
                try:
                    help_list = self.can_engine.get_modules_list()[self.can_engine.find_module(str(path_parts[3]))][1]._cmdList
                    response_help = collections.OrderedDict()
                    for key, cmd in help_list.items():
                        response_help[key] = {'descr': cmd.description, 'descr_param': cmd.desc_params, 'param_count': cmd.num_params}
                    body = json.dumps(response_help, ensure_ascii=False)
                    resp_code = 200
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()
            elif cmd == "start":
                try:
                    modz = self.can_engine.start_loop()
                    body = json.dumps({"status": modz})
                    resp_code = 200
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()

            elif cmd == "stop":
                try:
                    modz = self.can_engine.stop_loop()
                    body = json.dumps({"status": modz})
                    resp_code = 200
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()
            elif cmd == "status":
                try:
                    modz = self.can_engine.status_loop
                    modz2 = self.can_engine.get_modules_list()
                    modz3 = {}
                    for name, module, params in modz2:
                        btns = {}
                        for key, cmd in module._cmdList.items():
                            btns[key] = cmd.is_enabled
                        sts = module.get_status_bar()
                        modz3[name] = {"bar": sts['bar'],"text": sts['text'], "status": module.is_active, "buttons":btns}
                    body = json.dumps({"status": modz, "progress": modz3})
                    resp_code = 200
                except Exception as e:
                    resp_code = 500
                    body = "{ \"error\": "+json.dumps(str(e))+"}"
                    traceback.print_exc()

        else:  # Static content request
            if self.path == "/":
                self.path = "/index.html"

            content = self.root + self.path
            try:
                with open(content, "rb") as ins:
                    for line in ins:
                        body += line.decode("ISO-8859-1")

                ext = self.path.split(".")[-1]

                if ext == 'html':   cont_type = 'text/html'
                elif ext == 'js':   cont_type = 'text/javascript'
                elif ext == 'css':  cont_type = 'text/css'
                elif ext == 'png':  cont_type = 'image/png'
                else:               cont_type = 'text/plain'

                resp_code = 200

            except Exception as e:  # Error... almost not found, but can be other...
                # 404 not right then, but who cares?
                resp_code = 404
                cont_type = 'text/plain'
                body = str(e)

        self.send_response(resp_code)

        # this is new code ,if don't work ,delete it   --LouisozZ  **********************************************************************
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS,DELETE,PUT")
        self.send_header("Access-Control-Allow-Headers", "Test")
        # this is new code ,if don't work ,delete it   --LouisozZ  **********************************************************************

        self.send_header('X-Clacks-Overhead', 'GNU Terry Pratchett')
        self.send_header('Content-Type', cont_type)
        self.send_header('Connection', 'closed')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body.encode("ISO-8859-1"))

        return


# Console calss
class UserInterface:
    def __init__(self):
        usage = "%prog [options] for more help: %prog -h"
        parser = OptionParser(usage)

        parser.add_option("--debug", "-d", action="store", dest="DEBUG", type="int", help="Debug level")
        parser.add_option("--config", "-c", action="store", dest="CONFIG", type="string",
                          help="load config from file")
        parser.add_option("--gui", "-g", action="store", dest="GUI", type="string",
                          help="GUI mode, c - console or w - web")
        parser.add_option('--host', dest='HOST', type='string', help='host for the WEB server')
        parser.add_option("--port", "-p", action="store", dest="PORT", type="int",
                          help="port for WEB server")

        [options, args] = parser.parse_args()  # TODO need args?

        if options.DEBUG:
            self.DEBUG = options.DEBUG
        else:
            self.DEBUG = 0

        if options.HOST:
            self.HOST = options.HOST
        else:
            self.HOST = '127.0.0.1'

        if options.PORT:
            self.PORT = options.PORT
        else:
            self.PORT = 4444

        if options.CONFIG:
            self.CONFIG = options.CONFIG
        else:
            self.CONFIG = None

        if options.GUI:
            self.GUI = options.GUI
        else:
            self.GUI = "console"

        self.CANEngine = CANSploit()

        if self.CONFIG:
            self.CANEngine.load_config(self.CONFIG)

        if self.GUI[0] == "c":
            print((self.CANEngine.ascii_logo_c))
            self.console_loop()
        elif self.GUI[0] == "w":
            self.web_loop(host=self.HOST, port=self.PORT)
        else:
            print("No such GUI...")

    def loop_exit(self):
        exit()

    def web_loop(self, host='127.0.0.1', port=4444):
        print((self.CANEngine.ascii_logo_c))
        WebConsole.can_engine = self.CANEngine
        server = ThreadingSimpleServer((host, port), WebConsole)
        print('CANtoolz WEB started and bound to: http://{0}:{1}'.format(host, port))
        print("\tTo exit CTRL-C...")
        try:
            sys.stdout.flush()
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
            server.server_close()
            print("Please wait... (do not press ctr-c again!)")
            self.CANEngine.stop_loop()
            self.CANEngine.engine_exit()
            print("gg bb")
            exit()


    def console_loop(self):
        while True:
            try:
                input_ = input(">> ")
            except KeyboardInterrupt:
                input_ = "stop"

            if input_ == 'q' or input_ == 'quit':
                print("Please wait... (do not press ctr-c again!)")
                self.CANEngine.stop_loop()
                self.CANEngine.engine_exit()
                print("gg bb")
                self.loop_exit()
            elif input_ == 'start' or input_ == 's':
                self.CANEngine.start_loop()

            elif input_ == 'stop' or input_ == 's':
                self.CANEngine.stop_loop()

            elif input_ == 'view' or input_ == 'v':
                print("Loaded queue of modules: ")
                modz = self.CANEngine.get_modules_list()
                total = len(modz)
                i = 0
                print()
                for name, module, params in modz:
                    tab1 = "\t"
                    tab2 = "\t"
                    tab1 += "\t" * int(12 / len(str(name)))
                    tab2 += "\t"
                    print(("("+str(i)+")\t-\t" + name + tab1 + str(params) + tab2 + "Enabled: " + str(module.is_active)))
                    if i < total - 1:
                        print("\t\t||\t")
                        print("\t\t||\t")
                        print("\t\t\/\t")
                    i += 1
                print()

            elif input_[0:5] == 'edit ' or input_[0:2] == 'e ':  # edit params from the console
                match = re.match(r"(edit|e)\s+(\d+)\s+(.+)", input_, re.IGNORECASE)
                if match:
                    module = int(match.group(2).strip())
                    _paramz = match.group(3).strip()
                    try:
                        paramz = ast.literal_eval(_paramz)
                        self.CANEngine.edit_module(module, paramz)
                        print(("Edited module: " + str(self.CANEngine.get_modules_list()[module][0])))
                        print(("Added  params: " + str(self.CANEngine.get_module_params(module))))

                        mode = 1 if self.CANEngine.get_modules_list()[module][1].is_active else 0
                        if mode == 1:
                            self.CANEngine.get_modules_list()[module][1].do_activate(0, 0)
                        if not self.CANEngine._stop.is_set():
                            self.CANEngine.get_modules_list()[module][1].do_stop(paramz)
                            self.CANEngine.get_modules_list()[module][1].do_start(paramz)
                        if mode == 1:
                            self.CANEngine.get_modules_list()[module][1].do_activate(0, 1)
                    except Exception as e:
                        print(("Edit error: " + str(e)))
                else:
                    print("Wrong format for EDIT command")

            elif input_[0:4] == 'cmd ' or input_[0:2] == 'c ':
                match = re.match(r"(cmd|c)\s+(\d+)\s+(.*)", input_, re.IGNORECASE)
                if match:
                    _mod = int(match.group(2).strip())
                    _paramz = match.group(3).strip()
                    if 1 == 1:
                        try:
                            text = self.CANEngine.call_module(_mod, str(_paramz))
                            print("Response: " + text)
                        except Exception as e:
                            print("CMD input_ error: " + str(e))

            elif input_[0:4] == 'help' or input_[0:2] == 'h ':

                match = re.match(r"(help|h)\s+(\d+)", input_, re.IGNORECASE)
                if match:
                    try:
                        module = int(match.group(2).strip())
                        mod  = self.CANEngine.get_modules_list()[module][1]
                        print(("\nModule " + mod.__class__.__name__ + ": " + mod.name + "\n" + mod.help + \
                            "\n\nConsole commands:\n"))
                        for key, cmd in mod._cmdList.items():
                            print(("\t" + key + " " + cmd.desc_params + "\t\t - " + cmd.description + "\n"))
                    except Exception as e:
                        print(("Help error: " + str(e)))
                else:
                    print()
                    print('start\t\t\tStart sniff/mitm/fuzz on CAN buses')
                    print('stop or ctrl+c\t\tStop sniff/mitm/fuzz')
                    print('view\t\t\tList of loaded MiTM modules')
                    print('edit <index> [params]\tEdit parameters for modules')
                    print('cmd  <index> <cmd>\tSend some cmd to modules')
                    print('help\t\t\tThis menu')
                    print('help <index>\t\tHelp for module with chosen index')
                    print('quit\t\t\tClose port and exit')
                    print()


def main():
    sys.dont_write_bytecode = True
    UserInterface()


if __name__ == '__main__':
    main()
