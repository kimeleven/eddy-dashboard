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

# launchd 에이전트 수 (cron 아님)
launchd_count = 0
try:
    r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    launchd_count = len([l for l in r.stdout.splitlines() if "com.eddy." in l])
except:
    pass

# 최근 활동 수집
activity = []
for logfile in [
    "eddy/eddy.log",
    "eldo-team/dev1.log", "eldo-team/dev2.log",
    "devgate-team/dev1.log", "devgate-team/dev2.log",
    "iri-safety-team/dev1.log", "iri-safety-team/dev2.log",
    "reviewbot-team/dev1.log",
]:
    for line in tail(os.path.join(AGENT, logfile), 5):
        if any(k in line for k in ["[done]", "완료", "push 완료", "커밋", "PASS", "FAIL"]):
            activity.append(line)
activity = activity[-15:]

data = {
    "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "system": {
        "host": "MacBook (a1111)",
        "scheduler": "launchd",
        "launchdAgents": launchd_count,
        "operatingHours": "월~금 19:00~07:00, 토일 24시간",
        "model": "Sonnet (전체)",
        "telegram": "Eddy PM만 보고"
    },
    "teams": [
        {
            "name": "Eddy",
            "icon": "🧠",
            "description": "유일한 PM — 전체 팀 관리 + Sanghun 보고",
            "schedule": "24시간 30분 (주중/주말 무관)",
            "status": "active",
            "agents": [
                {"name": "Eddy PM", "role": "텔레그램 모니터링, 전체 팀 검수/보고", "schedule": "24h 30분", "lastRun": last_run(f"{AGENT}/eddy/eddy.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/eddy/eddy.log"))
        },
        {
            "name": "ELDO",
            "icon": "📊",
            "description": "기업 재무분석 플랫폼",
            "schedule": "launchd 2시간",
            "status": "active",
            "agents": [
                {"name": "Dev1", "role": "백엔드/API/DB", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/eldo-team/dev1.log")},
                {"name": "Dev2", "role": "UI/UX/다크모드", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/eldo-team/dev2.log")},
                {"name": "Planner", "role": "기획/태스크 관리", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/eldo-team/planner.log")},
                {"name": "QA", "role": "E2E 테스트/코드 검증", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/eldo-team/qa.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/eldo-team/dev1.log"))
        },
        {
            "name": "DevGate",
            "icon": "🏗️",
            "description": "외주 개발 플랫폼 (기업 신뢰 기반)",
            "schedule": "launchd 24시간",
            "status": "active",
            "agents": [
                {"name": "Dev1", "role": "개발 + 버그 수정", "schedule": "24시간", "lastRun": last_run(f"{AGENT}/devgate-team/dev1.log")},
                {"name": "Dev2", "role": "E2E 테스트 확장", "schedule": "24시간", "lastRun": last_run(f"{AGENT}/devgate-team/dev2.log")},
                {"name": "QA", "role": "E2E 테스트 검증", "schedule": "24시간", "lastRun": last_run(f"{AGENT}/devgate-team/qa.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/devgate-team/dev1.log"))
        },
        {
            "name": "IRI-Safety",
            "icon": "⛑️",
            "description": "산업안전 컴플라이언스 SaaS",
            "schedule": "launchd 2시간",
            "status": "active",
            "agents": [
                {"name": "Planner", "role": "법안 검토/기능 기획", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/iri-safety-team/planner.log")},
                {"name": "Dev1", "role": "백엔드 개발", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/iri-safety-team/dev1.log")},
                {"name": "Dev2", "role": "프론트엔드 개발", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/iri-safety-team/dev2.log")},
                {"name": "QA", "role": "E2E 테스트", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/iri-safety-team/qa.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/iri-safety-team/dev1.log"))
        },
        {
            "name": "ReviewBot",
            "icon": "📝",
            "description": "사봤쪄 리뷰 블로그 (자동 포스팅 중단)",
            "schedule": "launchd 2시간 (Dev1만)",
            "status": "active",
            "agents": [
                {"name": "Dev1", "role": "쿠팡 검색 전환 개발", "schedule": "2시간", "lastRun": last_run(f"{AGENT}/reviewbot-team/dev1.log")},
                {"name": "Pipeline", "role": "자동 포스팅", "schedule": "중단", "lastRun": last_run(f"{AGENT}/reviewbot/data/logs/pipeline.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/reviewbot-team/dev1.log"))
        },
        {
            "name": "XBot",
            "icon": "🐦",
            "description": "X.com 자동화",
            "schedule": "중단",
            "status": "paused",
            "agents": [],
            "recentLog": "봇 감지 차단으로 중단 (2026-04-05~)"
        },
        {
            "name": "LiveOrder",
            "icon": "🛒",
            "description": "라이브커머스 주문 플랫폼",
            "schedule": "종료",
            "status": "paused",
            "agents": [],
            "recentLog": "개발 종료 (2026-04-03~)"
        }
    ],
    "weeklyReport": {
        "schedule": "매주 일요일 23:59",
        "format": "팀별 개별 PDF → 텔레그램 전송",
        "status": "active"
    },
    "recentActivity": activity
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[{data['updatedAt']}] status.json 업데이트 완료")
