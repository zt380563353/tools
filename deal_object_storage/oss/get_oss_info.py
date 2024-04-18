import json

import oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkram.request.v20150501.ListPoliciesForUserRequest import ListPoliciesForUserRequest


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

