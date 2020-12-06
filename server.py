from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy, Transport
import os
import re
import sys
import threading
import time

livelist = {}
dispatch_port = 1357  # 可能需要修改
evaluate_port = "4242"  # 可能需要修改
question_path = "./question/"
question_file = "question.txt"
question = ""
now_ip = ''

def test():
    print("test")
    return "testOK"


class RequestHandler(SimpleXMLRPCRequestHandler):
    def __init__(self, request, client_address, server):
        global now_ip
        now_ip = client_address[0]
        if not livelist.keys().__contains__(now_ip):
            livelist[now_ip] = 0
        SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)


class interaction:
    def getEvaluater(self):
        min_value = sys.maxsize
        point = None
        for i in livelist.keys():
            if livelist[i] < min_value and i != now_ip:
                min_value = livelist[i]
                point = i
        if point is not None:
            livelist[point] += 1
        return point

    def giveback(self, ip_address):
        if livelist.keys().__contains__(ip_address):
            livelist[ip_address] -= 1
            print("giveback: ")
            print(livelist)
            return True
        print("giveback: ")
        print(livelist)
        return False

    def getQuestion(self):
        return question

    def getTxt(self, path):
        result = []
        myfile = os.listdir(path)
        myfilestr = ','.join(myfile)
        findtxt = re.compile(r'[0-9]+\.txt')
        myfile = findtxt.findall(myfilestr)
        for mf in myfile:
            print(mf)
            mf_file = open(path + '/' + mf, 'r', encoding='ascii', errors="ignore")
            result.append(''.join(mf_file.readlines()))
        return result


def get_question_content():
    global question
    while True:
        os.chdir(question_path)
        file = open(question_file, encoding='utf-8', errors="ignore")
        question = ''.join(file.readlines())
        file.close()
        os.chdir("../")
        time.sleep(1)


def check():
    while True:
        print("check:")
        for i in list(livelist):
            testIP = "http://" + i + ":" + evaluate_port
            print("checkip" + testIP)
            server = ServerProxy(testIP)
            try:
                server.testConnect()
            except Exception:
                livelist.pop(i)
                print(Exception)
        time.sleep(5)


def open_server():
    print("start")
    obj = interaction()
    server = SimpleXMLRPCServer(("0.0.0.0", dispatch_port), RequestHandler, allow_none=True)
    # 将实例注册给rpc server
    server.register_instance(obj)
    server.register_function(test, "test")
    print("Real Server Listening on port 1357")
    server.serve_forever()


if __name__ == '__main__':
    question_thread = threading.Thread(target=get_question_content)
    question_thread.start()

    check_thread = threading.Thread(target=check)
    check_thread.start()

    server_thread = threading.Thread(target=open_server)
    server_thread.start()

