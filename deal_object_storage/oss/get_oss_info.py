import json
import os
import sys

import oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkram.request.v20150501.ListPoliciesForUserRequest import ListPoliciesForUserRequest

sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Deploy.settings.develop")


def get_bucket_info(auth, endpoint):
    """
    获取所有bucket信息
    """
    service = oss2.Service(auth, endpoint)
    bucket_info_list = []
    for bucket in oss2.BucketIterator(service):
        bucket_name = bucket.name
        bucket_obj = oss2.Bucket(auth, endpoint, bucket_name)
        bucket_info = bucket_obj.get_bucket_info()
        bucket_stat = bucket_obj.get_bucket_stat()

        bucket_create_time = bucket_info.creation_date
        if bucket_create_time:
            # 将tz时间改为正常时间
            # src: '2022-10-11T08:33:28.000Z'
            # dst: '2022-10-11 08:33:28'
            bucket_create_time = bucket_create_time[:-5].replace("T", " ")

        bucket_info_list.append({
            "bucket_name": bucket_info.name,
            "bucket_create_time": bucket_create_time,
            "bucket_location": bucket_info.location,
            "object_count": bucket_stat.object_count,
            "bucket_storage_type": bucket_info.storage_class,
            "bucket_intranet_endpoint": bucket_info.intranet_endpoint,
            "bucket_extranet_endpoint": bucket_info.intranet_endpoint,
            "bucket_acl_grant": bucket_info.acl.grant,
            "bucket_data_redundancy_type": bucket_info.data_redundancy_type,
            "object_storage_type": 1
        })

    return bucket_info_list


def get_user_info(accesskeyid, accesskeysecret, region_id):
    """
    获取所有用户信息
    """
    from aliyunsdkcore.request import CommonRequest
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('ram.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2015-05-01')
    request.set_action_name('ListUsers')
    client = AcsClient(accesskeyid, accesskeysecret, region_id)
    response = client.do_action(request)
    return json.loads(response.decode('utf-8'))


def get_user_policy_info(accesskeyid, accesskeysecret, region_id, username):
    """
    获取单个用户的权限
    """
    request = ListPoliciesForUserRequest()
    request.set_UserName(username)
    request.set_accept_format('json')
    client = AcsClient(accesskeyid, accesskeysecret, region_id)
    response = client.do_action(request)
    return json.loads(response.decode('utf-8'))


def sync_bucket_info_to_cmdb():

    region_id = "region"
    accesskeyid = "access_key_id"
    accesskeysecret = "access_key_secret"

    from django.conf import settings
    endpoint = settings.OSS_ENDPOINT_TEMPLATE.format(region_id)
    auth = oss2.Auth(accesskeyid, accesskeysecret)

    # 同步bucket信息到cmdb
    bucket_info_list = get_bucket_info(auth, endpoint)
    for bucket_info in bucket_info_list:
        bucket_name = bucket_info.get("bucket_name")
        ObjectStorage.objects.update_or_create(
            defaults=bucket_info,
            bucket_name=bucket_name
        )


def sync_user_info_to_cmdb(belong):
    region_id = "region"
    accesskeyid = "access_key_id"
    accesskeysecret = "access_key_secret"

    # 同步用户信息到cmdb
    user_info_dict = get_user_info(accesskeyid, accesskeysecret, region_id)
    user_info_list = []
    Users = user_info_dict.get("Users")
    if Users:
        for user_info in Users.get("User"):
            user_name = user_info.get("UserName")
            display_name = user_info.get("DisplayName", None)

            # 获取用户权限信息
            user_privileges = ""
            user_privileges_dict = get_user_policy_info(accesskeyid, accesskeysecret, region_id, user_name)
            policies = user_privileges_dict.get("Policies")
            if policies:
                for policy in policies.get("Policy"):
                    user_privileges += policy.get("PolicyName") + ","

            # 去掉末尾的逗号
            if user_privileges.endswith(","):
                user_privileges = user_privileges[:-1]

            if display_name:
                user_name = "{}---{}".format(display_name, user_name)
            user_create_time = user_info.get("CreateDate")
            if user_create_time:
                # 将tz时间改为正常时间
                # src: '2022-10-11T08:33:28.000Z'
                # dst: '2022-10-11 08:33:28'
                user_create_time = user_create_time[:-5].replace("T", " ")

            user_info_list.append({
                "username": user_name,
                "user_privileges": user_privileges,
                "object_storage_type": 1,
                "user_create_time": user_create_time
            })


    for userinfo in user_info_list:
        username = userinfo.get("username")
        ObjectStorageUser.objects.update_or_create(
            defaults=userinfo,
            username=username
        )


# 每天执行
def sync_oss_info_to_cmdb():
    sync_bucket_info_to_cmdb()
    for belong_tuple in HOST_BELONG_CHOICES:
        belong = belong_tuple[0]
        sync_user_info_to_cmdb(belong)


# 执行一次
def sync_oss_workorder_info_to_cmdb():
    oss_application_queryset = OssApplication.objects.filter(status=6)
    for oss_application in oss_application_queryset:
        bucket_name = oss_application.bucket_name
        oss_cmdb_queryset = ObjectStorage.objects.filter(bucket_name=bucket_name)
        if oss_cmdb_queryset:
            oss_cmdb_queryset = oss_cmdb_queryset[0]
            oss_cmdb_queryset.update(
                id=oss_cmdb_queryset.id,
                product=oss_application.product,
                env=oss_application.env,
                belong=oss_application.belong,
                creator=oss_application.creator,
                service=oss_application.service,
                bucket_privileges=oss_application.oss_privileges,
            )


if __name__ == '__main__':
    sync_oss_info_to_cmdb()
    sync_oss_workorder_info_to_cmdb()
