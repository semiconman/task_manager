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

    def __init__(self, name, color=None, templates=None):
        """카테고리 초기화

        Args:
            name (str): 카테고리 이름
            color (str, optional): 카테고리 색상 (HEX 코드). 지정하지 않으면 기본 색상 사용
            templates (list, optional): 템플릿 목록. 기본값은 빈 리스트
        """
        self.name = name

        # 기본 색상이 있으면 사용, 없으면 회색 사용
        if color:
            self.color = color
        else:
            self.color = self.DEFAULT_COLORS.get(name, "#9E9E9E")  # 기본값은 회색

        # 템플릿 목록 초기화 (기본값은 빈 리스트)
        self.templates = templates if templates is not None else []

    def add_template(self, title, content=""):
        """템플릿 추가

        Args:
            title (str): 템플릿 제목
            content (str, optional): 템플릿 내용
        """
        template = {
            "title": title,
            "content": content
        }
        print(f"Category.add_template 호출: {template}")
        self.templates.append(template)
        print(f"템플릿 추가 후 총 개수: {len(self.templates)}")

    def remove_template(self, index):
        """템플릿 삭제

        Args:
            index (int): 삭제할 템플릿 인덱스

        Returns:
            bool: 삭제 성공 여부
        """
        print(f"Category.remove_template 호출: index={index}, 현재 템플릿 수={len(self.templates)}")
        if 0 <= index < len(self.templates):
            removed_template = self.templates[index]
            print(f"삭제할 템플릿: {removed_template}")
            del self.templates[index]
            print(f"삭제 후 템플릿 수: {len(self.templates)}")
            return True
        print("템플릿 삭제 실패: 잘못된 인덱스")
        return False

    def get_template(self, index):
        """템플릿 조회

        Args:
            index (int): 템플릿 인덱스

        Returns:
            dict: 템플릿 정보 (title, content) 또는 None
        """
        if 0 <= index < len(self.templates):
            return self.templates[index]
        return None

    def has_templates(self):
        """템플릿 존재 여부 확인

        Returns:
            bool: 템플릿이 있으면 True
        """
        return len(self.templates) > 0

    def to_dict(self):
        """Category 객체를 딕셔너리로 변환 (JSON 저장용)"""
        result = {
            "name": self.name,
            "color": self.color,
            "templates": getattr(self, 'templates', [])  # templates 필드 안전하게 가져오기
        }
        print(f"카테고리 '{self.name}' 저장 시 템플릿 수: {len(result['templates'])}")  # 디버그용
        return result

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Category 객체 생성

        Args:
            data (dict): 카테고리 데이터를 포함한 딕셔너리

        Returns:
            Category: 생성된 Category 객체
        """
        templates = data.get("templates", [])
        print(f"카테고리 '{data['name']}' 로드 시 템플릿 수: {len(templates)}")  # 디버그용

        return cls(
            name=data["name"],
            color=data.get("color"),
            templates=templates  # 템플릿 정보 로드 (기본값: 빈 리스트)
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