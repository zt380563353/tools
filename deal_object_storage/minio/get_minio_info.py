import os
import re
import subprocess
import sys

from minio import Minio


def get_bucket_info(minio_client):
    bucket_info_list = []
    bucket_obj_list = minio_client.list_buckets()
    for bucket_obj in bucket_obj_list:
        bucket_name = bucket_obj.name
        created_time = bucket_obj.creation_date.strftime("%Y-%m-%d %H:%M:%S")

        bucket_location = minio_client._get_bucket_location(bucket_name)
        objects_obj_list = list(minio_client.list_objects(bucket_name))
        object_count = len(objects_obj_list)
        for objects_obj in objects_obj_list:
            if objects_obj.is_dir:
                objects_name = objects_obj.object_name[:-1]
                bucket_info_list.append({
                    "bucket_name": "{}/{}".format(bucket_name, objects_name),
                    "bucket_create_time": created_time,
                    "bucket_location": bucket_location,
                    "object_count": object_count,
                    "object_storage_type": 2
                })
    return bucket_info_list


MINIO_COMMAND_PATH = "/usr/local/bin/mc"


class MinioClientCmd:
    def __init__(self, api, access_key, secret_key, minio_alias_hostname="minio"):
        self.mc = MINIO_COMMAND_PATH
        self.minio_domain = api
        self.access_key = access_key
        self.secret_key = secret_key
        # 该名称为自定义名称，minio远程连接需要给远程的minio服务器起一个名字
        self.minio_alias_hostname = minio_alias_hostname

    def get_minio_host_list(self):
        _cmd = f"{self.mc} config host list"
        ret = subprocess.getoutput(_cmd)
        return ret

    def get_minio_user_list(self):
        _cmd = f"{self.mc} admin user list {self.minio_alias_hostname}"
        ret = subprocess.getoutput(_cmd)
        return ret


def sync_minio_info_to_cmdb(api, access_key, secret_key, minio_alias_hostname):
    minio_client = Minio(
        api,
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )
    # 同步bucket_info
    bucket_info_list = get_bucket_info(minio_client)
    for bucket_info in bucket_info_list:
        print(bucket_info)

    # 同步用户
    mc_cmd = MinioClientCmd(api, access_key, secret_key, minio_alias_hostname)
    result = mc_cmd.get_minio_host_list()
    # 如果没有管理该主机，则结束
    if minio_alias_hostname not in result:
        print("minio: {} not in hostlist".format(minio_alias_hostname))
        exit(0)
    else:
        result = mc_cmd.get_minio_user_list()
        userinfo_list = []
        for userinfo in result.split("\n"):
            match = re.search(r'(\w+)\s+(\w+)(?:\s+(\w+))?', userinfo)
            if match:
                status = match.group(1)
                username = match.group(2)
                user_privileges = match.group(3) if match.group(3) else ""
                userinfo_list.append({
                    "username": username,
                    "user_privileges": user_privileges,
                    "object_storage_type": 2
                })
            else:
                print("无法解析该行,userinfo: {}".format(userinfo))
        for userinfo in userinfo_list:
            print(userinfo)


if __name__ == '__main__':
    api = "minio-aaaa.test.com"
    access_key = "minio_test"
    secret_key = "minio_test"
    minio_alias_hostname = "minio-test"
    sync_minio_info_to_cmdb(api, access_key, secret_key, minio_alias_hostname)
