#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from utils.date_utils import get_week_start_end, get_month_start_end

# pywin32 의존성 확인
try:
    import win32com.client as win32

    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False
    print("경고: pywin32가 설치되지 않았습니다. 메일 기능을 사용할 수 없습니다.")


class EmailSender:
    """Outlook을 통한 메일 발송 클래스 (카테고리 필터 지원)"""

    def __init__(self, storage_manager):
        self.storage_manager = storage_manager

    def check_availability(self):
        """메일 기능 사용 가능 여부 확인"""
        if not OUTLOOK_AVAILABLE:
            return False, "pywin32 라이브러리가 설치되지 않았습니다.\n\n설치 방법:\n1. 명령 프롬프트를 관리자 권한으로 실행\n2. 'pip install pywin32' 입력\n3. 프로그램 재시작"

        try:
            outlook = win32.Dispatch('outlook.application')
            return True, ""
        except Exception as e:
            return False, f"Outlook 연결에 실패했습니다:\n{str(e)}\n\nOutlook이 설치되어 있고 로그인되어 있는지 확인하세요."

    def send_scheduled_email(self, settings, is_test=False):
        """설정에 따른 메일 발송 (카테고리 필터 지원)"""
        available, error_msg = self.check_availability()
        if not available:
            print(f"메일 발송 불가: {error_msg}")
            return False

        try:
            # Outlook 연결
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            # 제목 설정
            today = datetime.now().strftime("%Y-%m-%d")
            custom_title = settings.get("custom_title", "")
            subject = f"{today} Todolist"
            if custom_title:
                subject += f" {custom_title}"
            if is_test:
                subject = "[테스트] " + subject

            mail.Subject = subject

            # 수신자 설정
            recipients = settings.get("recipients", [])
            if recipients:
                mail.To = "; ".join(recipients)

            # HTML 내용 생성 (카테고리 필터 적용)
            html_body = self.create_simple_html(settings, is_test)
            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            print(f"메일 발송 완료: {subject}")
            return True

        except Exception as e:
            print(f"메일 발송 중 오류 발생: {e}")
            return False

    def create_simple_html(self, settings, is_test=False):
        """간단한 HTML 메일 내용 생성 (카테고리 필터 지원)"""
        # 작업 데이터 수집 (카테고리 필터 적용)
        tasks_data = self.collect_tasks_data(settings)

        # 현재 시간
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

        # 카테고리 필터 정보 - 수정된 로직
        selected_categories = settings.get("selected_categories")
        category_filter_info = ""

        print(f"EmailSender - 카테고리 필터: {selected_categories}")  # 디버그

        if selected_categories is not None and len(selected_categories) > 0:
            # 특정 카테고리가 선택된 경우
            category_filter_info = f'''
            <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #17a2b8;">
                <strong>📂 포함된 카테고리:</strong> {', '.join(selected_categories)}
            </div>
            '''
        else:
            # 모든 카테고리가 선택된 경우 (None이거나 빈 리스트)
            category_filter_info = f'''
            <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #28a745;">
                <strong>📂 포함된 카테고리:</strong> 모든 카테고리
            </div>
            '''

        # 테스트 메시지
        test_message = ""
        if is_test:
            test_message = '<div style="background: #fff3cd; padding: 10px; margin-bottom: 20px; border-radius: 5px;"><strong>🧪 테스트 메일입니다</strong></div>'

        # 통계
        stats = tasks_data["stats"]

        # 간단한 요약
        summary = f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: #1976d2; margin-top: 0;">📊 오늘의 요약</h2>
            <div style="display: flex; gap: 20px; justify-content: space-around; margin: 15px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #2196f3;">{stats['total']}</div>
                    <div style="font-size: 12px; color: #666;">전체 작업</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #4caf50;">{stats['completed']}</div>
                    <div style="font-size: 12px; color: #666;">완료됨</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #f44336;">{stats['incomplete']}</div>
                    <div style="font-size: 12px; color: #666;">미완료</div>
                </div>
            </div>
            <div style="background: #fff; padding: 10px; border-radius: 5px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>완료율</span>
                    <span style="font-weight: bold; color: #4caf50;">{stats['completion_rate']:.0f}%</span>
                </div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 5px;">
                    <div style="background: #4caf50; height: 8px; border-radius: 4px; width: {stats['completion_rate']:.0f}%;"></div>
                </div>
            </div>
        </div>
        """

        # 작업 목록 (간단하게)
        task_lists = ""
        content_types = settings.get("content_types", ["all"])
        tasks = tasks_data["tasks"]

        if "all" in content_types and tasks["all"]:
            task_lists += self.create_task_section("📌 전체 작업", tasks["all"][:5])
        if "completed" in content_types and tasks["completed"]:
            task_lists += self.create_task_section("✅ 완료된 작업", tasks["completed"][:5])
        if "incomplete" in content_types and tasks["incomplete"]:
            task_lists += self.create_task_section("⏳ 미완료 작업", tasks["incomplete"][:5])

        # 전체 HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;"> Todolist 리포트</h1>
                    <div>{current_time}</div>
                </div>
                <div class="content">
                    {test_message}
                    {category_filter_info}
                    {summary}
                    {task_lists}
                </div>
                <div class="footer">
                    🤖 Todolist PM에서 자동 생성 | {current_time}
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def create_task_section(self, title, tasks):
        """작업 섹션 생성"""
        if not tasks:
            return f"""
            <div style="margin-bottom: 20px;">
                <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">{title}</h3>
                <div style="text-align: center; color: #666; padding: 20px;">작업이 없습니다</div>
            </div>
            """

        task_items = ""
        for task in tasks:
            status = "✅" if task.completed else "⏳"
            style = "text-decoration: line-through; color: #666;" if task.completed else ""
            importance = "⭐" if task.important else ""

            # 카테고리 색상 가져오기
            category_color = self.get_category_color(task.category)

            task_items += f"""
            <div style="background: #f8f9fa; margin: 5px 0; padding: 10px; border-radius: 5px; border-left: 3px solid {'#4caf50' if task.completed else '#2196f3'};">
                <div style="{style}">
                    {status} {importance} <strong>{self.escape_html(task.title)}</strong>
                    <span style="background: {category_color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 10px;">{task.category}</span>
                </div>
                {f'<div style="font-size: 12px; color: #666; margin-top: 5px;">{self.escape_html(task.content[:50])}</div>' if task.content else ''}
            </div>
            """

        return f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">{title}</h3>
            {task_items}
        </div>
        """

    def get_category_color(self, category_name):
        """카테고리 색상 반환"""
        for category in self.storage_manager.categories:
            if category.name == category_name:
                return category.color
        return "#6c757d"  # 기본 색상

    def collect_tasks_data(self, settings):
        """설정에 따른 작업 데이터 수집 (카테고리 필터 지원)"""
        period = settings.get("period", "오늘")

        # 오늘 작업만 간단하게 가져오기
        today = datetime.now().strftime("%Y-%m-%d")
        daily_tasks = self.storage_manager.get_tasks_by_date(today)

        # 1단계: 해당 날짜에 생성된 작업만 먼저 필터링
        all_tasks = [t for t in daily_tasks if t.created_date == today]
        print(f"EmailSender - 1단계 날짜별 필터링: {today}에 생성된 작업 {len(all_tasks)}개")

        # 2단계: 카테고리 필터 적용
        selected_categories = settings.get("selected_categories")
        if selected_categories is not None and len(selected_categories) > 0:  # 특정 카테고리만 선택된 경우
            filtered_tasks = [t for t in all_tasks if t.category in selected_categories]
            print(f"EmailSender - 2단계 카테고리 필터링: {selected_categories} 카테고리로 필터링 -> {len(filtered_tasks)}개 작업")
        else:
            filtered_tasks = all_tasks
            print(f"EmailSender - 2단계 카테고리 필터링: 모든 카테고리 포함 -> {len(filtered_tasks)}개 작업")

        # 통계 계산
        total = len(filtered_tasks)
        completed = len([t for t in filtered_tasks if t.completed])
        incomplete = total - completed
        completion_rate = (completed / total * 100) if total > 0 else 0

        return {
            "period": period,
            "tasks": {
                "all": filtered_tasks,
                "completed": [t for t in filtered_tasks if t.completed],
                "incomplete": [t for t in filtered_tasks if not t.completed]
            },
            "stats": {
                "total": total,
                "completed": completed,
                "incomplete": incomplete,
                "completion_rate": completion_rate
            }
        }

    def escape_html(self, text):
        """HTML 특수문자 이스케이프"""
        if not text:
            return ""

        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#39;",
            ">": "&gt;",
            "<": "&lt;",
        }

        return "".join(html_escape_table.get(c, c) for c in text)