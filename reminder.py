#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime
from pathlib import Path

# 현재 스크립트 경로 기준으로 config.json 로드
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.json"

WEEKDAY_KR = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

WEEKDAY_EN = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday"
}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_week_number(config, target_date=None):
    """시작일 기준으로 몇 주차인지 계산"""
    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    if target_date is None:
        target_date = datetime.now()
    diff_days = (target_date - start_date).days
    week_num = (diff_days // 7) + 1
    return week_num


def get_weekday_count(config, target_date=None):
    """시작일 기준으로 평일(월~금)이 몇 번째인지 계산 (로테이션용)"""
    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    if target_date is None:
        target_date = datetime.now()

    count = 0
    current = start_date
    while current < target_date:
        if current.weekday() < 5:  # 월~금
            count += 1
        current = current.replace(day=current.day + 1) if current.day < 28 else current + __import__('datetime').timedelta(days=1)

    return count


def get_business_day_count(config, target_date=None):
    """시작일 기준으로 평일 카운트 (더 정확한 버전)"""
    from datetime import timedelta
    start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
    if target_date is None:
        target_date = datetime.now()

    count = 0
    current = start_date
    while current <= target_date:
        if current.weekday() < 5:  # 월~금
            count += 1
        current += timedelta(days=1)

    return count - 1  # 0부터 시작하도록


def build_message(config):
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    weekday_num = today.weekday()
    weekday_kr = WEEKDAY_KR[weekday_num]
    weekday_en = WEEKDAY_EN[weekday_num]
    week_num = get_week_number(config)

    members = config["members"]
    num_members = len(members)

    # 매일 로테이션: 평일 카운트 기준
    daily_rotation_index = get_business_day_count(config) % num_members

    # 주간 로테이션: 주차 기준
    weekly_rotation_index = (week_num - 1) % num_members

    # 각 멤버별 업무 수집
    member_tasks = {member: [] for member in members}

    # 매일 로테이션 업무 배정
    daily_rotation_tasks = config.get("daily_rotation_tasks", {})
    for i, member in enumerate(members):
        # 로테이션에 따라 member_0 또는 member_1 업무 배정
        rotation_key = f"member_{(i + daily_rotation_index) % num_members}"
        tasks = daily_rotation_tasks.get(rotation_key, [])
        member_tasks[member].extend(tasks)

    # 주간 로테이션 업무 배정 (해당 요일에만)
    weekly_rotation_tasks = config.get("weekly_rotation_tasks", {}).get(weekday_en, {})
    if weekly_rotation_tasks:
        for i, member in enumerate(members):
            # 주간 로테이션에 따라 member_0 또는 member_1 업무 배정
            rotation_key = f"member_{(i + weekly_rotation_index) % num_members}"
            tasks = weekly_rotation_tasks.get(rotation_key, [])
            member_tasks[member].extend(tasks)

    # 특정 날짜 공통 업무 배정
    date_tasks = config.get("date_tasks", {}).get(date_str, [])
    if date_tasks:
        for member in members:
            member_tasks[member].extend(date_tasks)

    # 업무별 링크 매핑
    task_links = config.get("task_links", {})

    # 헤더
    lines = [f"## 📋 {date_str} \"{week_num}주차\" {weekday_kr} 업무 분담 알리미", ""]

    for member in members:
        lines.append(f"### {member}")
        tasks = member_tasks[member]
        if tasks:
            for task in tasks:
                if task in task_links:
                    lines.append(f"- [{task}]({task_links[task]})")
                else:
                    lines.append(f"- {task}")
        else:
            lines.append("- (오늘 배정된 업무 없음)")
        lines.append("")

    return "\n".join(lines)


def send_to_mattermost(webhook_url, message):
    payload = {"text": message}
    headers = {"Content-Type": "application/json; charset=utf-8"}

    response = requests.post(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers
    )

    if response.status_code == 200:
        print("메시지 전송 성공!")
    else:
        print(f"메시지 전송 실패: {response.status_code}")
        print(response.text)


def main():
    config = load_config()
    webhook_url = config["webhook_url"]

    if webhook_url == "여기에_웹훅_URL_입력":
        print("config.json에서 webhook_url을 설정해주세요.")
        return

    message = build_message(config)
    print("=== 전송할 메시지 미리보기 ===")
    print(message)
    print("==============================")

    send_to_mattermost(webhook_url, message)


if __name__ == "__main__":
    main()
