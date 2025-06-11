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

        # ETC 카테고리 존재 확인
        self.ensure_etc_category()

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

                print(f"로드된 카테고리 데이터: {categories_data}")  # 디버그용

                categories = [Category.from_dict(cat_dict) for cat_dict in categories_data]

                # 기존 카테고리들에 templates 속성이 없으면 추가
                for category in categories:
                    if not hasattr(category, 'templates'):
                        category.templates = []
                        print(f"카테고리 '{category.name}'에 빈 templates 추가")

                print("카테고리 로드 완료:")
                for category in categories:
                    template_count = len(getattr(category, 'templates', []))
                    print(f"  카테고리 '{category.name}': 템플릿 {template_count}개")

                return categories
            except (json.JSONDecodeError, KeyError) as e:
                print(f"카테고리 데이터 로드 중 오류 발생: {e}")
                # 기본 카테고리 반환
                return Category.get_default_categories()
        # 파일이 없으면 기본 카테고리 반환
        print("카테고리 파일이 없어 기본 카테고리 생성")
        return Category.get_default_categories()

    def save_data(self):
        """변경된 데이터가 있는 경우 저장"""
        try:
            if self.tasks_changed:
                print("작업 데이터 저장 중...")
                self._save_tasks()
                self.tasks_changed = False
                print("작업 데이터 저장 완료")

            if self.categories_changed:
                print("카테고리 데이터 저장 중...")
                self._save_categories()
                self.categories_changed = False
                print("카테고리 데이터 저장 완료")
        except Exception as e:
            print(f"데이터 저장 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def _save_tasks(self):
        """작업 데이터 저장"""
        tasks_data = [task.to_dict() for task in self.tasks]
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)

    def _save_categories(self):
        """카테고리 데이터 저장"""
        try:
            print("카테고리 저장 시작:")
            for category in self.categories:
                template_count = len(getattr(category, 'templates', []))
                print(f"  카테고리 '{category.name}': 템플릿 {template_count}개")
                if template_count > 0:
                    print(f"    템플릿 목록: {[t.get('title', 'No Title') for t in category.templates]}")

            categories_data = []
            for cat in self.categories:
                cat_dict = cat.to_dict()
                categories_data.append(cat_dict)

            print(f"저장할 전체 카테고리 데이터:")
            for i, cat_data in enumerate(categories_data):
                print(f"  {i}: {cat_data}")

            # 디렉토리 존재 확인
            os.makedirs(self.data_dir, exist_ok=True)

            with open(self.categories_file, "w", encoding="utf-8") as f:
                json.dump(categories_data, f, ensure_ascii=False, indent=2)

            print(f"카테고리 데이터 파일 저장 완료: {self.categories_file}")

            # 저장 후 파일 검증
            if os.path.exists(self.categories_file):
                file_size = os.path.getsize(self.categories_file)
                print(f"저장된 파일 크기: {file_size} bytes")

                # 파일 내용 재확인
                with open(self.categories_file, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                print(f"저장 후 검증 - 카테고리 수: {len(saved_data)}")
                for cat_data in saved_data:
                    template_count = len(cat_data.get('templates', []))
                    print(f"  검증: '{cat_data['name']}' - 템플릿 {template_count}개")
            else:
                print("경고: 파일이 저장되지 않았습니다!")

        except Exception as e:
            print(f"카테고리 저장 중 오류: {e}")
            import traceback
            traceback.print_exc()

    def add_task(self, task):
        """작업 추가

        Args:
            task (Task): 추가할 작업 객체
        """
        # 해당 날짜의 마지막 순서 번호 계산
        date_tasks = [t for t in self.tasks if t.created_date == task.created_date]
        if hasattr(task, 'order') and task.order is not None:
            # order가 이미 설정되어 있으면 그대로 사용
            pass
        else:
            # 새 작업이면 마지막 순서로 설정
            max_order = max([getattr(t, 'order', 0) for t in date_tasks] + [0])
            task.order = max_order + 1

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
                deleted_task = self.tasks[i]
                del self.tasks[i]

                # 삭제된 작업 이후의 순서 재정렬
                self._reorder_tasks_after_deletion(deleted_task.created_date, getattr(deleted_task, 'order', 0))

                self.tasks_changed = True
                return True
        return False

    def _reorder_tasks_after_deletion(self, date_str, deleted_order):
        """작업 삭제 후 순서 재정렬"""
        date_tasks = [t for t in self.tasks if t.created_date == date_str]
        for task in date_tasks:
            if hasattr(task, 'order') and task.order > deleted_order:
                task.order -= 1

    def reorder_tasks(self, date_str, source_index, target_index):
        """특정 날짜의 작업 순서 변경

        Args:
            date_str (str): 날짜 (YYYY-MM-DD)
            source_index (int): 원본 인덱스
            target_index (int): 대상 인덱스

        Returns:
            bool: 성공 여부
        """
        try:
            # 해당 날짜의 작업들만 필터링 (중요한 다른 날짜 작업 제외)
            date_only_tasks = [t for t in self.tasks if t.created_date == date_str]

            if source_index < 0 or source_index >= len(date_only_tasks):
                print(f"잘못된 소스 인덱스: {source_index}, 작업 수: {len(date_only_tasks)}")
                return False
            if target_index < 0 or target_index >= len(date_only_tasks):
                print(f"잘못된 타겟 인덱스: {target_index}, 작업 수: {len(date_only_tasks)}")
                return False

            print(f"순서 변경 전 작업 순서:")
            for i, task in enumerate(date_only_tasks):
                print(f"  {i}: {task.title} (order: {getattr(task, 'order', 'None')})")

            # 실제 순서 변경 - 원본 tasks 리스트에서 직접 수행
            # 1. 이동할 작업과 대상 작업의 실제 인덱스 찾기
            source_task = date_only_tasks[source_index]
            target_task = date_only_tasks[target_index]

            # 2. 전체 tasks 리스트에서 실제 인덱스 찾기
            source_real_index = -1
            target_real_index = -1

            for i, task in enumerate(self.tasks):
                if task.id == source_task.id:
                    source_real_index = i
                if task.id == target_task.id:
                    target_real_index = i

            if source_real_index == -1 or target_real_index == -1:
                print(f"실제 인덱스를 찾을 수 없음: source={source_real_index}, target={target_real_index}")
                return False

            # 3. 실제 tasks 리스트에서 순서 변경
            moved_task = self.tasks.pop(source_real_index)

            # target_real_index 조정 (source가 target보다 앞에 있었다면)
            if source_real_index < target_real_index:
                target_real_index -= 1

            self.tasks.insert(target_real_index, moved_task)

            # 4. 해당 날짜의 모든 작업의 order 필드 재계산
            updated_date_tasks = [t for t in self.tasks if t.created_date == date_str]
            for i, task in enumerate(updated_date_tasks):
                task.order = i + 1

            print(f"순서 변경 후 작업 순서:")
            for i, task in enumerate(updated_date_tasks):
                print(f"  {i}: {task.title} (order: {getattr(task, 'order', 'None')})")

            self.tasks_changed = True
            print(f"작업 순서 변경 완료: {source_index} -> {target_index}")
            return True

        except Exception as e:
            print(f"작업 순서 변경 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_tasks_by_date(self, date_str):
        """특정 날짜의 작업 목록 조회 (순서대로 정렬)

        Args:
            date_str (str): 조회할 날짜 (YYYY-MM-DD)

        Returns:
            list: 해당 날짜에 생성된 작업 목록 + 다른 날짜의 중요 미완료 작업
        """
        # 해당 날짜의 작업
        date_tasks = [task for task in self.tasks if task.created_date == date_str]

        # order 필드가 없는 경우 추가
        for i, task in enumerate(date_tasks):
            if not hasattr(task, 'order') or task.order is None:
                task.order = i + 1

        # order 순으로 정렬 (order가 없으면 999로 처리하여 뒤로)
        date_tasks.sort(key=lambda x: getattr(x, 'order', 999))

        print(f"날짜 {date_str}의 작업 순서:")
        for i, task in enumerate(date_tasks):
            print(f"  위치 {i}: {task.title} (order: {getattr(task, 'order', 'None')})")

        # 다른 날짜의 중요 미완료 작업
        important_tasks = [
            task for task in self.tasks
            if task.created_date != date_str and task.important and not task.completed
        ]

        # 다른 날짜의 중요 작업에도 임시 order 할당 (음수로 구분)
        for i, task in enumerate(important_tasks):
            task.temp_order = -(i + 1)  # 음수로 설정하여 맨 앞에 표시

        # 중요 작업을 먼저, 그 다음 해당 날짜 작업 (order 순서 유지)
        return important_tasks + date_tasks

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
        # ETC 카테고리는 삭제 불가
        if category_name == "ETC":
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

    def reorder_categories(self, source_index, target_index):
        """카테고리 순서 변경

        Args:
            source_index (int): 원본 인덱스
            target_index (int): 대상 인덱스

        Returns:
            bool: 성공 여부
        """
        try:
            if source_index < 0 or source_index >= len(self.categories):
                print(f"잘못된 소스 인덱스: {source_index}, 카테고리 수: {len(self.categories)}")
                return False
            if target_index < 0 or target_index >= len(self.categories):
                print(f"잘못된 타겟 인덱스: {target_index}, 카테고리 수: {len(self.categories)}")
                return False
            if source_index == target_index:
                return True

            print(f"카테고리 순서 변경: {source_index} -> {target_index}")
            print(f"변경 전 순서:")
            for i, cat in enumerate(self.categories):
                print(f"  {i}: {cat.name}")

            # 카테고리 순서 변경
            moved_category = self.categories.pop(source_index)
            self.categories.insert(target_index, moved_category)

            print(f"변경 후 순서:")
            for i, cat in enumerate(self.categories):
                print(f"  {i}: {cat.name}")

            self.categories_changed = True
            return True

        except Exception as e:
            print(f"카테고리 순서 변경 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def ensure_etc_category(self):
        """ETC 카테고리가 존재하는지 확인하고 없으면 생성"""
        etc_exists = any(cat.name == "ETC" for cat in self.categories)
        if not etc_exists:
            from models.category import Category
            etc_category = Category("ETC", "#EA4335")
            self.categories.append(etc_category)
            self.categories_changed = True
            print("ETC 카테고리가 자동으로 생성되었습니다.")

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