import json, time, argparse, os, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
from utils import reserve, get_user_credentials

get_current_time = lambda action: time.strftime("%H:%M:%S", time.localtime(time.time() + (8*3600 if action else 0)))

SLEEPTIME = 0.2
ENDTIME = "12:01:00"
ENABLE_SLIDER = True
MAX_ATTEMPT = 10
RESERVE_NEXT_DAY = False

def login_and_reserve(users, usernames, passwords, action, success_list=None):
    if action and len(usernames.split(",")) != len(users): raise Exception("user count mismatch")
    if success_list is None: success_list = [False] * len(users)
    for index, user in enumerate(users):
        username, password, times, roomid, seatid, daysofweek = user.values()
        if action: username, password = usernames.split(",")[index], passwords.split(",")[index]
        if time.strftime("%A", time.localtime(time.time() + (8*3600 if action else 0))) not in daysofweek: continue
        if not success_list[index]:
            s = reserve(SLEEPTIME, MAX_ATTEMPT, ENABLE_SLIDER, RESERVE_NEXT_DAY)
            s.get_login_status(); s.login(username, password)
            s.requests.headers.update({"Host": "reserve.chaoxing.com"})
            success_list[index] = s.submit(times, roomid, seatid, action)
    return success_list

def main(users, action=False):
    t = get_current_time(action)
    logging.info(f"start {t} action={action}")
    usernames = passwords = None
    if action: usernames, passwords = get_user_credentials(action)
    success_list = None
    while t < ENDTIME:
        success_list = login_and_reserve(users, usernames, passwords, action, success_list)
        print(f"time={t} success={success_list}")
        t = get_current_time(action)
        if sum(success_list) == len(users): print("reserved successfully!"); return

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", default=config_path)
    parser.add_argument("-m", "--method", default="reserve", choices=["reserve", "debug", "room"])
    parser.add_argument("-a", "--action", action="store_true")
    args = parser.parse_args()
    with open(args.user) as f:
        usersdata = json.load(f)["reserve"]
    if args.action:
        us, pw = get_user_credentials(args.action)
        for i, u in enumerate(usersdata):
            u["username"] = us.split(",")[i]
            u["password"] = pw.split(",")[i]
    main(usersdata, args.action)
