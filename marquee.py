import time
import requests

# Shifu 中 PLC 的 URL
BASE_URL = "http://deviceshifu-plc.deviceshifu.svc.cluster.local/sendsinglebit"

# 位数这里面是16位
BIT_LENGTH = 16

# 每次设置的间隔秒数
INTERVAL = 0.3

# 每隔多久重新跑一次（秒）
CYCLE_INTERVAL = 20


def send_bit(digit, value):
    params = {
        "rootaddress": "Q",
        "address": 0,
        "start": 0,
        "digit": digit,
        "value": value
    }
    try:
        response = requests.get(BASE_URL, params=params)
        print(response.text)
    except Exception as e:
        print("请求失败", e)


def run_marquee_once():
    # 点亮 0 到 BIT_LENGTH-1
    for i in range(BIT_LENGTH):
        send_bit(i, 1)
        time.sleep(INTERVAL)

    # 熄灭 0 到 BIT_LENGTH-1
    for i in range(BIT_LENGTH):
        send_bit(i, 0)
        time.sleep(INTERVAL)


def loop_marquee():
    while True:
        run_marquee_once()
        time.sleep(CYCLE_INTERVAL)


if __name__ == "__main__":
    loop_marquee()

