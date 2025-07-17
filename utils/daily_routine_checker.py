#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from utils.email_sender import EmailSender


class DailyRoutineChecker:
    """데일리 리포트 루틴 자동 실행 체크 (카테고리 필터 지원)"""

    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.routines_file = "data/daily_routines.json"
        self.last_check_file = "data/last_routine_check.json"

    def check_and_execute_routines(self):
        """루틴 체크 및 실행"""
        try:
            current_time = datetime.now()
            current_date = current_time.strftime("%Y-%m-%d")
            current_weekday = current_time.weekday()  # 0=월요일, 6=일요일
            current_hour_min = current_time.strftime("%H:%M")

            # 마지막 체크 시간 로드
            last_check = self.load_last_check()

            # 같은 날짜에 이미 실행된 루틴들 확인
            executed_today = last_check.get(current_date, [])

            # 루틴 목록 로드
            routines = self.load_routines()

            for routine in routines:
                if not routine.get("enabled", True):
                    continue

                routine_id = routine.get("id", "")
                if routine_id in executed_today:
                    continue  # 오늘 이미 실행됨

                # 시간 체크 (정확한 시간에만 실행)
                if routine.get("send_time", "00:00") != current_hour_min:
                    continue

                # 요일 체크
                weekday_map = {
                    0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
                    4: "friday", 5: "saturday", 6: "sunday"
                }
                current_weekday_name = weekday_map.get(current_weekday, "monday")

                if current_weekday_name not in routine.get("weekdays", []):
                    continue

                # 루틴 실행
                if self.execute_routine(routine, current_date):
                    # 실행 기록 저장
                    executed_today.append(routine_id)
                    last_check[current_date] = executed_today
                    self.save_last_check(last_check)

                    print(f"데일리 루틴 실행 완료: {routine.get('name', 'Unknown')}")

        except Exception as e:
            print(f"루틴 체크 중 오류: {e}")

    def execute_routine(self, routine, date_str):
        """개별 루틴 실행"""
        try:
            # 메일 발송 설정 생성
            settings = {
                "custom_title": routine.get("subject", "데일리 리포트"),
                "recipients": routine.get("recipients", []),
                "content_types": routine.get("content_types", ["all"]),
                "period": "오늘",
                "memo": routine.get("memo", ""),
                "selected_categories": routine.get("selected_categories")  # 카테고리 필터 추가
            }

            # 메일 발송 (데일리 리포트와 동일한 방식)
            return self.send_routine_report(routine, settings, date_str)

        except Exception as e:
            print(f"루틴 실행 중 오류: {e}")
            return False

    def send_routine_report(self, routine, settings, date_str):
        """루틴 리포트 메일 발송"""
        try:
            import win32com.client as win32

            # Outlook 연결
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            # 메일 제목
            subject = routine.get("subject", "데일리 리포트")
            mail.Subject = f"[루틴] {subject}"

            # 수신자
            recipients = routine.get("recipients", [])
            if not recipients:
                print("수신자가 없어 루틴 실행을 건너뜁니다.")
                return False

            mail.To = "; ".join(recipients)

            # 작업 데이터 수집 (카테고리 필터 적용)
            tasks_data = self.collect_tasks_data(date_str, routine.get("selected_categories"))

            # HTML 메일 내용 생성
            html_body = self.create_routine_html_report(routine, tasks_data, date_str)
            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            print(f"루틴 리포트 발송 완료: {routine.get('name', 'Unknown')}")
            return True

        except Exception as e:
            print(f"루틴 리포트 발송 중 오류: {e}")
            return False

    def collect_tasks_data(self, date_str, selected_categories=None):
        """지정된 날짜의 작업 데이터 수집 (카테고리 필터 적용)"""
        all_tasks = self.storage_manager.get_tasks_by_date(date_str)
        # 해당 날짜에 생성된 작업만 필터링
        date_tasks = [t for t in all_tasks if t.created_date == date_str]

        # 카테고리 필터 적용
        if selected_categories is not None:  # 특정 카테고리만 선택된 경우
            date_tasks = [t for t in date_tasks if t.category in selected_categories]
            print(f"루틴 카테고리 필터 적용: {selected_categories} -> {len(date_tasks)}개 작업")

        return {
            "all": date_tasks,
            "completed": [t for t in date_tasks if t.completed],
            "incomplete": [t for t in date_tasks if not t.completed],
            "total": len(date_tasks),
            "completed_count": len([t for t in date_tasks if t.completed]),
            "completion_rate": (
                        len([t for t in date_tasks if t.completed]) / len(date_tasks) * 100) if date_tasks else 0
        }

    def create_routine_html_report(self, routine, tasks_data, date_str):
        """루틴용 HTML 리포트 생성 (카테고리 필터 정보 포함)"""
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")

        # 루틴 정보
        routine_info = f'''
        <div style="background: #e8f4fd; padding: 15px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #17a2b8;">
            <strong>🔄 자동 루틴 리포트</strong>
            <div style="font-size: 12px; color: #0c5460; margin-top: 5px;">루틴명: {routine.get('name', 'Unknown')} | 자동 발송</div>
        </div>
        '''

        # 카테고리 필터 정보
        category_filter_info = ""
        selected_categories = routine.get("selected_categories")
        if selected_categories is not None:
            category_filter_info = f'''
            <div style="background: #d1ecf1; padding: 15px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #bee5eb;">
                <strong>📂 포함된 카테고리:</strong> {', '.join(selected_categories)}
                <div style="font-size: 12px; color: #0c5460; margin-top: 5px;">선택한 카테고리의 작업만 포함됩니다.</div>
            </div>
            '''

        # 통계 섹션
        stats_section = f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; color: white;">
            <h2 style="margin: 0 0 20px 0; font-size: 24px;">📊 {report_date} 업무 현황</h2>
            <div style="display: flex; gap: 25px; justify-content: space-around; margin: 20px 0;">
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; min-width: 80px;">
                    <div style="font-size: 28px; font-weight: bold;">{tasks_data['total']}</div>
                    <div style="font-size: 12px; opacity: 0.9;">전체 작업</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; min-width: 80px;">
                    <div style="font-size: 28px; font-weight: bold; color: #4CAF50;">{tasks_data['completed_count']}</div>
                    <div style="font-size: 12px; opacity: 0.9;">완료</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; min-width: 80px;">
                    <div style="font-size: 28px; font-weight: bold; color: #FF9800;">{tasks_data['total'] - tasks_data['completed_count']}</div>
                    <div style="font-size: 12px; opacity: 0.9;">미완료</div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-top: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span>완료율</span>
                    <span style="font-weight: bold; font-size: 18px;">{tasks_data['completion_rate']:.1f}%</span>
                </div>
                <div style="background: rgba(255,255,255,0.2); height: 12px; border-radius: 6px;">
                    <div style="background: #4CAF50; height: 12px; border-radius: 6px; width: {tasks_data['completion_rate']:.1f}%; transition: width 0.3s;"></div>
                </div>
            </div>
        </div>
        '''

        # 작업 목록 섹션들
        task_sections = ""
        content_types = routine.get("content_types", ["all"])

        if "all" in content_types and tasks_data['all']:
            task_sections += self.create_task_section("📋 전체 작업", tasks_data['all'], "#2196F3")

        if "completed" in content_types and tasks_data['completed']:
            task_sections += self.create_task_section("✅ 완료된 작업", tasks_data['completed'], "#4CAF50")

        if "incomplete" in content_types and tasks_data['incomplete']:
            task_sections += self.create_task_section("⏳ 미완료 작업", tasks_data['incomplete'], "#FF9800")

        # 추가 메모 섹션
        memo_section = ""
        memo = routine.get("memo", "").strip()
        if memo:
            memo_section = f'''
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #6c757d;">
                <h3 style="color: #495057; margin: 0 0 15px 0;">📝 추가 메모</h3>
                <div style="color: #6c757d; line-height: 1.6; white-space: pre-line;">{self.escape_html(memo)}</div>
            </div>
            '''

        # 전체 HTML
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f8f9fa; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 6px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 25px; text-align: center; }}
                .content {{ padding: 25px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #6c757d; font-size: 12px; border-top: 1px solid #dee2e6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">🔄 자동 데일리 리포트</h1>
                    <div style="margin-top: 10px; opacity: 0.9;">{current_time} 자동 발송</div>
                </div>
                <div class="content">
                    {routine_info}
                    {category_filter_info}
                    {stats_section}
                    {task_sections}
                    {memo_section}
                </div>
                <div class="footer">
                    🤖 Todolist PM 자동 루틴에서 발송 | {current_time}<br>
                    루틴: {routine.get('name', 'Unknown')} - {report_date}
                </div>
            </div>
        </body>
        </html>
        '''

        return html

    def create_task_section(self, title, tasks, color):
        """작업 섹션 HTML 생성"""
        if not tasks:
            return f'''
            <div style="margin-bottom: 25px;">
                <h3 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 8px; margin-bottom: 15px;">{title}</h3>
                <div style="text-align: center; color: #6c757d; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    해당하는 작업이 없습니다.
                </div>
            </div>
            '''

        task_items = ""
        for i, task in enumerate(tasks, 1):
            status_icon = "✅" if task.completed else "⏳"
            importance_icon = "⭐ " if task.important else ""

            # 완료된 작업 스타일
            task_style = ""
            if task.completed:
                task_style = "text-decoration: line-through; opacity: 0.7;"

            # 카테고리 색상 가져오기
            category_color = self.get_category_color(task.category)

            task_items += f'''
            <div style="background: #f8f9fa; margin: 8px 0; padding: 15px; border-radius: 8px; border-left: 4px solid {color};">
                <div style="display: flex; align-items: flex-start; gap: 10px;">
                    <span style="font-size: 16px;">{status_icon}</span>
                    <div style="flex: 1; {task_style}">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            {importance_icon}{self.escape_html(task.title)}
                            <span style="background: {category_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 10px; margin-left: 10px;">
                                {task.category}
                            </span>
                        </div>
                        {f'<div style="font-size: 12px; color: #6c757d; margin-top: 5px;">{self.escape_html(task.content[:100])}{"..." if len(task.content) > 100 else ""}</div>' if task.content else ''}
                    </div>
                </div>
            </div>
            '''

        return f'''
        <div style="margin-bottom: 25px;">
            <h3 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 8px; margin-bottom: 15px;">{title} ({len(tasks)}개)</h3>
            {task_items}
        </div>
        '''

    def get_category_color(self, category_name):
        """카테고리 색상 반환"""
        for category in self.storage_manager.categories:
            if category.name == category_name:
                return category.color
        return "#6c757d"  # 기본 색상

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

    def load_routines(self):
        """루틴 목록 로드"""
        try:
            if os.path.exists(self.routines_file):
                with open(self.routines_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"루틴 로드 중 오류: {e}")
        return []

    def load_last_check(self):
        """마지막 체크 시간 로드"""
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"마지막 체크 시간 로드 중 오류: {e}")
        return {}

    def save_last_check(self, data):
        """마지막 체크 시간 저장"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.last_check_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"마지막 체크 시간 저장 중 오류: {e}")