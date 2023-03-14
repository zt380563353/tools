

def read_config():
    last_time_dict = {}
    with open('oid_value.conf', 'r') as f:
        for line in f.readlines():
            # 井号为注释行
            if line.startswith("#"):
                continue
            if "=" in line:
                key = line.split('=')[0].strip()
                value = line.split('=')[1].strip()
                last_time_dict[key] = int(value)
        return last_time_dict


last_time_dict = read_config()
print(last_time_dict)
