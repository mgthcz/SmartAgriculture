import paramiko


def file_ssh(local_file_path, remote_file_path):
    # 远程主机的信息
    hostname = '192.168.60.53'
    port = 22
    username = 'nle'
    password = 'nle'

    # 建立SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    # 通过SSH连接创建SFTP客户端
    sftp = ssh.open_sftp()

    # 上传本地文件到远程主机
    sftp.put(local_file_path, remote_file_path)

    # 关闭SFTP客户端和SSH连接
    sftp.close()
    ssh.close()

    print("文件上传完成。")


# 本地文件路径
# local_file_path = r'E:\新大陆提交材料\2024007006-作品主文件夹\2024007006-01作品与答辩材料\作品文件夹\SmartAgriculture\static\images\4.jpg'
local_file_path = r'E:\新大陆提交材料\2024007006-作品主文件夹\2024007006-01作品与答辩材料\作品文件夹\SmartAgriculture\media\2.mp4'

# 远程文件路径
remote_file_path = '/home/nle/Videos/2.mp4'
file_ssh(local_file_path, remote_file_path)
