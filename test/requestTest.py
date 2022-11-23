import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

config = {
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "cookie": "pgv_pvid=207119658; pgv_pvi=9280456704; RK=tYbhHvz4dY; ptcz=939298ccfd23ae1eb55b57ff160cbe0641b51e47d05c924f503d34fc9dd4f855; ua_id=MA7mZv3xEFkNO7PAAAAAAOF69ndGBNx-6DZYcYlCVtg=; mm_lang=zh_CN; tvfe_boss_uuid=f6cb10b475b7dc7a; o_cookie=349414392; XWINDEXGREY=0; pac_uid=1_349414392; iip=0; wxuin=09683419096664; rewardsn=; wxtokenkey=777; vversion_name=8.2.95; pgv_info=ssid=s1098824249; gamerqqcomrouteLine=index; tokenParams=%3Fnav%3D1%26ichannel%3Dtxsppc0Ftxsp2; wwapp.vid=; wwapp.cst=; wwapp.deviceid=; video_omgid=9ff58d77e9cd1549; video_platform=2; cert=0AYe0Eaz1NRXu8aBbMItXUs4QF82Zu_Y; master_key=SfP4Ddcmjje7XvrqGEzIpvxB6m7ja6xYXptuXA42f58=; media_ticket=6c03d61962eefb66821f9e91a656968db0ec367b; media_ticket_id=3916431936; _clck=3916431936|1|f7b|0; qz_gdt=7bjkiy4yaqamcceelvcq; fqm_pvqid=95f21b45-6799-486c-88c9-856c29d11fbb; fqm_sessionid=71706e38-4472-43ea-a991-2434a9c2a358; sig=h01ff04fed64fc92e72bb040f3826a34861b134a107484bad60416a625454be6b9d1e6211f49811399a; noticeLoginFlag=1; uuid=d878599950a12684c500649c15db190f; rand_info=CAESIC2ytbmgdo9LzaPLjMkvwnRa4e5oStY8Ml2rHWOx8Lb8; slave_bizuin=3916431936; data_bizuin=3916431936; bizuin=3916431936; data_ticket=Pe/P+mauGJ4/O9ZtxiV59CyiL5mktxUgo3NHVBgSY+MEayABlp7hqirbKeN/Zxsq; slave_sid=WUhfVGYwMzRGZl9MQnRmSXlMOGlndmNlS1kySlhEVkZMWXd4X1o2Y053bHY3SFFncWxDZzJIT3J4anlqdHlOZWpxYmZLTk00dXREb01uOXFoTmlUTnlRSExGN0FmR0tMZ2RtQzNJNWpFZkw5VWdWRk5NT1hvUk45REI3dEs1M2tyMXlpaWl0TXBoM0d0N0pZ; slave_user=gh_a86fa15481c2; xid=e2df18c84c70b37e6b2dd22f102a625d",
    "token": "535528086",
}
info = {
    "name": "字节前端 ByteFE", "fakeid": "Mzg2ODQ1OTExOA=="
}

with open("../config/index.json", "r") as file:
    config = json.load(file)
    userConfig = config['userInfo']

print(userConfig)

# 请求参数
url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
headers = {
    "Cookie": userConfig['cookie'],
    "User-Agent": userConfig['userAgent']
}
begin = 1
params = {
    "action": "list_ex",
    "begin": begin,
    "count": 5,
    "fakeid": info['fakeid'],
    "type": "9",
    "token": userConfig['token'],
    "lang": "zh_CN",
    "f": "json",
    "ajax": "1"
}
resp = requests.get(url, headers=headers, params=params, verify=False).json()
if "app_msg_list" in resp:
    for item in resp["app_msg_list"]:
        info = '"{}","{}","{}","{}"'.format(
            str(item["aid"]), item['title'], item['link'], str(item['create_time']))
        print("\n".join(info.split(",")))
        print("\n\n---------------------------------------------------------------------------------\n")
