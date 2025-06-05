#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from datetime import datetime


class CsvExporter:
    """CSV 내보내기 기능 클래스"""

    @staticmethod
    def export_tasks(tasks, file_path, include_header=True, fields=None):
        """작업 목록을 CSV 파일로 내보내기

        Args:
            tasks (list): 작업 객체 목록
            file_path (str): CSV 파일 저장 경로
            include_header (bool, optional): 헤더 포함 여부. 기본값은 True
            fields (list, optional): 포함할 필드 목록. 기본값은 모든 필드

        Returns:
            bool: 내보내기 성공 여부
        """
        # 기본 필드 설정
        available_fields = {
            "id": "ID",
            "title": "제목",
            "content": "내용",
            "category": "카테고리",
            "created_date": "생성일",
            "important": "중요",
            "completed": "완료"
        }

        # 사용할 필드 결정
        if fields is None:
            export_fields = list(available_fields.keys())
        else:
            export_fields = [f for f in fields if f in available_fields]

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)

                # 헤더 작성
                if include_header:
                    header = [available_fields[field] for field in export_fields]
                    writer.writerow(header)

                # 데이터 작성
                for task in tasks:
                    task_dict = task.to_dict()

                    # Boolean 값 변환
                    if "important" in export_fields:
                        task_dict["important"] = "예" if task_dict["important"] else "아니오"
                    if "completed" in export_fields:
                        task_dict["completed"] = "예" if task_dict["completed"] else "아니오"

                    row = [task_dict.get(field, "") for field in export_fields]
                    writer.writerow(row)

            return True

        except Exception as e:
            print(f"CSV 내보내기 중 오류 발생: {e}")
            return False

    @staticmethod
    def filter_tasks(tasks, date_range=None, categories=None, completed=None):
        """작업 목록 필터링

        Args:
            tasks (list): 작업 객체 목록
            date_range (tuple, optional): 시작일과 종료일 튜플 (YYYY-MM-DD)
            categories (list, optional): 포함할 카테고리 목록
            completed (bool, optional): 완료 상태 필터 (None: 모두, True: 완료, False: 미완료)

        Returns:
            list: 필터링된 작업 목록
        """
        filtered_tasks = tasks

        # 날짜 범위 필터링
        if date_range:
            start_date, end_date = date_range
            filtered_tasks = [
                task for task in filtered_tasks
                if start_date <= task.created_date <= end_date
            ]

        # 카테고리 필터링
        if categories:
            filtered_tasks = [
                task for task in filtered_tasks
                if task.category in categories
            ]

        # 완료 상태 필터링
        if completed is not None:
            filtered_tasks = [
                task for task in filtered_tasks
                if task.completed == completed
            ]

        return filtered_tasks