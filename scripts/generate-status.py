#!/usr/bin/env python3
import json, os, re, subprocess, plistlib
from datetime import datetime
from pathlib import Path

HOME = os.path.expanduser("~")
AGENT = os.path.join(HOME, "eddy-agent")
OUT = os.path.join(AGENT, "eddy-dashboard", "public", "status.json")
PLIST_DIR = os.path.join(HOME, "Library/LaunchAgents")

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

def read_secretary():
    """secretary.md를 파싱하여 섹션별로 반환"""
    path = os.path.join(AGENT, "eddy", "secretary.md")
    try:
        with open(path) as f:
            content = f.read()
        sections = {}
        current = None
        for line in content.split('\n'):
            if line.startswith('## 📌'):
                current = 'pinned'
                sections[current] = []
            elif line.startswith('## 📅'):
                current = 'schedule'
                sections[current] = []
            elif line.startswith('## 📝'):
                current = 'memo'
                sections[current] = []
            elif line.startswith('## ✅'):
                current = 'done'
                sections[current] = []
            elif line.startswith('## ') or line.startswith('# '):
                current = None
            elif current and line.strip() and not line.startswith('_') and not line.startswith('---'):
                sections.setdefault(current, []).append(line.strip())
        return {
            "pinned": sections.get('pinned', []),
            "schedule": sections.get('schedule', []),
            "memo": sections.get('memo', []),
            "done": sections.get('done', []),
            "raw": content
        }
    except:
        return {"pinned": [], "schedule": [], "memo": [], "done": [], "raw": ""}

def get_schedule(plist_name):
    """launchd plist에서 실제 주기를 읽어옴"""
    path = os.path.join(PLIST_DIR, plist_name)
    try:
        with open(path, 'rb') as f:
            pl = plistlib.load(f)
        interval = pl.get('StartInterval')
        if interval:
            if interval >= 86400: return f"{interval // 3600}시간"
            if interval >= 3600: return f"{interval // 3600}시간"
            return f"{interval // 60}분"
        cal = pl.get('StartCalendarInterval')
        if cal:
            wd = cal.get('Weekday')
            h = cal.get('Hour', 0)
            m = cal.get('Minute', 0)
            days = ['월','화','수','목','금','토','일']
            if wd is not None:
                return f"매주 {days[wd]}요일 {h:02d}:{m:02d}"
            return f"매일 {h:02d}:{m:02d}"
    except:
        pass
    return "알 수 없음"

# launchd 에이전트 수
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
    "biztool-team/planner.log", "biztool-team/dev1.log",
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
        "operatingHours": "Eddy: 24시간 / 팀: 월~금 19:00~07:00, 토일 24시간",
        "model": "Sonnet (전체)",
        "token": "바둑이토큰",
        "telegram": "Eddy PM만 보고"
    },
    "teams": [
        {
            "name": "Eddy",
            "icon": "🧠",
            "description": "유일한 PM — 전체 팀 관리 + Sanghun 보고",
            "schedule": get_schedule("com.eddy.agent.plist"),
            "status": "active",
            "agents": [
                {"name": "Eddy PM", "role": "텔레그램 모니터링, 전체 팀 검수/보고", "schedule": get_schedule("com.eddy.agent.plist"), "lastRun": last_run(f"{AGENT}/eddy/eddy.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/eddy/eddy.log"))
        },
        {
            "name": "ELDO",
            "icon": "📊",
            "description": "기업 재무분석 플랫폼",
            "schedule": get_schedule("com.eddy.eldo-dev1.plist"),
            "status": "active",
            "agents": [
                {"name": "Dev1", "role": "백엔드/API/DB", "schedule": get_schedule("com.eddy.eldo-dev1.plist"), "lastRun": last_run(f"{AGENT}/eldo-team/dev1.log")},
                {"name": "Dev2", "role": "UI/UX/다크모드", "schedule": get_schedule("com.eddy.eldo-dev2.plist"), "lastRun": last_run(f"{AGENT}/eldo-team/dev2.log")},
                {"name": "Planner", "role": "기획/태스크 관리", "schedule": get_schedule("com.eddy.eldo-planner.plist"), "lastRun": last_run(f"{AGENT}/eldo-team/planner.log")},
                {"name": "QA", "role": "E2E 테스트/코드 검증", "schedule": get_schedule("com.eddy.eldo-qa.plist"), "lastRun": last_run(f"{AGENT}/eldo-team/qa.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/eldo-team/dev1.log"))
        },
        {
            "name": "DevGate",
            "icon": "🏗️",
            "description": "외주 개발 플랫폼 (기업 신뢰 기반)",
            "schedule": get_schedule("com.eddy.devgate-dev1.plist"),
            "status": "active",
            "agents": [
                {"name": "Dev1", "role": "개발 + 버그 수정", "schedule": get_schedule("com.eddy.devgate-dev1.plist"), "lastRun": last_run(f"{AGENT}/devgate-team/dev1.log")},
                {"name": "Dev2", "role": "E2E 테스트 + UI", "schedule": get_schedule("com.eddy.devgate-dev2.plist"), "lastRun": last_run(f"{AGENT}/devgate-team/dev2.log")},
                {"name": "QA", "role": "E2E 테스트 검증", "schedule": get_schedule("com.eddy.devgate-qa.plist"), "lastRun": last_run(f"{AGENT}/devgate-team/qa.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/devgate-team/dev1.log"))
        },
        {
            "name": "IRI-Safety",
            "icon": "⛑️",
            "description": "산업안전 컴플라이언스 SaaS",
            "schedule": get_schedule("com.eddy.iri-dev1.plist"),
            "status": "active",
            "agents": [
                {"name": "Planner", "role": "법안 검토/기능 기획", "schedule": get_schedule("com.eddy.iri-planner.plist"), "lastRun": last_run(f"{AGENT}/iri-safety-team/planner.log")},
                {"name": "Dev1", "role": "백엔드 개발", "schedule": get_schedule("com.eddy.iri-dev1.plist"), "lastRun": last_run(f"{AGENT}/iri-safety-team/dev1.log")},
                {"name": "Dev2", "role": "프론트엔드 개발", "schedule": get_schedule("com.eddy.iri-dev2.plist"), "lastRun": last_run(f"{AGENT}/iri-safety-team/dev2.log")},
                {"name": "QA", "role": "E2E 테스트", "schedule": get_schedule("com.eddy.iri-qa.plist"), "lastRun": last_run(f"{AGENT}/iri-safety-team/qa.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/iri-safety-team/dev1.log"))
        },
        {
            "name": "BizTool",
            "icon": "💼",
            "description": "회계/HR 통합 관리 (프로덕션 운영 중)",
            "schedule": get_schedule("com.eddy.biztool-planner.plist") + " (push 금지)",
            "status": "active",
            "agents": [
                {"name": "Planner", "role": "TODO 발굴/API 조사", "schedule": get_schedule("com.eddy.biztool-planner.plist"), "lastRun": last_run(f"{AGENT}/biztool-team/planner.log")},
                {"name": "Dev1", "role": "승인된 TODO 개발", "schedule": get_schedule("com.eddy.biztool-dev1.plist"), "lastRun": last_run(f"{AGENT}/biztool-team/dev1.log")}
            ],
            "recentLog": "\n".join(tail(f"{AGENT}/biztool-team/planner.log"))
        },
        {
            "name": "ReviewBot",
            "icon": "📝",
            "description": "사봤쪄 리뷰 블로그 (자동 포스팅 중단)",
            "schedule": get_schedule("com.eddy.reviewbot-dev1.plist") + " (Dev1만)",
            "status": "active",
            "agents": [
                {"name": "Dev1", "role": "쿠팡 검색 전환 개발", "schedule": get_schedule("com.eddy.reviewbot-dev1.plist"), "lastRun": last_run(f"{AGENT}/reviewbot-team/dev1.log")},
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
    "secretary": read_secretary(),
    "weeklyReport": {
        "schedule": get_schedule("com.eddy.weekly-report.plist"),
        "format": "팀별 개별 PDF → 텔레그램 전송",
        "status": "active"
    },
    "recentActivity": activity
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[{data['updatedAt']}] status.json 업데이트 완료")
