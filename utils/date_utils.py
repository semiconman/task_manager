#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, timedelta


def get_current_date_str():
    """현재 날짜를 문자열로 반환 (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")


def get_month_calendar(year, month):
    """특정 연도와 월의 달력 데이터 생성

    Args:
        year (int): 연도
        month (int): 월

    Returns:
        list: 주 단위로 구성된 날짜 리스트
    """
    cal = calendar.monthcalendar(year, month)
    return cal


def get_month_days(year, month):
    """특정 연도와 월의 전체 날짜 리스트 반환

    Args:
        year (int): 연도
        month (int): 월

    Returns:
        list: 해당 월의 모든 날짜 (YYYY-MM-DD 형식)
    """
    num_days = calendar.monthrange(year, month)[1]
    return [
        f"{year}-{month:02d}-{day:02d}"
        for day in range(1, num_days + 1)
    ]


def get_week_start_end(date_str):
    """주의 시작일과 종료일 계산

    Args:
        date_str (str): 기준 날짜 (YYYY-MM-DD)

    Returns:
        tuple: 주의 시작일과 종료일 (YYYY-MM-DD 형식)
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    # 월요일이 0, 일요일이 6
    weekday = date.weekday()

    # 이번 주 월요일 (주의 시작)
    start_date = date - timedelta(days=weekday)
    # 이번 주 일요일 (주의 끝)
    end_date = start_date + timedelta(days=6)

    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )


def get_month_start_end(date_str):
    """월의 시작일과 종료일 계산

    Args:
        date_str (str): 기준 날짜 (YYYY-MM-DD)

    Returns:
        tuple: 월의 시작일과 종료일 (YYYY-MM-DD 형식)
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    # 이번 달 첫날
    start_date = date.replace(day=1)

    # 이번 달 마지막 날
    if date.month == 12:
        next_month = date.replace(year=date.year + 1, month=1, day=1)
    else:
        next_month = date.replace(month=date.month + 1, day=1)

    end_date = next_month - timedelta(days=1)

    return (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )


def format_date_for_display(date_str):
    """날짜 문자열을 표시용 형식으로 변환

    Args:
        date_str (str): 날짜 문자열 (YYYY-MM-DD)

    Returns:
        str: 표시용 날짜 문자열 (YYYY년 MM월 DD일 요일)
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        weekday = weekday_kr[date.weekday()]
        return f"{date.year}년 {date.month}월 {date.day}일 {weekday}"
    except ValueError:
        return date_str