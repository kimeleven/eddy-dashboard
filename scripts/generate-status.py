#!/usr/bin/env python3
import json, os, re, subprocess
from datetime import datetime

HOME = os.path.expanduser("~")
AGENT = os.path.join(HOME, "eddy-agent")
OUT = os.path.join(AGENT, "eddy-dashboard", "public", "status.json")

def tail(path, n=10):
    try:
        with open(path) as f:
            lines = f.readlines()
        return [l.strip() for l in lines[-n:] if l.strip()]
    except:
        return []

def last_run(path):
    for line in reversed(tail(path, 30)):
        m = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
        if m:
            return m.group(1)
    return ""

def get_hour():
    return datetime.now().hour

hour = get_hour()
dg_status = "active" if hour >= 19 or hour < 7 else "scheduled"
lo_status = dg_status

cron_count = 0
try:
    r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    cron_count = len([l for l in r.stdout.splitlines() if l.strip() and not l.startswith("#")])
except:
    pass

# 최근 활동 수집
activity = []
for logfile in [
    "eddy/eddy.log",
    "devgate-team/dev1.log", "devgate-team/dev2.log",
    "liveorder-team/dev1.log",
    "reviewbot-team/dev1.log",
]:
    for line in tail(os.path.join(AGENT, logfile), 5):
        if any(k in line for k in ["[done]", "완료", "push 완료", "커밋"]):
            activity.append(line)
activity = activity[-15:]

data = {
    "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "system": {
        "host": "MacBook (a1111)",
        "services": ["Claude Max", "Gemini 2.5", "Imagen 4"],
        "cronJobs": cron_count,
        "telegram": "Eddy Bot (30분마다)"
    },
    "teams": [
        {
            "name": "Eddy",
            "icon": "🧠",
            "description": "Personal AI Agent",
            "schedule": "24h (30분마다)",
            "status": "active",
            "agents": [
                {"name": "Eddy", "role": "텔레그램 모니터링, PM 총괄", "cron": "0,30 * * * *", "lastRun": last_run(f"{AGENT}/eddy/eddy.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/eddy/eddy.log"))
        },
        {
            "name": "DevGate",
            "icon": "🏗️",
            "description": "외주 개발 플랫폼",
            "schedule": "19:00~07:00",
            "status": dg_status,
            "agents": [
                {"name": "Dev1", "role": "기능 개발", "cron": ":00 (19~07)", "lastRun": last_run(f"{AGENT}/devgate-team/dev1.log")},
                {"name": "Dev2", "role": "기능 개발", "cron": ":30 (19~07)", "lastRun": last_run(f"{AGENT}/devgate-team/dev2.log")},
                {"name": "Planner", "role": "기획/태스크 관리", "cron": "2h간격", "lastRun": last_run(f"{AGENT}/devgate-team/planner.log")},
                {"name": "QA", "role": "코드 검증", "cron": "3h간격", "lastRun": last_run(f"{AGENT}/devgate-team/qa.log")},
                {"name": "PM", "role": "텔레그램 보고", "cron": ":05 (19~07)", "lastRun": last_run(f"{AGENT}/devgate-team/pm.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/devgate-team/dev1.log"))
        },
        {
            "name": "LiveOrder",
            "icon": "🛒",
            "description": "라이브커머스 주문 플랫폼",
            "schedule": "19:00~07:00",
            "status": lo_status,
            "agents": [
                {"name": "Dev1", "role": "기능 개발", "cron": ":10 (19~07)", "lastRun": last_run(f"{AGENT}/liveorder-team/dev1.log")},
                {"name": "Planner", "role": "기획/태스크 관리", "cron": "2h간격", "lastRun": last_run(f"{AGENT}/liveorder-team/planner.log")},
                {"name": "QA", "role": "코드 검증", "cron": "3h간격", "lastRun": last_run(f"{AGENT}/liveorder-team/qa.log")},
                {"name": "PM", "role": "텔레그램 보고", "cron": ":15 (19~07)", "lastRun": last_run(f"{AGENT}/liveorder-team/pm.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/liveorder-team/dev1.log"))
        },
        {
            "name": "ReviewBot",
            "icon": "📝",
            "description": "사봤쪄 리뷰 블로그",
            "schedule": "하루 1회 (09:30~14:00)",
            "status": "scheduled",
            "agents": [
                {"name": "Planner", "role": "키워드 전략/SEO", "cron": "09:30", "lastRun": last_run(f"{AGENT}/reviewbot-team/planner.log")},
                {"name": "Dev1", "role": "파이프라인 실행", "cron": "10:00", "lastRun": last_run(f"{AGENT}/reviewbot-team/dev1.log")},
                {"name": "QA", "role": "리뷰 품질 평가", "cron": "12:00", "lastRun": last_run(f"{AGENT}/reviewbot-team/qa.log")},
                {"name": "PM", "role": "텔레그램 보고", "cron": "14:00", "lastRun": last_run(f"{AGENT}/reviewbot-team/pm.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/reviewbot-team/dev1.log"))
        }
    ],
    "recentActivity": activity
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[{data['updatedAt']}] status.json 업데이트 완료")
