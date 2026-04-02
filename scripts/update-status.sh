#!/bin/bash
# 에이전트 상태 수집 → status.json 생성 → GitHub push → Vercel 자동 배포
DASHBOARD_DIR="$HOME/eddy-agent/eddy-dashboard"
STATUS_FILE="$DASHBOARD_DIR/public/status.json"
AGENT_DIR="$HOME/eddy-agent"

# 로그 마지막 10줄 가져오기
get_log() {
  local file="$1"
  if [ -f "$file" ]; then
    tail -10 "$file" 2>/dev/null | sed 's/"/\\"/g' | tr '\n' '|'
  else
    echo "No log yet"
  fi
}

# 마지막 실행 시간 가져오기
get_last_run() {
  local file="$1"
  if [ -f "$file" ]; then
    grep -o '\[20[0-9-]* [0-9:]*\]' "$file" | tail -1 | tr -d '[]'
  else
    echo ""
  fi
}

# 현재 시간
NOW=$(date '+%Y-%m-%d %H:%M:%S')
CRON_COUNT=$(crontab -l 2>/dev/null | grep -c '/')

# 로그 수집
EDDY_LOG=$(get_log "$AGENT_DIR/eddy/eddy.log")
EDDY_LAST=$(get_last_run "$AGENT_DIR/eddy/eddy.log")

DG_DEV1_LOG=$(get_log "$AGENT_DIR/devgate-team/dev1.log")
DG_DEV1_LAST=$(get_last_run "$AGENT_DIR/devgate-team/dev1.log")
DG_DEV2_LOG=$(get_log "$AGENT_DIR/devgate-team/dev2.log")
DG_DEV2_LAST=$(get_last_run "$AGENT_DIR/devgate-team/dev2.log")
DG_PLAN_LAST=$(get_last_run "$AGENT_DIR/devgate-team/planner.log")
DG_QA_LAST=$(get_last_run "$AGENT_DIR/devgate-team/qa.log")
DG_PM_LAST=$(get_last_run "$AGENT_DIR/devgate-team/pm.log")

LO_DEV1_LOG=$(get_log "$AGENT_DIR/liveorder-team/dev1.log")
LO_DEV1_LAST=$(get_last_run "$AGENT_DIR/liveorder-team/dev1.log")
LO_PLAN_LAST=$(get_last_run "$AGENT_DIR/liveorder-team/planner.log")
LO_QA_LAST=$(get_last_run "$AGENT_DIR/liveorder-team/qa.log")
LO_PM_LAST=$(get_last_run "$AGENT_DIR/liveorder-team/pm.log")

RB_DEV1_LOG=$(get_log "$AGENT_DIR/reviewbot-team/dev1.log")
RB_DEV1_LAST=$(get_last_run "$AGENT_DIR/reviewbot-team/dev1.log")
RB_PLAN_LAST=$(get_last_run "$AGENT_DIR/reviewbot-team/planner.log")
RB_QA_LAST=$(get_last_run "$AGENT_DIR/reviewbot-team/qa.log")
RB_PM_LAST=$(get_last_run "$AGENT_DIR/reviewbot-team/pm.log")

# 최근 활동 (전체 로그에서 최근 완료 항목)
RECENT=$(grep -h '\[done\]\|완료\|실행 완료\|push 완료' \
  "$AGENT_DIR"/eddy/eddy.log \
  "$AGENT_DIR"/devgate-team/*.log \
  "$AGENT_DIR"/liveorder-team/*.log \
  "$AGENT_DIR"/reviewbot-team/*.log 2>/dev/null | tail -15 | sed 's/"/\\"/g' | while read line; do echo "\"$line\","; done)
RECENT=$(echo "$RECENT" | sed '$ s/,$//')

# 현재 시간으로 활성 여부 판단
HOUR=$(date '+%H')
if [ "$HOUR" -ge 19 ] || [ "$HOUR" -lt 7 ]; then
  DG_STATUS="active"
  LO_STATUS="active"
else
  DG_STATUS="scheduled"
  LO_STATUS="scheduled"
fi

# status.json 생성
cat > "$STATUS_FILE" << ENDJSON
{
  "updatedAt": "$NOW",
  "system": {
    "host": "MacBook (a1111)",
    "services": ["Claude Max", "Gemini 2.5", "Imagen 4"],
    "cronJobs": $CRON_COUNT,
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
        {"name": "Eddy", "role": "텔레그램 모니터링, PM 총괄", "cron": "0,30 * * * *", "lastRun": "$EDDY_LAST"}
      ],
      "recentLog": "$(echo "$EDDY_LOG" | tr '|' '\n')"
    },
    {
      "name": "DevGate",
      "icon": "🏗️",
      "description": "외주 개발 플랫폼",
      "schedule": "19:00~07:00",
      "status": "$DG_STATUS",
      "agents": [
        {"name": "Dev1", "role": "기능 개발", "cron": ":00 (19~07)", "lastRun": "$DG_DEV1_LAST"},
        {"name": "Dev2", "role": "기능 개발", "cron": ":30 (19~07)", "lastRun": "$DG_DEV2_LAST"},
        {"name": "Planner", "role": "기획/태스크 관리", "cron": "2h간격", "lastRun": "$DG_PLAN_LAST"},
        {"name": "QA", "role": "코드 검증", "cron": "3h간격", "lastRun": "$DG_QA_LAST"},
        {"name": "PM", "role": "텔레그램 보고", "cron": ":05 (19~07)", "lastRun": "$DG_PM_LAST"}
      ],
      "recentLog": "$(echo "$DG_DEV1_LOG" | tr '|' '\n')"
    },
    {
      "name": "LiveOrder",
      "icon": "🛒",
      "description": "라이브커머스 주문 플랫폼",
      "schedule": "19:00~07:00",
      "status": "$LO_STATUS",
      "agents": [
        {"name": "Dev1", "role": "기능 개발", "cron": ":10 (19~07)", "lastRun": "$LO_DEV1_LAST"},
        {"name": "Planner", "role": "기획/태스크 관리", "cron": "2h간격", "lastRun": "$LO_PLAN_LAST"},
        {"name": "QA", "role": "코드 검증", "cron": "3h간격", "lastRun": "$LO_QA_LAST"},
        {"name": "PM", "role": "텔레그램 보고", "cron": ":15 (19~07)", "lastRun": "$LO_PM_LAST"}
      ],
      "recentLog": "$(echo "$LO_DEV1_LOG" | tr '|' '\n')"
    },
    {
      "name": "ReviewBot",
      "icon": "📝",
      "description": "사봤쪄 리뷰 블로그",
      "schedule": "하루 1회 (09:30~14:00)",
      "status": "scheduled",
      "agents": [
        {"name": "Planner", "role": "키워드 전략/SEO", "cron": "09:30", "lastRun": "$RB_PLAN_LAST"},
        {"name": "Dev1", "role": "파이프라인 실행", "cron": "10:00", "lastRun": "$RB_DEV1_LAST"},
        {"name": "QA", "role": "리뷰 품질 평가", "cron": "12:00", "lastRun": "$RB_QA_LAST"},
        {"name": "PM", "role": "텔레그램 보고", "cron": "14:00", "lastRun": "$RB_PM_LAST"}
      ],
      "recentLog": "$(echo "$RB_DEV1_LOG" | tr '|' '\n')"
    }
  ],
  "recentActivity": [
    $RECENT
  ]
}
ENDJSON

echo "[$NOW] status.json 업데이트 완료"

# GitHub push
cd "$DASHBOARD_DIR"
git add -A
git commit -m "status: $NOW" --allow-empty 2>/dev/null
git push origin main 2>/dev/null || git push origin master 2>/dev/null
