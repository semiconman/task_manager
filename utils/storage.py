#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
from models.task import Task
from models.category import Category


class StorageManager:
    """데이터 저장 및 로드 관리 클래스"""

    def __init__(self, data_dir="data"):
        """스토리지 매니저 초기화

        Args:
            data_dir (str, optional): 데이터 저장 디렉토리. 기본값은 "data"
        """
        self.data_dir = data_dir
        self.tasks_file = os.path.join(data_dir, "tasks.json")
        self.categories_file = os.path.join(data_dir, "categories.json")

        # 데이터 로드
        self.tasks = self._load_tasks()
        self.categories = self._load_categories()

        # 변경 감지 플래그
        self.tasks_changed = False
        self.categories_changed = False

    def _load_tasks(self):
        """작업 데이터 로드"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                return [Task.from_dict(task_dict) for task_dict in tasks_data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"작업 데이터 로드 중 오류 발생: {e}")
                return []
        return []

    def _load_categories(self):
        """카테고리 데이터 로드"""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, "r", encoding="utf-8") as f:
                    categories_data = json.load(f)
                return [Category.from_dict(cat_dict) for cat_dict in categories_data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"카테고리 데이터 로드 중 오류 발생: {e}")
                # 기본 카테고리 반환
                return Category.get_default_categories()
        # 파일이 없으면 기본 카테고리 반환
        return Category.get_default_categories()

    def save_data(self):
        """변경된 데이터가 있는 경우 저장"""
        if self.tasks_changed:
            self._save_tasks()
            self.tasks_changed = False

        if self.categories_changed:
            self._save_categories()
            self.categories_changed = False

    def _save_tasks(self):
        """작업 데이터 저장"""
        tasks_data = [task.to_dict() for task in self.tasks]
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)

    def _save_categories(self):
        """카테고리 데이터 저장"""
        categories_data = [cat.to_dict() for cat in self.categories]
        with open(self.categories_file, "w", encoding="utf-8") as f:
            json.dump(categories_data, f, ensure_ascii=False, indent=2)

    def add_task(self, task):
        """작업 추가

        Args:
            task (Task): 추가할 작업 객체
        """
        self.tasks.append(task)
        self.tasks_changed = True

    def update_task(self, task_id, updated_task):
        """작업 업데이트

        Args:
            task_id (str): 업데이트할 작업의 ID
            updated_task (Task): 업데이트된 작업 객체

        Returns:
            bool: 업데이트 성공 여부
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks[i] = updated_task
                self.tasks_changed = True
                return True
        return False

    def delete_task(self, task_id):
        """작업 삭제

        Args:
            task_id (str): 삭제할 작업의 ID

        Returns:
            bool: 삭제 성공 여부
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self.tasks_changed = True
                return True
        return False

    def get_tasks_by_date(self, date_str):
        """특정 날짜의 작업 목록 조회

        Args:
            date_str (str): 조회할 날짜 (YYYY-MM-DD)

        Returns:
            list: 해당 날짜에 생성된 작업 목록 + 다른 날짜의 중요 미완료 작업
        """
        # 해당 날짜의 작업
        date_tasks = [task for task in self.tasks if task.created_date == date_str]

        # 다른 날짜의 중요 미완료 작업
        important_tasks = [
            task for task in self.tasks
            if task.created_date != date_str and task.important and not task.completed
        ]

        # 중요 작업을 먼저 정렬하고, 그 다음 일반 작업 정렬
        return sorted(date_tasks + important_tasks, key=lambda x: (not x.important, x.completed))

    def add_category(self, category):
        """카테고리 추가

        Args:
            category (Category): 추가할 카테고리 객체
        """
        self.categories.append(category)
        self.categories_changed = True

    def delete_category(self, category_name):
        """카테고리 삭제

        Args:
            category_name (str): 삭제할 카테고리 이름

        Returns:
            bool: 삭제 성공 여부
        """
        # 기본 카테고리는 삭제 불가
        default_names = ["LB", "Tester", "Handler", "ETC"]
        if category_name in default_names:
            return False

        for i, category in enumerate(self.categories):
            if category.name == category_name:
                # 해당 카테고리를 사용하는 작업들의 카테고리를 ETC로 변경
                for task in self.tasks:
                    if task.category == category_name:
                        task.category = "ETC"
                        self.tasks_changed = True

                del self.categories[i]
                self.categories_changed = True
                return True
        return False

    def get_task_stats(self, date_str):
        """특정 날짜의 작업 통계 조회

        Args:
            date_str (str): 조회할 날짜 (YYYY-MM-DD)

        Returns:
            dict: 작업 총 개수와 완료율을 포함한 통계
        """
        tasks = [task for task in self.tasks if task.created_date == date_str]
        total_count = len(tasks)

        if total_count == 0:
            return {"total": 0, "completed": 0, "completion_rate": 0}

        completed_count = sum(1 for task in tasks if task.completed)
        completion_rate = (completed_count / total_count) * 100

        return {
            "total": total_count,
            "completed": completed_count,
            "completion_rate": completion_rate
        }

    def export_to_csv(self, file_path, date_range=None, categories=None, completed=None, include_header=True,
                      fields=None):
        """작업 데이터를 CSV로 내보내기

        Args:
            file_path (str): 저장할 CSV 파일 경로
            date_range (tuple, optional): 시작일과 종료일 튜플 (YYYY-MM-DD)
            categories (list, optional): 포함할 카테고리 목록
            completed (bool, optional): 완료 상태 필터 (None: 모두, True: 완료, False: 미완료)
            include_header (bool, optional): 헤더 포함 여부
            fields (list, optional): 포함할 필드 목록

        Returns:
            bool: 내보내기 성공 여부
        """
        import csv

        # 기본 필드
        default_fields = ["id", "title", "content", "category", "created_date", "important", "completed"]

        # 필드 선택
        export_fields = fields if fields else default_fields

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # 헤더 작성
                if include_header:
                    writer.writerow(export_fields)

                # 필터링된 작업 목록
                filtered_tasks = self.tasks

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

                # 데이터 작성
                for task in filtered_tasks:
                    task_dict = task.to_dict()
                    row = [task_dict.get(field, "") for field in export_fields]
                    writer.writerow(row)

            return True

        except Exception as e:
            print(f"CSV 내보내기 중 오류 발생: {e}")
            return False