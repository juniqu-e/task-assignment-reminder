# Mattermost Reminder Bot

Mattermost Incoming Webhook을 이용한 **업무 분담 자동 알림 봇**입니다.

매일 평일 아침, 팀원별 담당 업무를 자동으로 로테이션하여 Mattermost 채널에 알림을 보냅니다.

## 주요 기능

- **매일 로테이션**: 평일 기준으로 매일 업무가 팀원 간 자동 교대
- **주간 로테이션**: 특정 요일에만 발생하는 업무를 주차별로 교대
- **특정 날짜 업무**: 지정된 날짜에 모든 팀원에게 공통 업무 배정
- **업무 링크 연동**: 각 업무에 Google Sheets 등 외부 링크 자동 첨부
- **인원 수 자유**: 2명 이상 원하는 만큼 팀원 추가 가능

## 메시지 예시

```
## 📋 2026-04-09 "1주차" 목요일 업무 분담 알리미

### 홍길동
- 일일보고서(4, 5)
- 공지사항 전달
- [베스트 멤버 선정](https://docs.google.com/spreadsheets/d/example1)

### 김철수
- 일일보고서(1, 2, 3)
- [출결 현황 체크](https://docs.google.com/spreadsheets/d/example3)
- [회의록 작성](https://docs.google.com/spreadsheets/d/example2)
```

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/mm-reminder.git
cd mm-reminder
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
| `webhook_url` | Mattermost Incoming Webhook URL | `https://your-server.com/hooks/xxx` |
| `start_date` | 로테이션 시작 기준일 (주차 계산 기준) | `"2026-04-06"` |
| `members` | 팀원 이름 목록 | `["홍길동", "김철수"]` |

### 매일 로테이션 업무 (`daily_rotation_tasks`)

평일마다 팀원 간 교대되는 업무입니다.

```json
"daily_rotation_tasks": {
    "member_0": ["업무 A", "업무 B"],
    "member_1": ["업무 C", "업무 D"]
}
```

- `member_0`, `member_1`, ... 은 역할 슬롯입니다 (특정 사람이 아님).
- 평일 기준으로 매일 로테이션되어, 오늘 `member_0`이 홍길동이면 내일은 김철수가 됩니다.
- 팀원이 3명 이상이면 `member_2`, `member_3`, ... 을 추가하면 됩니다.

### 주간 로테이션 업무 (`weekly_rotation_tasks`)

특정 요일에만 발생하며, 주차별로 로테이션되는 업무입니다.

```json
"weekly_rotation_tasks": {
    "thursday": {
        "member_0": ["베스트 멤버 선정"],
        "member_1": ["회의록 작성"]
    },
    "friday": {
        "member_0": ["주간 보고서"],
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
    "2026-04-17": ["월간 평가"],
    "2026-05-21": ["월간 평가"]
}
```

### 업무별 링크 (`task_links`)

업무 이름에 링크를 연결하면 메시지에서 클릭 가능한 링크로 표시됩니다.

```json
"task_links": {
    "베스트 멤버 선정": "https://docs.google.com/spreadsheets/d/...",
    "출결 현황 체크": "https://docs.google.com/spreadsheets/d/..."
}
```

- 키 값이 업무 이름과 **정확히 일치**해야 링크가 적용됩니다.

## 실행

### 수동 실행

```bash
python3 reminder.py
```

미리보기 메시지가 출력되고, Mattermost로 전송됩니다.

### cron으로 자동 실행 (권장)

매일 평일 오전 8시에 자동 실행하려면:

```bash
crontab -e
```

아래 내용을 추가합니다:

```
0 8 * * 1-5 /usr/bin/python3 /path/to/mm-reminder/reminder.py >> /path/to/mm-reminder/cron.log 2>&1
```

- `0 8 * * 1-5`: 월~금 08:00
- 경로는 본인 환경에 맞게 수정하세요.
- 실행 시간을 변경하려면 `0 8` 부분을 수정합니다 (예: `0 9`는 09:00).

## Mattermost Webhook 설정

1. Mattermost에서 알림을 받을 채널로 이동
2. **채널 헤더 > Integrations > Incoming Webhooks** 클릭
3. **Add Incoming Webhook** 클릭
4. 표시 이름, 설명, 채널을 설정 후 저장
5. 생성된 Webhook URL을 `config.json`의 `webhook_url`에 입력

## 로테이션 규칙 상세

### 매일 로테이션 (daily)

`start_date`부터 오늘까지의 **평일 수**를 세어 팀원 수로 나눈 나머지로 결정합니다.

```
로테이션 인덱스 = (start_date 이후 평일 수) % 팀원 수
```

예) 팀원 2명, 평일 3일차:
- 인덱스 = 3 % 2 = 1
- 홍길동 → `member_1` 업무, 김철수 → `member_0` 업무

### 주간 로테이션 (weekly)

`start_date` 기준 **주차 번호**로 결정합니다.

```
주차 = ((오늘 - start_date).days / 7) + 1
로테이션 인덱스 = (주차 - 1) % 팀원 수
```

## 라이선스

MIT License
