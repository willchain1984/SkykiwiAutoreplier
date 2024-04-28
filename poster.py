import login
import logging
import re
from time import time
from random import randint
from urllib.parse import urlparse, urlsplit, parse_qsl
from bs4 import BeautifulSoup
import requests
import sys

HTTP_TIMEOUT = 5

logging.basicConfig(
    level=logging.INFO,
    filename="info.log",
    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d %(levelname)s %(message)s",
)


class Discuz:
    def __init__(
        self,
        loginurl,
        hostname,
        username,
        password,
        questionid="0",
        answer=None,
        cookies_flag=True,
        pub_url="",
    ):
        self.hostname = hostname
        if pub_url != "":
            self.hostname = self.get_host(pub_url)
        self.discuz_login = login.Login(
            loginurl,
            hostname,
            username,
            password,
            questionid,
            answer,
            cookies_flag,
            HTTP_TIMEOUT,
        )

    def login(self):
        ret = self.discuz_login.main()
        if ret == True:
            self.session = self.discuz_login.session
            self.formhash = self.discuz_login.post_formhash
            return True
        else:
            return ret

    def logout(self):
        return self.discuz_login.logout()

    def get_host(self, pub_url):
        res = requests.get(pub_url)
        res.encoding = "utf-8"
        url = re.search(r'a href="http://(.+?)/".+?>.+?入口</a>', res.text)
        if url is not None:
            url = url.group(1)
            logging.info(f"The latest publish url has been retrieved as: http://{url}")
            return url
        else:
            logging.error(
                f"Failed to retrieve，please check the provided publish url.{pub_url}"
            )
            return self.hostname

    def go_home(self):
        return self.session.get(f"http://{self.hostname}/forum.php").text

    def get_reply_tid_list(self):
        tids, replys = [], []
        soup = BeautifulSoup(self.go_home(), features="html.parser")
        reply = soup.select_one("#portal_block_136_content")
        replys.append(reply)

        for reply in replys:
            for a in reply.find_all("a"):
                if "机器人" in str(a) or "测试" in str(a) or "封号" in str(a):
                    continue
                dt = dict(parse_qsl(urlsplit(a["href"]).query))
                if "tid" in dt:
                    tids.append(f"{dt['tid']} | {a.string}")
        return tids

    def get_myreply_tid_list(self):
        tids = []
        soup = BeautifulSoup(
            self.session.get(
                f"http://{self.hostname}/home.php?mod=space&do=thread&view=me&type=reply"
            ).text,
            features="html.parser",
        )
        replys = soup.select("tr.bw0_all th")

        for reply in replys:
            for a in reply.find_all("a"):
                if "机器人" in str(a) or "测试" in str(a) or "封号" in str(a):
                    continue
                dt = dict(parse_qsl(urlsplit(a["href"]).query))
                if "ptid" in dt:
                    tids.append(f"{dt['ptid']} | {a.string}")
        return tids

    def get_reply_tid(self):
        tids = self.get_reply_tid_list()
        if len(tids) > 0:
            return tids[randint(0, len(tids) - 1)]
        else:
            logging.error("Failed to retried a tid，exit.")
            sys.exit()

    def get_title_by_tid(self, tid):
        soup = BeautifulSoup(
            self.session.get(
                f"http://{self.hostname}/forum.php?mod=viewthread&tid={tid}"
            ).text,
            features="html.parser",
        )
        title = soup.select_one("a#thread_subject")
        if hasattr(title, "string"):
            return title.string
        else:
            return False

    def reply(self, tid, message=""):
        reply_list = [
            "膜拜神贴，后面的请保持队形~",
            "啥也不说了，楼主就是给力！",
            "果断MARK，前十有我必火！",
            "看了LZ的帖子，我只想说一句很好很强大！",
            "不错，又占了一个沙发！",
            "哥顶的不是帖子，是寂寞！",
            "果断回帖，如果沉了就是我弄沉的很有成就感",
            "找了很久，终于找到了~",
            "这个真的很好很不错，我很喜欢~",
            "我回帖不是为了赞同，只是为了让楼主的帖子看起来不那么孤单.",
            "别人在帖子里找到答案，我在帖子里找到了存在感。",
            "我回帖就像小黄鸭，虽然不起眼，但总能给帖子增添一些乐趣。",
        ]

        msg = reply_list[randint(0, len(reply_list) - 1)] if message == "" else message
        reply_url = f"http://{self.hostname}/forum.php?mod=post&action=reply&tid={tid}&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1"
        data = {
            "file": "",
            "message": msg.encode("utf-8"),
            "posttime": int(time()),
            "formhash": self.formhash,
            "usesig": 1,
            "subject": "",
        }
        try:
            res = self.session.post(reply_url, data=data, timeout=HTTP_TIMEOUT).text
        except Exception:
            logging.error("Reply failed，network error.")
            return False
        if "succeed" in res:
            url = re.search(r"succeedhandle_fastpost\(\'(.+?)\',", res).group(1)
            logging.info(
                f'Reply successed，tid:{tid}，content:{msg}, URL:{"http://" + self.hostname + "/" + url}'
            )
            return True
        else:
            logging.error("Reply failed due to an exception.\t" + res)
            return False
