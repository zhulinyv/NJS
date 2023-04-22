
import requests
import base64
import datetime

def timestamp_to_utc(timestamp):
    # 将时间戳转换为datetime对象
    dt = datetime.datetime.fromtimestamp(timestamp)
    # 将datetime对象转换为UTC时间
    utc = dt.astimezone(datetime.timezone.utc)
    # 将UTC时间格式化为字符串，注意要加上时区信息Z
    utc_str = utc.strftime("%a, %d %b %Y %H:%M:%S Z")
    return utc_str
def api_paddle_ocr(img):
    # 定义请求的url和headers
    url = "https://www.paddlepaddle.org.cn/paddlehub-api/image_classification/chinese_ocr_db_crnn_mobile"
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.paddlepaddle.org.cn",
        "Accept-Encoding": "gzip, deflate, br",
        #"Cookie": "Hm_lpvt_89be97848720f62fa00a07b1e0d83ae6=1680262774; Hm_lvt_89be97848720f62fa00a07b1e0d83ae6=1680262716",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/605.1.15",
        "Referer": "https://www.paddlepaddle.org.cn/hub/scene/ocr",
        "Content-Length": "176200",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9"
    }
    # 定义两个时间戳
    Hm_lpvt = 1680262774
    Hm_lvt = 1680262716
    # 调用函数，得到两个日期字符串
    Hm_lpvt_utc = timestamp_to_utc(Hm_lpvt)
    Hm_lvt_utc = timestamp_to_utc(Hm_lvt)
    # 将两个日期字符串拼接成Cookie的Expires属性，并添加到headers中
    headers["Cookie"] = f"Hm_lpvt_89be97848720f62fa00a07b1e0d83ae6={Hm_lpvt_utc}; Hm_lvt_89be97848720f62fa00a07b1e0d83ae6={Hm_lvt_utc}"

    # 将图片内容转换为base64编码
    pic_base64 = base64.b64encode(img.getvalue())
    # 定义请求的数据，使用base64编码的图片
    data = {
        "image": pic_base64.decode()
    }

    # 发送post请求，并获取响应
    response = requests.post(url, headers=headers, json=data)
    results = response.json()['result'][0]['data']
    text = ''
    for result in results:
        result = result['text']
        text += result + ' '

    return text

# with open(r"C:\Users\Administrator\PycharmProjects\paddle\ocr\ppocr_img\ch\ch.jpg", "rb") as pic:
#     # 读取图片内容
#     pic_data = pic.read()
#     print(api_paddle_ocr(pic_data))