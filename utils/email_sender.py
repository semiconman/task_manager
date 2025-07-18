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

            # HTML 내용 생성 (카테고리 필터 적용, 테이블 기반으로 수정)
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
        """간단한 HTML 메일 내용 생성 (테이블 기반, Outlook 호환성 개선)"""
        # 작업 데이터 수집 (카테고리 필터 적용)
        tasks_data = self.collect_tasks_data(settings)

        # 현재 시간
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

        # 카테고리 필터 정보
        selected_categories = settings.get("selected_categories")
        category_filter_info = ""

        print(f"EmailSender - 카테고리 필터: {selected_categories}")

        if selected_categories is not None and len(selected_categories) > 0:
            category_filter_info = f'''
            <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; margin-bottom: 20px;">
                <tr><td style="text-align: center;">
                    <strong>📂 포함된 카테고리:</strong> {', '.join(selected_categories)}
                </td></tr>
            </table>
            '''
        else:
            category_filter_info = f'''
            <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; margin-bottom: 20px;">
                <tr><td style="text-align: center;">
                    <strong>📂 포함된 카테고리:</strong> 모든 카테고리
                </td></tr>
            </table>
            '''

        # 테스트 메시지 (테이블 기반)
        test_message = ""
        if is_test:
            test_message = '''
            <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; margin-bottom: 20px;">
                <tr><td style="text-align: center; font-weight: bold;">🧪 테스트 메일입니다</td></tr>
            </table>
            '''

        # 통계 (테이블 기반)
        stats = tasks_data["stats"]

        # 작업 목록 섹션들 (테이블 기반)
        task_sections = ""
        content_types = settings.get("content_types", ["all"])
        tasks = tasks_data["tasks"]

        if "all" in content_types and tasks["all"]:
            task_sections += self.create_outlook_task_section("📌 전체 작업", tasks["all"][:5])
        if "completed" in content_types and tasks["completed"]:
            task_sections += self.create_outlook_task_section("✅ 완료된 작업", tasks["completed"][:5])
        if "incomplete" in content_types and tasks["incomplete"]:
            task_sections += self.create_outlook_task_section("⏳ 미완료 작업", tasks["incomplete"][:5])

        # Outlook 호환 HTML (테이블 기반 레이아웃)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Todolist 리포트</title>
            <!--[if mso]>
            <style type="text/css">
                table {{ border-collapse: collapse; }}
                .header-table {{ background-color: #4facfe !important; }}
            </style>
            <![endif]-->
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f5f5f5;">

            <!-- 메인 컨테이너 -->
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
                <tr>
                    <td align="center">

                        <!-- 메일 내용 테이블 -->
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">

                            <!-- 헤더 -->
                            <tr>
                                <td class="header-table" style="background-color: #4facfe; padding: 25px 20px; text-align: center;">
                                    <h1 style="margin: 0 0 10px 0; color: #ffffff; font-size: 24px; font-weight: bold;">
                                        📋 Todolist 리포트
                                    </h1>
                                    <div style="color: #ffffff; font-size: 16px; margin: 0;">
                                        {current_time}
                                    </div>
                                </td>
                            </tr>

                            <!-- 메인 컨텐츠 -->
                            <tr>
                                <td style="padding: 25px 20px;">

                                    {test_message}
                                    {category_filter_info}

                                    <!-- 오늘의 요약 -->
                                    <table width="100%" cellpadding="20" cellspacing="0" style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 10px; margin-bottom: 20px;">
                                        <tr>
                                            <td>
                                                <h2 style="color: #1976d2; margin-top: 0; margin-bottom: 15px; text-align: center;">📊 오늘의 요약</h2>

                                                <!-- 통계 테이블 -->
                                                <table width="100%" cellpadding="10" cellspacing="0">
                                                    <tr>
                                                        <td width="33%" style="text-align: center;">
                                                            <div style="font-size: 24px; font-weight: bold; color: #2196f3;">{stats['total']}</div>
                                                            <div style="font-size: 12px; color: #666;">전체 작업</div>
                                                        </td>
                                                        <td width="33%" style="text-align: center;">
                                                            <div style="font-size: 24px; font-weight: bold; color: #4caf50;">{stats['completed']}</div>
                                                            <div style="font-size: 12px; color: #666;">완료됨</div>
                                                        </td>
                                                        <td width="33%" style="text-align: center;">
                                                            <div style="font-size: 24px; font-weight: bold; color: #f44336;">{stats['incomplete']}</div>
                                                            <div style="font-size: 12px; color: #666;">미완료</div>
                                                        </td>
                                                    </tr>
                                                </table>

                                                <!-- 완료율 -->
                                                <table width="100%" cellpadding="10" cellspacing="0" style="background: #fff; border-radius: 5px; margin-top: 15px;">
                                                    <tr>
                                                        <td>
                                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                                <tr>
                                                                    <td style="font-weight: bold;">완료율</td>
                                                                    <td style="text-align: right; font-weight: bold; color: #4caf50;">
                                                                        {stats['completion_rate']:.0f}%
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 5px;">
                                                                <tr>
                                                                    <td style="background: #e0e0e0; height: 8px; border-radius: 4px;">
                                                                        <div style="background: #4caf50; height: 8px; border-radius: 4px; width: {stats['completion_rate']:.0f}%;"></div>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>

                                    {task_sections}

                                </td>
                            </tr>

                            <!-- 푸터 -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 15px 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #e9ecef;">
                                    🤖 Todolist PM에서 자동 생성 | {current_time}
                                </td>
                            </tr>

                        </table>

                    </td>
                </tr>
            </table>

        </body>
        </html>
        """

        return html

    def create_outlook_task_section(self, title, tasks):
        """Outlook 호환 작업 섹션 생성 (테이블 기반)"""
        if not tasks:
            return f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
                <tr>
                    <td style="padding: 10px 0 5px 0; border-bottom: 2px solid #e0e0e0;">
                        <h3 style="margin: 0; color: #333;">{title}</h3>
                    </td>
                </tr>
                <tr>
                    <td style="text-align: center; color: #666; padding: 20px;">작업이 없습니다</td>
                </tr>
            </table>
            """

        task_rows = ""
        for task in tasks:
            status = "✅" if task.completed else "⏳"
            text_style = "text-decoration: line-through; color: #666;" if task.completed else ""
            importance = "⭐" if task.important else ""
            border_color = "#4caf50" if task.completed else "#2196f3"

            task_rows += f"""
            <tr>
                <td style="padding: 10px; background-color: #f8f9fa; border-left: 3px solid {border_color}; border-radius: 5px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="{text_style}">
                                {status} {importance} <strong>{self.escape_html(task.title)}</strong>
                                <span style="background: {self.get_category_color(task.category)}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 10px;">{task.category}</span>
                            </td>
                        </tr>
                        {f'<tr><td style="font-size: 12px; color: #666; margin-top: 5px;">{self.escape_html(task.content[:50])}</td></tr>' if task.content else ''}
                    </table>
                </td>
            </tr>
            <tr><td style="height: 5px;"></td></tr>
            """

        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
            <tr>
                <td style="padding: 10px 0 5px 0; border-bottom: 2px solid #e0e0e0;">
                    <h3 style="margin: 0; color: #333;">{title}</h3>
                </td>
            </tr>
            <tr><td style="height: 10px;"></td></tr>
            {task_rows}
        </table>
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