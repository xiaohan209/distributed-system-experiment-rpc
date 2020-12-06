#RPC-README

###1.配置server端

将rpc.zip文件解压后留下question和server.py在其中，其目录如下：

```shell
.
├── question
│   └── question.txt
└── server.py
```

##### 修改question.txt
可以从原始文件夹的评测题目.md中获取，也可以自行修改

#####修改server.py

1. 配置服务端端口，修改第10行dispatch_port
2. 设置调用其他用户的端口，修改第11行evaluate_port



运行server.py启用服务端



### 2.配置客户端

将rpc.zip文件解压后留下concordance.py, myProgram, otherProgram, testfile，其目录如下：

```shell
.
├── concordance.py
├── myProgram
│   └── my-origin.c
├── otherProgram
│   └── other-origin.c
└── testfile
    ├── 1.txt
    ├── 2.txt
    ├── 3.txt
    ├── 4.txt
    └── 5.txt
```



#####testfile

内容设置为测试的样例，用户自行编写，也可以增加文件

##### otherProgram

这是个中间文件夹，用来存放其他用户传过来的程序，无需修改

##### myProgram

可以自行初始化，也可以不初始化，用户在提交自己程序的时候会保存到此文件中，如果还未提交但别人调用此节点进行评测可能有两种情况。第一种是原来编译的test.exe还在，则正常返回，第二种是本身test.exe不存在，此时此节点返回CE。

##### concordance.py

1. 设置用户互相测评的端口，保证与服务端设置用户端口一致，第44行evaluate_port，修改第230行evaluate_port
2. 设置服务端IP和端口，保证与服务端设置相同，修改第41行dispatch_ip，第42行dispatch_port



运行并concordance.py启用客户端即可