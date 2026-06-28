# 超星学习通图书馆座位预约（seatengine 版）

适配 `reserve.chaoxing.com` 新版座位预约系统，支持滑块验证码自动识别，通过 GitHub Actions 定时自动抢座。

## 部署方式

### GitHub Actions（推荐）

1. **Fork 本仓库** 或直接使用
2. **修改 `config.json`**，填入你的预约信息（账号密码留空或用占位符）
3. **配置 Secrets**：在 Settings → Secrets and variables → Actions 中添加：
   - `USERNAMES`：你的学号
   - `PASSWORDS`：你的密码
4. **手动触发一次** 激活定时任务（Actions → auto_Reserve → Run workflow）
5. cron 每天 **11:50** 自动启动，预计 **12:00** 准时抢座

### 本地部署

```bash
pip install cryptography requests numpy opencv-python
python main.py -m debug   # 测试配置
python main.py            # 正式运行
```

## 配置说明

```json
{
    "reserve": [
        {
            "username": "xxxxxxxxxx",
            "password": "xxxxxxxxx",
            "time": ["09:00","22:00"],
            "roomid": "11229",
            "seatid": ["175"],
            "daysofweek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        }
    ]
}
```

## 关键参数（main.py）

```python
SLEEPTIME = 0.2        # 抢座间隔（秒）
ENDTIME = "12:01:00"   # 截止时间（学校开放时间+1分钟）
ENABLE_SLIDER = True   # 滑块验证码
MAX_ATTEMPT = 10       # 最大重试次数
```

## License

MIT
