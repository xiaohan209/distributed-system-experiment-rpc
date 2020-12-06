import threading
import xmlrpc.client
from pathlib import Path
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer
import time
import os
from subprocess import PIPE, Popen
import platform
from tkinter import *
from tkinter import messagebox
from tkinter import StringVar

originLock = threading.Lock()
dirty = True


class Backup(threading.Thread):
    input_str = ''
    my_P = ''
    my_file_name = ''

    def __init__(self, input_str, my_P, my_file_name):
        threading.Thread.__init__(self)
        self.input_str = input_str
        self.my_P = my_P
        self.my_file_name = my_file_name

    def run(self):
        global dirty
        originLock.acquire(True)
        dup_file = open(self.my_P + self.my_file_name, "w+", encoding='ascii')
        dup_file.write(self.input_str)
        dup_file.close()
        dirty = True
        originLock.release()


class ClientGUI(Frame):
    my_P = './myProgram/'
    my_file_name = 'my-origin.c'
    dispatch_ip = '10.135.20.210'
    dispatch_port = '1357'
    evaluator_ip = ''
    evaluate_port = '4242'
    my_output = []
    other_output = []
    compare_result = []
    result_show = []
    result_text_show = []
    question_description = ''
    flag_my = []
    flag_other = []
    description = None
    result_part = None
    problem_des = None

    def __init__(self):
        dispatch_server = xmlrpc.client.ServerProxy("http://" + self.dispatch_ip + ":" + self.dispatch_port)
        Frame.__init__(self)
        self.pack()
        self.windowInit()
        self.description = StringVar()
        self.createWidgets()
        self.description.set(dispatch_server.getQuestion())
        self.problem_des.update()

    def windowInit(self):
        self.master.title('欢迎来到程序互评窗口')
        width, height = self.master.maxsize()
        self.master.geometry("1200x750".format(width, height))

    def createWidgets(self):
        lPart = Frame(self)

        # 题目描述部分
        proDes = Frame(lPart)

        desLabel = Label(proDes, text="题目描述", height=3, font=('微软雅黑', 12))
        desLabel.pack(side=TOP)

        self.problem_des = Message(proDes, textvariable=self.description, width=300)
        self.problem_des.pack(side=TOP, fill=X)

        proDes.pack(side=LEFT, fill=Y)

        # 输入文本框
        textPart = Frame(lPart)

        textLabel = Label(textPart, text="请在此输入你的程序", height=3, font=('微软雅黑', 12))
        textLabel.pack(side=TOP)

        xScroll = Scrollbar(textPart, orient=HORIZONTAL)
        yScroll = Scrollbar(textPart, orient=VERTICAL)
        textEntry = Text(textPart, width=70, height=36, xscrollcommand=xScroll.set, yscrollcommand=yScroll.set,
                         wrap=NONE)

        submitButton = Button(textPart, text='提交')
        submitButton.pack(side=BOTTOM)
        submitButton.bind('<Button-1>', lambda event: self.buttonBind(text=textEntry.get("1.0", "end")))

        xScroll.pack(side=BOTTOM, fill=X)
        xScroll.config(command=textEntry.xview)
        yScroll.pack(side=RIGHT, fill=Y)
        yScroll.config(command=textEntry.yview)
        textEntry.pack(fill=BOTH)

        textPart.pack(side=LEFT, fill=Y)

        lPart.pack(side=LEFT, fill=Y)

        # 返回结果框
        self.rPart = Frame(self)
        resultLabel = Label(self.rPart, text="评测结果")
        resultLabel.pack(side=TOP)
        self.rPart.pack(side=LEFT, fill=BOTH)

    def result(self):
        count = len(self.compare_result)
        for i in range(0, count):
            locals()["result" + str(i)] = Frame(self.rPart)
            locals()["result_text" + str(i)] = Message(locals()["result" + str(i)], text=self.compare_result[i],
                                                       width=100)
            locals()["result_text" + str(i)].pack(side=LEFT)
            self.detail(i, locals()["result" + str(i)])
            locals()["result" + str(i)].pack()
            self.result_show.append(locals()["result" + str(i)])
            self.result_text_show.append(locals()["result_text" + str(i)])
        return

    def detail(self, i, result):
        locals()["result_button" + str(i)] = Button(result, text="查看详情", command=lambda: self.create(i=i))
        locals()["result_button" + str(i)].pack(side=RIGHT)
        return

    def create(self, i):
        top = Toplevel()
        top.geometry("400x630")
        top.title("result" + str(i + 1))

        lPart = Frame(top)
        lTitle = Message(lPart, text="评测机输出结果", width=350)
        lTitle.pack(side=TOP, fill=BOTH)
        otherResult = Message(lPart, text=self.other_output[i], width=350)
        otherResult.pack(fill=BOTH)
        lPart.pack(side=LEFT, fill=BOTH)
        rPart = Frame(top)
        rTitle = Message(rPart, text="你的输出结果", width=350)
        rTitle.pack(side=TOP, fill=BOTH)
        myResult = Message(rPart, text=self.my_output[i], width=350)
        myResult.pack(fill=BOTH)
        rPart.pack(side=RIGHT, fill=BOTH)
        return

    def delete(self):
        while self.result_show:
            show = self.result_show.pop()
            show.destroy()
        while self.result_text_show:
            show = self.result_text_show.pop()
            show.destroy()

    def buttonBind(self, text):
        self.submit(text)
        self.delete()
        self.result()
        return

    def submit(self, text):
        # update my-origin.c

        down_file = Backup(text, self.my_P, self.my_file_name)
        down_file.start()
        # connect to dispatcher
        dispatch_server = xmlrpc.client.ServerProxy("http://" + self.dispatch_ip + ":" + self.dispatch_port)
        self.description.set(dispatch_server.getQuestion())
        self.problem_des.update()
        self.evaluator_ip = dispatch_server.getEvaluater()
        if self.evaluator_ip is not None:
            # call evaluate
            evaluate_server = xmlrpc.client.ServerProxy("http://" + self.evaluator_ip + ":" + self.evaluate_port)
            my_out, other_out, my_error, other_error = evaluate_server.evaluate(text)
            self.compare_result.clear()
            self.my_output.clear()
            self.other_output.clear()
            for i in range(len(my_out)):
                my_flag = (my_error[i] != "")
                other_flag = (other_error[i] != "")
                self.my_output.append(my_error[i] if my_flag else my_out[i])
                self.other_output.append(other_error[i] if other_flag else other_out[i])
                if my_flag and other_flag:
                    self.compare_result.append("两人全CE")
                elif my_flag:
                    self.compare_result.append("您CE")
                elif other_flag:
                    self.compare_result.append("他人CE")
                else:
                    self.compare_result.append("AC" if (self.my_output[i] == self.other_output[i]) else "WA")
            # give back
            dispatch_server.giveback(self.evaluator_ip)
        else:
            messagebox.showerror("错误提示", "此时只有您的结点，请耐心等待！")


def openFiles(file):
    inputting_path = "./testfile/" + file
    input_file = open(inputting_path, "r", encoding='ascii', errors="ignore")
    return input_file


def file_compare(my_output, other_output):
    my_list = my_output.readlines()
    other_list = other_output.readlines()
    my_count = len(my_list)
    other_count = len(other_list)
    if other_count != my_count:
        return 2
    else:
        i = 0
        while i < other_count:
            r = (other_list[i] == my_list[i])
            if not r:
                return 2
            i = i + 1
        if i == other_count:
            return 1


class ClientServer(threading.Thread):
    evaluate_server = None
    evaluate_port = 4242  # 可能需要修改
    testing_path = "./testfile/"
    file_exe = "test.exe"
    my_P = './myProgram/'
    other_P = './otherProgram/'
    compile_my = "gcc -o ./myProgram/test.exe ./myProgram/*.c"
    compile_other = "gcc -o ./otherProgram/test.exe ./otherProgram/*.c"
    isWindows = platform.system().lower() == 'windows'

    def testConnect(self):
        return "OK"

    def executeFiles(self, input_file):
        if self.isWindows:
            file = Popen([self.file_exe], stdin=input_file, stdout=PIPE, stderr=PIPE, shell=True)
        else:
            file = Popen(["./" + self.file_exe], stdin=input_file, stdout=PIPE, stderr=PIPE, shell=True)
        test_out = file.stdout.read().decode("utf-8")
        test_error = file.stderr.read().decode("utf-8")
        return test_out, test_error

    def evaluate(self, pro_str):
        global dirty
        my_out = []
        other_out = []
        my_error = []
        other_error = []
        my_output_str = ""
        my_error_str = ""
        other_output_str = ""
        other_error_str = ""

        origin_file = open("./otherProgram/other-origin.c", "w+", encoding='ascii', errors="ignore")
        origin_file.write(pro_str)
        origin_file.close()

        # lock file
        originLock.acquire(True)
        if dirty:
            os.system(self.compile_my)
            dirty = False
        originLock.release()
        os.system(self.compile_other)
        dirs = os.listdir(self.testing_path)
        for file in dirs:
            print("testing on " + file)
            input_file = openFiles(file)
            os.chdir(self.my_P)
            my_output_str, my_error_str = self.executeFiles(input_file)

            os.chdir("../")
            input_file.seek(0, 0)
            os.chdir(self.other_P)
            other_output_str, other_error_str = self.executeFiles(input_file)

            os.chdir("../")
            # compare???
            my_out.append(my_output_str)
            my_error.append(my_error_str)
            other_out.append(other_output_str)
            other_error.append(other_error_str)
            input_file.close()
        if os.path.exists(self.other_P + self.file_exe):
            os.remove(self.other_P + self.file_exe)
        return other_out, my_out, other_error, my_error

    def __init__(self):
        threading.Thread.__init__(self)
        self.evaluate_server = SimpleXMLRPCServer(("0.0.0.0", self.evaluate_port))
        # 将实例注册给rpc server
        # self.evaluate_server.register_function(self.evaluate, "evaluate")
        self.evaluate_server.register_instance(self)

    def run(self):
        my_file = Path("./myProgram/my-origin.c")
        while not my_file.exists():
            time.sleep(1)
        print("Evaluate Server Listening on port 4242")
        self.evaluate_server.serve_forever()


if __name__ == '__main__':
    # open server

    server = ClientServer()
    server.start()
    # open Client
    client = ClientGUI()
    client.mainloop()
