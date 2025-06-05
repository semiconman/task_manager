#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Category:
    """카테고리 클래스: 작업 분류 표현"""

    # 기본 카테고리 색상 정의
    DEFAULT_COLORS = {
        "LB": "#4285F4",  # 파란색
        "Tester": "#FBBC05",  # 노란색
        "Handler": "#34A853",  # 녹색
        "ETC": "#EA4335"  # 빨간색
    }

    def __init__(self, name, color=None):
        """카테고리 초기화

        Args:
            name (str): 카테고리 이름
            color (str, optional): 카테고리 색상 (HEX 코드). 지정하지 않으면 기본 색상 사용
        """
        self.name = name

        # 기본 색상이 있으면 사용, 없으면 회색 사용
        if color:
            self.color = color
        else:
            self.color = self.DEFAULT_COLORS.get(name, "#9E9E9E")  # 기본값은 회색

    def to_dict(self):
        """Category 객체를 딕셔너리로 변환 (JSON 저장용)"""
        return {
            "name": self.name,
            "color": self.color
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Category 객체 생성

        Args:
            data (dict): 카테고리 데이터를 포함한 딕셔너리

        Returns:
            Category: 생성된 Category 객체
        """
        return cls(
            name=data["name"],
            color=data.get("color")
        )

    @classmethod
    def get_default_categories(cls):
        """기본 카테고리 목록 반환

        Returns:
            list: 기본 카테고리 객체 목록
        """
        return [
            cls("LB", cls.DEFAULT_COLORS["LB"]),
            cls("Tester", cls.DEFAULT_COLORS["Tester"]),
            cls("Handler", cls.DEFAULT_COLORS["Handler"]),
            cls("ETC", cls.DEFAULT_COLORS["ETC"])
        ]