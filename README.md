# Task Assignment Reminder Bot

Mattermost / Slack Incoming Webhook을 이용한 **업무 분담 자동 알림 봇**입니다.

매일 평일 아침, 팀원별 담당 업무를 자동으로 로테이션하여 채널에 알림을 보냅니다.

## 주요 기능

- **Mattermost & Slack 지원**: `platform` 설정 하나로 전환
- **매일 로테이션**: 평일 기준으로 매일 업무가 팀원 간 자동 교대
- **주간 로테이션**: 특정 요일에만 발생하는 업무를 주차별로 교대
- **특정 날짜 업무**: 지정된 날짜에 모든 팀원에게 공통 업무 배정
- **업무 링크 연동**: 각 업무에 Google Sheets 등 외부 링크 자동 첨부
- **인원 수 자유**: 2명 이상 원하는 만큼 팀원 추가 가능

## 메시지 예시

```
📋 2026-04-09 "1주차" 목요일 업무 분담 알리미

Alice
- Team announcements
- Meeting schedule sharing
- [MVP nomination](https://docs.google.com/spreadsheets/d/example2)

Bob
- Daily standup notes
- [Attendance check](https://docs.google.com/spreadsheets/d/example3)
- [Meeting minutes](https://docs.google.com/spreadsheets/d/example1)
```

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/task-assignment-reminder.git
cd task-assignment-reminder
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 설정 파일 생성

```bash
cp config.example.json config.json
```

`config.json`을 열어 본인 환경에 맞게 수정합니다.

## 설정 (`config.json`)

### 기본 설정

| 필드 | 설명 | 예시 |
|------|------|------|
| `platform` | 메신저 플랫폼 (`mattermost` 또는 `slack`) | `"mattermost"` |
| `webhook_url` | Incoming Webhook URL | `"https://your-server.com/hooks/xxx"` |
| `start_date` | 로테이션 시작 기준일 (주차 계산 기준) | `"2026-04-06"` |
| `members` | 팀원 이름 목록 | `["Alice", "Bob"]` |

### 매일 로테이션 업무 (`daily_rotation_tasks`)

평일마다 팀원 간 교대되는 업무입니다.

```json
"daily_rotation_tasks": {
    "member_0": ["Daily standup notes", "Attendance check"],
    "member_1": ["Team announcements", "Meeting schedule sharing"]
}
```

- `member_0`, `member_1`, ... 은 **역할 슬롯**입니다 (특정 사람이 아님).
- 평일 기준으로 매일 로테이션되어, 오늘 `member_0`이 Alice이면 내일은 Bob이 됩니다.
- 팀원이 3명 이상이면 `member_2`, `member_3`, ... 을 추가하면 됩니다.

### 주간 로테이션 업무 (`weekly_rotation_tasks`)

특정 요일에만 발생하며, 주차별로 로테이션되는 업무입니다.

```json
"weekly_rotation_tasks": {
    "thursday": {
        "member_0": ["MVP nomination"],
        "member_1": ["Meeting minutes", "Team mood check"]
    },
    "friday": {
        "member_0": ["Weekly report"],
        "member_1": []
    }
}
```

- 요일 키: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`
- 주차가 바뀔 때마다 `member_0`과 `member_1`에 배정되는 사람이 교대됩니다.
- 해당 요일이 아니면 무시됩니다.

### 특정 날짜 업무 (`date_tasks`)

지정된 날짜에 **모든 팀원**에게 공통으로 배정되는 업무입니다.

```json
"date_tasks": {
    "2026-04-17": ["Monthly review"],
    "2026-05-21": ["Monthly review"]
}
```

### 업무별 링크 (`task_links`)

업무 이름에 링크를 연결하면 메시지에서 클릭 가능한 링크로 표시됩니다.

```json
"task_links": {
    "Weekly report": "https://docs.google.com/spreadsheets/d/...",
    "Attendance check": "https://docs.google.com/spreadsheets/d/..."
}
```

- 키 값이 업무 이름과 **정확히 일치**해야 링크가 적용됩니다.

## 실행

### 수동 실행

```bash
python3 reminder.py
```

미리보기 메시지가 출력되고, 설정된 플랫폼으로 전송됩니다.

### cron으로 자동 실행 (권장)

매일 평일 오전 8시에 자동 실행하려면:

```bash
crontab -e
```

아래 내용을 추가합니다:

```
0 8 * * 1-5 /usr/bin/python3 /path/to/reminder.py >> /path/to/cron.log 2>&1
```

- `0 8 * * 1-5`: 월~금 08:00
- 경로는 본인 환경에 맞게 수정하세요.

## Webhook 설정 가이드

### Mattermost

1. 알림을 받을 채널로 이동
2. **채널 헤더 > Integrations > Incoming Webhooks** 클릭
3. **Add Incoming Webhook** 클릭
4. 표시 이름, 설명, 채널을 설정 후 저장
5. 생성된 Webhook URL을 `config.json`의 `webhook_url`에 입력
6. `platform`을 `"mattermost"`로 설정

### Slack

1. [Slack API](https://api.slack.com/apps) 에서 **Create New App > From scratch** 클릭
2. App 이름과 워크스페이스를 선택 후 생성
3. 좌측 메뉴에서 **Incoming Webhooks** 클릭 > **Activate** 토글 On
4. **Add New Webhook to Workspace** 클릭 > 채널 선택 후 허용
5. 생성된 Webhook URL을 `config.json`의 `webhook_url`에 입력
6. `platform`을 `"slack"`으로 설정

## 로테이션 규칙

### 매일 로테이션

`start_date`부터 오늘까지의 **평일 수**를 세어 팀원 수로 나눈 나머지로 결정합니다.

```
로테이션 인덱스 = (start_date 이후 평일 수) % 팀원 수
```

### 주간 로테이션

`start_date` 기준 **주차 번호**로 결정합니다.

```
주차 = ((오늘 - start_date) / 7) + 1
로테이션 인덱스 = (주차 - 1) % 팀원 수
```

## 라이선스

MIT License
