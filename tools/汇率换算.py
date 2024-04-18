import requests


# 美元换算成人民币
def usd_to_cny(amount_usd):
    # 请求汇率数据
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()

    # 获取美元兑人民币的汇率
    usd_to_cny_rate = data['rates']['CNY']

    # 计算换算后的金额
    amount_cny = amount_usd * usd_to_cny_rate
    return amount_cny
