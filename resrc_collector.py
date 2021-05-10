import os
import requests as req
from urllib import request as url_req
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
req.packages.urllib3.disable_warnings(InsecureRequestWarning)

# TODO. 로그 기록에서도 똑같은 기록 안생기게 + 탐색 시간도 추가
# TODO. 그냥 루트 경로 주면 깊숙히 다 뒤져오게 하면 좋을 듯

COOKIES = {}

WEB_NAME = "naver"
URL = "https://www.naver.com/"
PROJECT_PATH = os.path.dirname(os.path.abspath(
    __file__)) + "\\" + WEB_NAME

TARGETS = [
    "https://www.naver.com/",
]

RESOURCE_TARGETS = [
]

EXCLUDE_TARGETS = [
]

LOG_PATH = os.path.dirname(os.path.abspath(__file__))
DO_UPDATE = False
RECURSIVE = True
AUTO_YES = True

TMP_ARRIVED = []


def resrc_parse(content, content_url):
    rp_resources = []

    static_indexs = [m.start() for m in re.finditer('/static/', content)]
    rel_static_indexs = [m.start() for m in re.finditer('../', content)]

    for static_i in static_indexs + rel_static_indexs:
        if 6 <= static_i and \
                content[static_i-5: static_i] == 'src="' or \
                content[static_i-5: static_i] == 'url("' or \
                content[static_i-6: static_i] == 'href="':
            static_end_i = content.find('"', static_i)
        elif 6 <= static_i and \
                content[static_i-5: static_i] == "src='" or \
                content[static_i-5: static_i] == "url('" or \
                content[static_i-6: static_i] == "href='":
            static_end_i = content.find("'", static_i)
        elif 4 <= static_i and \
                content[static_i-4: static_i] == 'url(':
            static_end_i = content.find(')', static_i)
        else:
            continue


c
        parsed = content[static_i: stati_end_i]

        if "?" in parsed:
            parsed = parsed[:parsed.find('?')]
        if "#" in parsed:
            parsed = parsed[:parsed.find('#')]

        if rel_static_indexs:
            sliced_content_url = content_url[content_url.find(
                '/static/'):content_url.rfind('/')]
            parsed = parsed.replace(
                "..", sliced_content_url[:sliced_content_url.rfind('/')])

        rp_resources.append(parsed)
    return rp_resources


def resrc_save(url, rs_resource_path):
    if os.path.isfile(PROJECT_PATH + rs_resource_path):
        if DO_UPDATE:
            url_req.urlretrieve(url, PROJECT_PATH + rs_resource_path)
            print("updated")
        else:
            print("exist")
    else:
        if os.path.isdir(PROJECT_PATH + rs_resource_path[:rs_resource_path.rfind('/')]):
            url_req.urlretrieve(url, PROJECT_PATH + rs_resource_path)
            print("saved")
        else:
            print("no directory")
            print("[-] Create Folder - " +
                  rs_resource_path[:rs_resource_path.rfind('/')], end=" ...")
            os.makedirs(PROJECT_PATH +
                        rs_resource_path[:rs_resource_path.rfind('/')])
            print("OK.")

            url_req.urlretrieve(url, PROJECT_PATH + rs_resource_path)
            print("saved")

    if RECURSIVE and (url[-4:] == ".css" or url[-3:] == ".js") and url not in TMP_ARRIVED:
        TARGETS.append(url)
        print(" [*] Append Target : " + url)


def err_logging(path, lg_stat_code):
    with open(LOG_PATH + "\\error_log.txt", 'a') as f:
        f.write("ERROR PATH: " + path + '\n')
        f.write("STATUS CODE: " + str(lg_stat_code) + '\n')
        f.write("" + '\n')
        f.write("url: " + URL + '\n')
        f.write("----------------------------------" + '\n')

    with open(LOG_PATH + "\\error_url_log.txt", 'a') as f:
        f.write(URL + path + '\n')


def arrived_logging(url):
    with open(LOG_PATH + "\\arrived.txt", 'a') as f:
        f.write(url + '\n')


def open_arrived():
    arrived = []
    try:
        with open(LOG_PATH + "\\arrived.txt", 'r') as f:
            arrived = f.read().split('\n')[:-1]
    except:
        print(LOG_PATH + "\\arrived.txt is Not Exist")
    return arrived


if __name__ == "__main__":
    if DO_UPDATE:
        TMP_ARRIVED = list(set(EXCLUDE_TARGETS[:]))
    else:
        TMP_ARRIVED = list(set(EXCLUDE_TARGETS[:] + open_arrived()))

    while TARGETS:
        target = TARGETS.pop()

        print("\n[*] URL Target : " + target)
        TMP_ARRIVED.append(target)
        arrived_logging(target)

        res = req.get(target, cookies=COOKIES, verify=False)

        resources = resrc_parse(res.text, target)
        for resource in resources:
            print("[+] " + target + " : " + resource)

        if not AUTO_YES:
            answer = input("Continue?(yes[enter]/no): ").lower()
            if answer == "q":
                exit()
            elif answer == "no":
                continue

        for resource_path in resources:
            print("[+] Resource Target : " + resource_path, end=" ..")
            stat_code = req.get(URL + resource_path, verify=False).status_code
            if stat_code != 200:
                print("error\n [-] Error Resource Target " + str(stat_code))
                err_logging(resource_path, stat_code)
            else:
                print(stat_code, end="..")
                resrc_save(URL + resource_path, resource_path)

    while RESOURCE_TARGETS:
        resource_path = RESOURCE_TARGETS.pop()
        print("\n[+] A Resource Target : " + resource_path, end=" ..")
        stat_code = req.get(URL + resource_path, verify=False).status_code
        if stat_code != 200:
            print("error\n [-] Error Resource Target " + str(stat_code))
            err_logging(resource_path, stat_code)
        else:
            print(stat_code, end="..")
            resrc_save(URL + resource_path, resource_path)
