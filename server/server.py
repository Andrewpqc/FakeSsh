import socket,os,hashlib,json
from . import server_config
server=socket.socket()
server.bind((server_config.HOST,server_config.PORT))
server.listen(5)
print ('Server start at: %s:%s' %(server_config.HOST,server_config.PORT))
print ('wait for connection...')
while True:
    conn, addr = server.accept()
    print ('Connected by ', addr)

    while True:
        #接收到客户端输入的命令
        cmd = conn.recv(1024).decode().strip()
        if len(cmd)==0:
            print('客户端断开链接．．．')
            break

        #响应客户端的下载文件请求
        if cmd.startswith('get'):
            dataHeader_s2c = {}
            fileName=cmd.split(' ')[-1]
            if os.path.isfile(fileName):
                dataHeader_s2c['status']='Y'
                dataHeader_s2c['filename']=fileName
                dataHeader_s2c['size']=os.stat(fileName).st_size #文件大小
                conn.send((json.dumps(dataHeader_s2c)).encode('utf-8'))
                conn.recv(1024) #防止粘包
                md5=hashlib.md5()
                with open(fileName,'rb') as f:
                    for line in f:
                        md5.update(line)
                        conn.send(line)
                    else:
                        conn.recv(1024)#防止粘包
                        conn.send(md5.hexdigest().encode('utf-8'))
            else:
                dataHeader_s2c['status']='N'
                conn.send((json.dumps(dataHeader_s2c)).encode('utf-8'))

        #响应客户端的上传文件请求
        elif cmd.startswith('put'):
            conn.send(b'ok')#防止粘包
            md5 = hashlib.md5()
            raw_dateHeader = conn.recv(1024).decode('utf-8')
            dataHeader_c2s=json.loads(raw_dateHeader)
            filename = dataHeader_c2s['filename']
            accept_length=0
            response_length=dataHeader_c2s['size']
            conn.send(b'ok')#防止粘包
            with open(filename + ".c2s", 'wb') as f:
                while accept_length < response_length:
                    accept_temp = conn.recv(1024)
                    md5.update(accept_temp)
                    f.write(accept_temp)
                    accept_length += len(accept_temp)
                else:
                    conn.send(b'ok')#防止粘包
                    accept_md5 = conn.recv(1024).decode('utf-8')
                    if accept_md5 == md5.hexdigest():
                        conn.send(b'Y')
                    else:
                        os.popen('rm %s' % filename + ".c2s")
                        server.send(b'N')

                        # 响应客户端普通的命令请求

        #响应客户端的普通命令
        else:
            dataHeader_s2c = {}
            print('这是接收到的普通命令', cmd)
            res_content = os.popen(cmd).read()
            if len(res_content) == 0:
                res_content = "命令没有返回内容"
            dataHeader_s2c['type'] = 'cmd'
            dataHeader_s2c['size'] = len(res_content)
            conn.send(json.dumps(dataHeader_s2c).encode('utf-8'))
            conn.recv(1024)
            conn.send(res_content.encode("utf-8"))

conn.close()
