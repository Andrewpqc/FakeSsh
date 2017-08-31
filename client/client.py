import socket,json,hashlib,os
from . import helper
from . import client_config
client = socket.socket()
client.connect((client_config.HOST, client_config.PORT))

while True:
    cmd = input(">>>").strip()
    if len(cmd)==0:
        continue

    #文件上传
    if cmd.startswith('put'):
        cmdList = cmd.split(' ')
        fileName = cmdList[-1]
        if os.path.isfile(fileName):
            client.send(cmd.encode("utf-8"))
            client.recv(1024)#防止粘包
            dateHeader_c2s={}
            dateHeader_c2s['filename'] = fileName
            dateHeader_c2s['size'] = os.stat(fileName).st_size
            client.send((json.dumps(dateHeader_c2s)).encode('utf-8'))
            client.recv(1024)#防止粘包
            md5 = hashlib.md5()
            with open(fileName, 'rb') as f:
                for line in f:
                    md5.update(line)
                    client.send(line)
                else:
                    client.recv(1024)#防止粘包
                    client.send(md5.hexdigest().encode('utf-8'))
                    YoN=client.recv(1024).decode('utf-8')
                    if YoN=='Y':
                        print('上传成功')
                    else:
                        print('上传失败，请重新上传,更多信息请输入“help”')
        else:
            print('请正确输入文件名！更多信息请输入“help”')

    #下载文件
    elif cmd.startswith('get'):
        client.send(cmd.encode("utf-8"))
        dateHeader_s2c = json.loads(client.recv(1024).decode('utf-8'))
        if dateHeader_s2c['status']=='Y':
            client.send(b'ok')#防止粘包
            md5 = hashlib.md5()
            filename = dateHeader_s2c['filename']
            accept_length=0
            response_length=dateHeader_s2c['size']
            while accept_length < response_length:
                with open(filename + ".s2c", 'wb') as f:
                    accept_temp = client.recv(1024)
                    md5.update(accept_temp)
                    f.write(accept_temp)
                    accept_length += len(accept_temp)
            else:
                client.send(b'ok')#防止粘包
                accept_md5 = client.recv(1024).decode('utf-8')
                if accept_md5 == md5.hexdigest():
                    print('下载成功！')
                else:
                    os.popen('rm %s' % filename + ".s2c") #删除已经下载的破碎文件
                    print('文件破碎！请重新下载')
        else:
            print('请输入一个正确的文件名')

    #帮助信息
    elif cmd=="help":
        helper.helper()


    #执行并回收普通命令的输出
    else:
        client.send(cmd.encode("utf-8"))
        dateHeader_s2c = json.loads(client.recv(1024).decode('utf-8'))
        response_length=dateHeader_s2c['size']
        accept_length=0
        accept_content=b''
        client.send(b'ok')
        while accept_length<response_length:
            accept_temp = client.recv(1024)
            accept_length+=len(accept_temp)
            accept_content+=accept_temp
        else:
            print(accept_content.decode('utf-8'))

client.close()

