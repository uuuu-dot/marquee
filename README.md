# Shifu

### question:

```
在Kubernetes中运行Shifu并编写一个应用

请参考以下指南，部署并运行Shifu：https://shifu.dev/docs/tutorials/demo-install/
运行一个PLC的数字孪生：https://shifu.dev/docs/tutorials/demo-try/#2-interact-with-the-thermometer
编写一个Python应用
1 0b0000000000000001 
2 0b0000000000000011
3 0b0000000000000111
4 0b0000000000001111
5 ...
6 0b1111111111111111
7 0b1111111111111110
8 0b1111111111111100
9 ...

定期调用设置PLC比特位的/sendsinglebit接口，实现一个走马灯的效果
Python的应用需要容器化
Python的应用需要运行在Shifu的k8s集群当中
最终通过kubectl logs命令可以查看打印的值
```

### 部署并运行Shifu

```
curl -sfL https://raw.githubusercontent.com/Edgenesis/shifu/main/test/scripts/shifu-demo-install.sh | sudo sh -
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744860940279-398a9789-8fb8-4dd5-9487-953a91350f76.png?x-oss-process=image%2Fformat%2Cwebp%2Fresize%2Cw_1500%2Climit_0)

```
sudo kubectl get pods -A   # 列出所有命名空间（All namespaces） 中正在运行的 Pod 资源
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744860989704-d07f3c75-d12e-48d2-bb5e-81bd413f16da.png?x-oss-process=image%2Fformat%2Cwebp%2Fresize%2Cw_1500%2Climit_0)

```
sudo kind get clusters		# 查看创建的测试集群
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744880899554-eee817f9-14ab-4eb2-834d-14c307a7a2c8.png?x-oss-process=image%2Fformat%2Cwebp)

**⚠️本地有一个通过 kind 创建的 Kubernetes 测试集群，集群名字就叫：kind**

```
sudo kubectl config current-context		# 查看是否连接到集群
```



### 运行内置的PLC数字孪生应用

cd进入shifudemos目录

```
sudo kubectl run --image=nginx:1.21 nginx		# 在Kubernetes 中创建并运行一个名为 nginx 的 Pod，它里面运行的是 nginx:1.21 镜像

sudo kubectl get pods -A | grep nginx		# 查看所有命名空间下是否有包含 nginx 关键字的 Pod，并显示相关信息。
```



```
sudo kubectl get pods -A -o wide		# 查看已有pod的详细信息
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744881596446-82f55451-23cc-4712-bc76-bc89a6ea21ec.png?x-oss-process=image%2Fformat%2Cwebp%2Fresize%2Cw_1500%2Climit_0)



#### 应用四 —— PLC（题目背景）

步骤1.创建PLC的数字孪生

```
sudo kubectl apply -f run_dir/shifu/demo_device/edgedevice-plc
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744891112994-a54d2d81-cdf7-4852-a72b-32dc1bc08525.png?x-oss-process=image%2Fformat%2Cwebp)



```
sudo kubectl get pods -A | grep plc		# 筛选名为plc的pod并展示
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744891153801-cd587d28-ae31-46cf-b298-9307bd2ecbb5.png?x-oss-process=image%2Fformat%2Cwebp)



步骤2 与PLC数字孪生交互

```
sudo kubectl exec -it nginx -- bash		# 进入nginx
```

这里面有个问题为什么要进入nginx呢

`nginx` ke以理解位一个**中间 Pod**，从这个 Pod 里能访问集群内服务（比如 Shifu）。

Shifu 和 PLC 部署在集群内部，Shifu 会暴露一个 Service（ClusterIP），这个 Service 只能在 Kubernetes 内部被访问。

要跟 Shifu 通信，有两个途径：

- 代码部署在集群里 ——这个也是后面python—>打包位docker —>部署成pod到集群内部—>定期自动发请求给Shifu
- 临时进入 Pod 来调试（用 `kubectl exec`）



LC的数字孪生通过 `http://deviceshifu-plc.deviceshifu.svc.cluster.local` 进行交互，将PLC `Q0内存` 的第0位设置成 `1`

```
curl "deviceshifu-plc.deviceshifu.svc.cluster.local/sendsinglebit?rootaddress=Q&address=0&start=0&digit=0&value=1"; echo
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744891508296-064fdd1e-286c-4baa-8f9f-3ba190657895.png?x-oss-process=image%2Fformat%2Cwebp)

也就是说其实，只要调用sendsingbit接口就可以了，**主要就是改digit和value参数，来使得对应的位置上为对应数字**



### 实现跑马灯

**需要实现的效果**

<u>定期调用设置PLC比特位的/sendsinglebit接口，实现一个走马灯的效果，如下所示</u>

```
0b0000000000000001 
0b0000000000000011
0b0000000000000111
0b0000000000001111
...
0b1111111111111111
0b1111111111111110
0b1111111111111100

```

#### **步骤1 实现跑马灯的逻辑**

<u>思路：就是定期循环的调用接口，依次将对应digit的值改为1等这一轮结束，再将digit的值改为0。这样就为</u>

<u>一个跑马等的循环之后定期调用这样一个跑马灯循环即可</u>

创建如下文件结构

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744939496723-d23387ec-c8eb-4714-bd78-0827e4b19fec.png?x-oss-process=image%2Fformat%2Cwebp)

##### marquee.py

```
# marquee.py
import time
import requests

# Shifu 中 PLC 的 URL
BASE_URL = "http://deviceshifu-plc.deviceshifu.svc.cluster.local/sendsinglebit"

# 位数
BIT_LENGTH = 16

# 每次设置的间隔秒数
INTERVAL = 0.3

# 每隔多久重新跑一次（秒）
CYCLE_INTERVAL = 15


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

```

##### Dockerfile

```
FROM python:3.11-slim

WORKDIR /app

COPY marquee.py .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests

CMD ["python", "marquee.py"]
```



#### 步骤2 创建应用加载到kind并启动pod

步骤如下

```
sudo docker build --tag plc-marquee:v0.0.1 .		#创建应用

sudo kind load docker-image plc-marquee:v0.0.1		#加载应用镜像到kind

sudo kubectl run plc-marquee --image=plc-marquee:v0.0.1 -n deviceshifu		#启动pod

sudo kubectl logs -n deviceshifu plc-marquee -f		#在那个namespace就在哪查
```

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744939394249-841e1f23-dc71-4a52-8f66-a1965e630aac.png?x-oss-process=image%2Fformat%2Cwebp%2Fresize%2Cw_1500%2Climit_0)

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744939740617-cf16c13f-0f0f-4c8b-aa92-6073f5ee60a5.png?x-oss-process=image%2Fformat%2Cwebp)

最终实现结果

![image.png](https://cdn.nlark.com/yuque/0/2025/png/22654080/1744940260284-bf356c3c-e0da-4702-9aad-08b7da53e3f0.png?x-oss-process=image%2Fformat%2Cwebp)

另外不需要的时候也要记得删除pod及镜像

```
sudo kubectl delete pod plc-marquee -n deviceshifu		#删除pod
sudo docker rmi plc-marquee:v0.0.1		# 删除镜像
```
