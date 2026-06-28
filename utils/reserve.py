from utils import AES_Encrypt, generate_captcha_key, verify_param_seatengine
import json, requests, re, time, logging, datetime, random
from urllib3.exceptions import InsecureRequestWarning


class reserve:
    def __init__(self, sleep_time=0.2, max_attempt=10, enable_slider=True, reserve_next_day=False):
        self.login_page = "https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true&fid="
        self.url_tpl = "https://reserve.chaoxing.com/front/apps/seatengine/select?id={}&day={}&backLevel=2&seatId=3727"
        self.submit_url = "https://reserve.chaoxing.com/data/apps/seatengine/submit"
        self.login_url = "https://passport2.chaoxing.com/fanyalogin"
        self.requests = requests.session()
        self.captcha_headers = {"Referer": "https://reserve.chaoxing.com/", "Host": "captcha.chaoxing.com"}
        self.submit_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Host": "reserve.chaoxing.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        }
        self.login_headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "passport2.chaoxing.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1",
        }
        self.sleep_time = sleep_time
        self.max_attempt = max_attempt
        self.enable_slider = enable_slider
        self.reserve_next_day = reserve_next_day
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _get_submit_enc(self, roomid, day):
        resp = self.requests.get(url=self.url_tpl.format(roomid, day), verify=False)
        m = re.findall(r'id="submit_enc"\s+value="([^"]*)"', resp.content.decode("utf-8"))
        return m[0] if m else ""

    def get_login_status(self):
        self.requests.headers = self.login_headers
        self.requests.get(url=self.login_page, verify=False)

    def login(self, username, password):
        uname = AES_Encrypt(username)
        pwd = AES_Encrypt(password)
        parm = {"fid": -1, "uname": uname, "password": pwd,
                "refer": "http%3A%2F%2Freserve.chaoxing.com%2Ffront%2Fapps%2Fseatengine%2Fselect%3Fid%3D11229%26backLevel%3D2%26seatId%3D3727", "t": True}
        obj = self.requests.post(url=self.login_url, params=parm, verify=False).json()
        if obj.get("status"):
            logging.info("Login OK")
            return (True, "")
        logging.info(f"Login FAILED")
        return (False, "")

    def _solve_captcha(self):
        captcha_token, bg, tp = self._get_slide_captcha_data()
        x = self.x_distance(bg, tp) + random.randint(-2, 2)
        cb = f"jQuery{random.randint(100000000, 999999999)}_{int(time.time() * 1000)}"
        resp = self.requests.get("https://captcha.chaoxing.com/captcha/check/verification/result",
            params={"callback": cb, "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1", "type": "slide",
                    "token": captcha_token, "textClickArr": json.dumps([{"x": x}]), "coordinate": json.dumps([]),
                    "runEnv": "10", "version": "1.1.18", "_": int(time.time() * 1000)},
            headers=self.captcha_headers)
        try:
            return json.loads(json.loads(resp.text.replace(cb + "(", "").replace(")", ""))["extraData"])["validate"]
        except: return ""

    def _get_slide_captcha_data(self):
        ts = int(time.time() * 1000)
        capture_key, token = generate_captcha_key(ts)
        cb = f"jQuery{random.randint(100000000, 999999999)}_{ts}"
        resp = self.requests.get("https://captcha.chaoxing.com/captcha/get/verification/image",
            params={"callback": cb, "captchaId": "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1", "type": "slide",
                    "version": "1.1.18", "captchaKey": capture_key, "token": token,
                    "referer": "https://reserve.chaoxing.com/front/apps/seatengine/select?id=11229&backLevel=2&seatId=3727",
                    "_": ts, "d": "a", "b": "a"}, headers=self.captcha_headers)
        data = json.loads(resp.text.replace(cb + "(", "").replace(")", ""))
        return data["token"], data["imageVerificationVo"]["shadeImage"], data["imageVerificationVo"]["cutoutImage"]

    def x_distance(self, bg, tp):
        import numpy as np, cv2
        def cut(s):
            a = np.frombuffer(s, np.uint8); img = cv2.imdecode(a, cv2.IMREAD_UNCHANGED)
            m = img[:,:,3]; m[m!=0]=255; x,y,w,h = cv2.boundingRect(m)
            return img[y:y+h,x:x+w,:3]
        ch = {"Referer":"https://reserve.chaoxing.com/","Host":"captcha-b.chaoxing.com"}
        bg2 = cv2.imdecode(np.frombuffer(self.requests.get(bg,headers=ch).content,np.uint8),cv2.IMREAD_COLOR)
        tp2 = cut(self.requests.get(tp,headers=ch).content)
        return cv2.minMaxLoc(cv2.matchTemplate(cv2.cvtColor(cv2.Canny(bg2,100,200),cv2.COLOR_GRAY2RGB),
                                                cv2.cvtColor(cv2.Canny(tp2,100,200),cv2.COLOR_GRAY2RGB),
                                                cv2.TM_CCOEFF_NORMED))[3][0]

    def submit(self, times, roomid, seatid, action):
        delta = 1 if self.reserve_next_day else 0
        day = datetime.date.today() + datetime.timedelta(days=delta)
        if action: day = datetime.date.today() + datetime.timedelta(days=1 + delta)
        day_str = str(day)

        for seat in seatid:
            suc = False
            while ~suc and self.max_attempt > 0:
                captcha = ""
                if self.enable_slider:
                    captcha = self._solve_captcha()
                    if not captcha: time.sleep(0.3); self.max_attempt -= 1; continue

                submit_enc = self._get_submit_enc(roomid, day_str)
                if not submit_enc: time.sleep(self.sleep_time); self.max_attempt -= 1; continue

                params = {"roomId": roomid, "startTime": times[0], "endTime": times[1],
                          "day": day_str, "seatNum": seat, "captcha": captcha,
                          "wyToken": "", "wfwEngineEnc": ""}
                params["enc"] = verify_param_seatengine(params, submit_enc)

                headers = dict(self.submit_headers)
                headers["Referer"] = self.url_tpl.format(roomid, day_str)

                result = json.loads(self.requests.post(self.submit_url, data=params,
                    headers=headers, verify=False).content.decode("utf-8"))
                logging.info(f"{result}")
                if result.get("success", False): return True
                time.sleep(self.sleep_time)
                self.max_attempt -= 1
        return False
