#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
from datetime import datetime


class Task:
    """작업 클래스: 할 일 항목 표현"""

    # 배경색 상수 정의
    BG_COLORS = {
        "none": "#FFFFFF",  # 흰색 (기본)
        "red": "#FFCDD2",  # 연한 빨강
        "orange": "#FFE0B2",  # 연한 주황
        "yellow": "#FFF9C4",  # 연한 노랑
        "green": "#C8E6C9",  # 연한 초록
        "blue": "#BBDEFB",  # 연한 파랑
        "purple": "#E1BEE7"  # 연한 보라
    }

    def __init__(self, title, content="", category="ETC", important=False, completed=False, created_date=None,
                 bg_color="none"):
        """작업 초기화

        Args:
            title (str): 작업 제목
            content (str, optional): 작업 내용. 기본값은 빈 문자열
            category (str, optional): 작업 카테고리. 기본값은 "ETC"
            important (bool, optional): 중요 여부. 기본값은 False
            completed (bool, optional): 완료 여부. 기본값은 False
            created_date (str, optional): 작업 생성 날짜(YYYY-MM-DD). 기본값은 현재 날짜
            bg_color (str, optional): 배경색 코드. 기본값은 "none" (흰색)
        """
        try:
            self.id = uuid.uuid4().hex  # 고유 ID
            self.title = title if title else "새 작업"  # 제목이 없으면 기본값 사용
            self.content = content if content else ""  # 내용이 None이면 빈 문자열로 설정
            self.category = category if category else "ETC"  # 카테고리가 None이면 기본값 사용
            self.created_date = created_date if created_date else datetime.now().strftime("%Y-%m-%d")  # 날짜 지정 가능
            self.important = bool(important)  # 중요 여부를 bool 타입으로 강제 변환
            self.completed = bool(completed)  # 완료 여부를 bool 타입으로 강제 변환
            self.bg_color = bg_color if bg_color in self.BG_COLORS else "none"  # 배경색 설정
        except Exception as e:
            print(f"작업 객체 생성 중 오류 발생: {e}")
            # 기본값으로 초기화
            self.id = uuid.uuid4().hex
            self.title = "새 작업"
            self.content = ""
            self.category = "ETC"
            self.created_date = datetime.now().strftime("%Y-%m-%d")
            self.important = False
            self.completed = False
            self.bg_color = "none"

    def to_dict(self):
        """Task 객체를 딕셔너리로 변환 (JSON 저장용)"""
        try:
            return {
                "id": self.id,
                "title": self.title,
                "content": self.content,
                "category": self.category,
                "created_date": self.created_date,
                "important": self.important,
                "completed": self.completed,
                "bg_color": self.bg_color
            }
        except Exception as e:
            print(f"작업 딕셔너리 변환 중 오류 발생: {e}")
            # 기본 딕셔너리 반환
            return {
                "id": self.id,
                "title": self.title,
                "content": "",
                "category": "ETC",
                "created_date": self.created_date,
                "important": False,
                "completed": False,
                "bg_color": "none"
            }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Task 객체 생성

        Args:
            data (dict): 작업 데이터를 포함한 딕셔너리

        Returns:
            Task: 생성된 Task 객체
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("데이터가 딕셔너리 형식이 아닙니다.")

            if "title" not in data:
                raise KeyError("필수 필드 'title'이 없습니다.")

            task = cls(
                title=data["title"],
                content=data.get("content", ""),
                category=data.get("category", "ETC"),
                important=data.get("important", False),
                completed=data.get("completed", False),
                created_date=data.get("created_date"),
                bg_color=data.get("bg_color", "none")
            )

            # ID 설정
            if "id" in data:
                task.id = data["id"]

            return task
        except Exception as e:
            print(f"딕셔너리에서 작업 객체 생성 중 오류 발생: {e}")
            # 기본 Task 객체 생성
            return cls("오류 발생 작업", content="데이터 로드 중 오류가 발생했습니다.")

    def get_bg_color_hex(self):
        """배경색의 16진수 코드 반환"""
        return self.BG_COLORS.get(self.bg_color, self.BG_COLORS["none"])