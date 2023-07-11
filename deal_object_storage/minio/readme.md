MINIO_COMMAND_PATH = "/usr/local/bin/mc"

# 增加minio主机
mc config host add minio-test http://minio-api.t1.test.com minio_test minio_test

# 获取所有管理的minio服务器
mc config host list

# 获取指定minio主机下的用户列表
mc admin user list minio-test
