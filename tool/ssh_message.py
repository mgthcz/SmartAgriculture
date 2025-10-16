import paramiko

# 远程主机的信息
hostname = '192.168.60.53'
port = 22
username = 'nle'
password = 'nle'

# 要在远程终端执行的命令
command = 'echo 1'

# 建立SSH连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, port, username, password)

# 执行命令
stdin, stdout, stderr = ssh.exec_command(command)

# 读取命令输出
output = stdout.read().decode('utf-8')

# 打印输出结果
print("远程屏幕输出:", output)

# 关闭SSH连接
ssh.close()
