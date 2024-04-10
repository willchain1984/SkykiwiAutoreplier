import pickle
import logging
import requests
import re
import os
from os import listdir

LOGIN_URL = "https://passport.skykiwi.com/v1/login/bbslogon.do"
LOGOUT_URL = "https://passport.skykiwi.com/v1/login/logout.do"
HOST_NAME = "bbs.skykiwi.com"

logging.basicConfig(
    level=logging.INFO,
    filename="info.log",
    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d %(levelname)s %(message)s",
)


class Login:
    def __init__(
        self,
        loginurl,
        hostname,
        username,
        password,
        questionid="0",
        answer=None,
        cookies_flag=True,
        timeout=5,
    ):
        self.session = requests.session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
            }
        )
        self.hostname = hostname
        self.loginurl = loginurl
        self.username = str(username)
        self.password = str(password)
        self.questionid = questionid
        self.answer = answer
        self.cookies_flag = cookies_flag
        self.timeout = timeout

    def form_hash(self):
        rst = self.session.get(
            f"https://{self.hostname}/member.php?mod=logging&action=login"
        ).text
        loginhash = re.search(r'<div id="main_messaqge_(.+?)">', rst).group(1)
        formhash = re.search(
            r'<input type="hidden" name="formhash" value="(.+?)" />', rst
        ).group(1)
        logging.info(f"loginhash : {loginhash} , formhash : {formhash} ")
        return loginhash, formhash

    def verify_code_once(self):
        rst = self.session.get(
            f"https://{self.hostname}/misc.php?mod=seccode&action=update&idhash=cSA&0.3701502461393815&modid=member::logging"
        ).text
        update = re.search(r"update=(.+?)&idhash=", rst).group(1)

        code_headers = {
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "hostname": f"{self.hostname}",
            "Referer": f"https://{self.hostname}/member.php?mod=logging&action=login",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        }
        rst = self.session.get(
            f"https://{self.hostname}/misc.php?mod=seccode&update={update}&idhash=cSA",
            headers=code_headers,
        )
        return rst.content

    def verify_code(self, num=10):
        while num > 0:
            num -= 1
            code = self.verify_code_once()
            verify_url = f"https://{self.hostname}/misc.php?mod=seccode&action=check&inajax=1&modid=member::logging&idhash=cSA&secverify={code}"
            res = self.session.get(verify_url).text
            if "succeed" in res:
                logging.info("Verification code has been recognised as:" + code)
                return code
            else:
                logging.info("Failed to recognise the verification code，try again...")
        logging.error(
            "Failed to obtain the verification code, please increase the re-try time or check if the function works normally."
        )
        return ""

    def account_login_without_verify(self):
        login_url = self.loginurl
        formData = {
            "referer": f"https://{self.hostname}/",
            "username": self.username,
            "password": self.password,
            "verifycode": "1111",
        }
        try:
            login_rst = self.session.post(
                login_url, data=formData, timeout=self.timeout
            ).text
        except Exception:
            logging.info("Login failed，network timeout.")
            return -1
        if (
            "\\u7528\\u6237\\u540d\\u6216\\u8005\\u767b\\u5f55\\u5bc6\\u7801\\u9519\\u8bef\\u3002"
            not in login_rst
        ):
            logging.info("Login successed.")
            return True
        else:
            logging.info("Login failed，please check your username and password.")
            return False

    def account_login(self):
        return self.account_login_without_verify()

    def cookies_login(self):
        cookies_name = "COOKIES-" + self.username
        if cookies_name in listdir():
            try:
                with open(cookies_name, "rb") as f:
                    self.session = pickle.load(f)
                response = self.session.get(
                    f"http://{self.hostname}/home.php?mod=space"
                ).text
                if "我的空间" not in response:
                    logging.info(
                        "Restore login from saved cookies，skipping the authentication."
                    )
                    return False
            except Exception:
                logging.warning(
                    "Invalid saved cookies，try to log in with provided username and password."
                )
            return True
        else:
            logging.info(
                "First login without detecting saved cookies，try to do with provided username and password."
            )
        return False

    def go_home(self):
        return self.session.get(f"http://{self.hostname}/forum.php").text

    def get_conis(self):
        try:
            res = self.session.get(
                f"https://{self.hostname}/home.php?mod=spacecp&ac=credit&showcredit=1&inajax=1&ajaxtarget=extcreditmenu_menu"
            ).text
            coins = re.search(r'<span id="hcredit_4">(.+?)</span>', res).group(1)
            logging.info(f"Current Popularity：{coins}")
        except Exception:
            logging.error("Failed to get the popularity value.", exc_info=True)

    def main(self):
        try:
            if self.cookies_flag and self.cookies_login():
                logging.info("Login successed with saved cookies")
            else:
                ret = self.account_login()
                if not ret:
                    return ret

            res = self.go_home()
            self.post_formhash = re.search(
                r'<input type="hidden" name="formhash" value="(.+?)" />', res
            ).group(1)
            credit = re.search(r'class="showmenu">(.+?)</a>', res).group(1)
            logging.info(
                f"{credit},the formhash for post submission is:{self.post_formhash}"
            )
            # self.get_conis()

            cookies_name = "COOKIES-" + self.username
            with open(cookies_name, "wb") as f:
                pickle.dump(self.session, f)
                logging.info("New cookie has been saved.")
            return True
        except Exception:
            logging.error("An error occured during the login.", exc_info=True)
            return -2

    def logout(self):
        try:
            self.session.get(LOGOUT_URL, timeout=self.timeout)
            cookies_name = "COOKIES-" + self.username
            if cookies_name in listdir():
                try:
                    os.remove(cookies_name)
                except Exception:
                    logging.warning("Failed to delete the cookies when logout.")
        except Exception:
            logging.warning("Logout failed，network timeout.")
            return False
        return True

# if __name__ == "__main__":
#     login = Login(LOGIN_URL, HOST_NAME, "14022339@qq.com", "will545884")
