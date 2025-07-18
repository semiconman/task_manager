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

            # HTML 메일 내용 생성 (테이블 기반으로 수정)
            html_body = self.create_routine_html_report(routine, tasks_data, date_str)
            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            # 발송 이력 업데이트
            self.update_routine_send_history(routine["id"])

            print(f"루틴 리포트 발송 완료: {routine.get('name', 'Unknown')}")
            return True

        except Exception as e:
            print(f"루틴 리포트 발송 중 오류: {e}")
            return False

    def update_routine_send_history(self, routine_id):
        """루틴 발송 이력 업데이트"""
        try:
            current_time = datetime.now()
            current_date = current_time.strftime("%Y-%m-%d")
            current_time_str = current_time.strftime("%H:%M")

            # 루틴 파일 로드
            routines = self.load_routines()

            # 해당 루틴 찾아서 이력 업데이트
            for routine in routines:
                if routine.get("id") == routine_id:
                    routine["last_sent_date"] = current_date
                    routine["last_sent_time"] = current_time_str
                    routine["total_sent_count"] = routine.get("total_sent_count", 0) + 1
                    print(
                        f"루틴 '{routine.get('name')}' 발송 이력 업데이트: {current_date} {current_time_str} (총 {routine['total_sent_count']}회)")
                    break

            # 업데이트된 루틴 저장
            self.save_routines(routines)

        except Exception as e:
            print(f"루틴 발송 이력 업데이트 중 오류: {e}")

    def save_routines(self, routines):
        """루틴 목록 저장"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.routines_file, "w", encoding="utf-8") as f:
                json.dump(routines, f, ensure_ascii=False, indent=2)
            print("루틴 데이터 저장 완료")
        except Exception as e:
            print(f"루틴 저장 중 오류: {e}")

    def collect_tasks_data(self, date_str, selected_categories=None):
        """지정된 날짜의 작업 데이터 수집 (카테고리 필터 적용)"""
        all_tasks = self.storage_manager.get_tasks_by_date(date_str)

        # 1단계: 해당 날짜에 생성된 작업만 먼저 필터링
        date_tasks = [t for t in all_tasks if t.created_date == date_str]
        print(f"루틴 - 1단계 날짜별 필터링: {date_str}에 생성된 작업 {len(date_tasks)}개")

        # 2단계: 카테고리 필터 적용
        if selected_categories is not None and len(selected_categories) > 0:  # 특정 카테고리만 선택된 경우
            filtered_tasks = [t for t in date_tasks if t.category in selected_categories]
            print(f"루틴 - 2단계 카테고리 필터링: {selected_categories} 카테고리로 필터링 -> {len(filtered_tasks)}개 작업")
        else:
            filtered_tasks = date_tasks
            print(f"루틴 - 2단계 카테고리 필터링: 모든 카테고리 포함 -> {len(filtered_tasks)}개 작업")

        return {
            "all": filtered_tasks,
            "completed": [t for t in filtered_tasks if t.completed],
            "incomplete": [t for t in filtered_tasks if not t.completed],
            "total": len(filtered_tasks),
            "completed_count": len([t for t in filtered_tasks if t.completed]),
            "completion_rate": (
                    len([t for t in filtered_tasks if t.completed]) / len(
                filtered_tasks) * 100) if filtered_tasks else 0
        }

    def create_routine_html_report(self, routine, tasks_data, date_str):
        """루틴용 HTML 리포트 생성 (테이블 기반, Outlook 호환성 개선)"""
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")

        # 카테고리 필터 정보
        selected_categories = routine.get("selected_categories")
        category_filter_info = ""

        print(f"루틴 HTML 생성 시 카테고리 필터: {selected_categories}")

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

        # 루틴 정보 섹션 (테이블 기반)
        routine_info = f'''
        <table width="100%" cellpadding="15" cellspacing="0" style="background-color: #e8f4fd; border: 1px solid #17a2b8; border-radius: 8px; margin-bottom: 20px;">
            <tr>
                <td style="text-align: center;">
                    <strong style="color: #17a2b8; font-size: 16px;">🔄 루틴 리포트</strong>
                    <div style="font-size: 12px; color: #0c5460; margin-top: 5px;">
                        루틴명: {routine.get('name', 'Unknown')} | 자동 발송
                    </div>
                </td>
            </tr>
        </table>
        '''

        # 작업 목록 섹션들 (테이블 기반)
        task_sections = ""
        content_types = routine.get("content_types", ["all"])

        if "all" in content_types and tasks_data['all']:
            task_sections += self.create_outlook_task_section("📋 전체 작업", tasks_data['all'])

        if "completed" in content_types and tasks_data['completed']:
            task_sections += self.create_outlook_task_section("✅ 완료된 작업", tasks_data['completed'])

        if "incomplete" in content_types and tasks_data['incomplete']:
            task_sections += self.create_outlook_task_section("⏳ 미완료 작업", tasks_data['incomplete'])

        # 추가 메모 섹션 (테이블 기반)
        memo_section = ""
        memo = routine.get("memo", "").strip()
        if memo:
            memo_section = f'''
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
                <tr>
                    <td style="padding: 10px 0 5px 0; border-bottom: 2px solid #e0e0e0;">
                        <h3 style="margin: 0; color: #333;">📝 추가 메모</h3>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                        {self.escape_html(memo).replace(chr(10), "<br>")}
                    </td>
                </tr>
            </table>
            '''

        # Outlook 호환 HTML (테이블 기반 레이아웃)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>루틴 리포트</title>
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
                                         루틴 리포트
                                    </h1>
                                    <div style="color: #ffffff; font-size: 16px; margin: 0;">
                                        {current_time} 자동 발송
                                    </div>
                                </td>
                            </tr>

                            <!-- 메인 컨텐츠 -->
                            <tr>
                                <td style="padding: 25px 20px;">

                                    {routine_info}
                                    {category_filter_info}

                                    <!-- 데일리 리포트 요약 -->
                                    <table width="100%" cellpadding="20" cellspacing="0" style="background-color: #e3f2fd; border-radius: 10px; margin-bottom: 20px;">
                                        <tr>
                                            <td>
                                                <h2 style="margin: 0 0 15px 0; color: #1976d2; text-align: center;"> {report_date} 업무 현황</h2>

                                                <!-- 통계 테이블 -->
                                                <table width="100%" cellpadding="10" cellspacing="0">
                                                    <tr>
                                                        <td width="33%" style="text-align: center;">
                                                            <div style="font-size: 24px; font-weight: bold; color: #2196f3;">{tasks_data['total']}</div>
                                                            <div style="font-size: 12px; color: #666;">전체 작업</div>
                                                        </td>
                                                        <td width="33%" style="text-align: center;">
                                                            <div style="font-size: 24px; font-weight: bold; color: #4caf50;">{tasks_data['completed_count']}</div>
                                                            <div style="font-size: 12px; color: #666;">완료됨</div>
                                                        </td>
                                                        <td width="33%" style="text-align: center;">
                                                            <div style="font-size: 24px; font-weight: bold; color: #f44336;">{tasks_data['total'] - tasks_data['completed_count']}</div>
                                                            <div style="font-size: 12px; color: #666;">미완료</div>
                                                        </td>
                                                    </tr>
                                                </table>

                                                <!-- 완료율 -->
                                                <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #ffffff; border-radius: 5px; margin-top: 15px;">
                                                    <tr>
                                                        <td>
                                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                                <tr>
                                                                    <td style="font-weight: bold;">완료율</td>
                                                                    <td style="text-align: right; font-weight: bold; color: #4caf50;">
                                                                        {tasks_data['completion_rate']:.0f}%
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 5px;">
                                                                <tr>
                                                                    <td style="background-color: #e0e0e0; height: 8px; border-radius: 4px;">
                                                                        <div style="background-color: #4caf50; height: 8px; width: {tasks_data['completion_rate']:.0f}%; border-radius: 4px;"></div>
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
                                    {memo_section}

                                </td>
                            </tr>

                            <!-- 푸터 -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 15px 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #e9ecef;">
                                     Todolist PM 자동 루틴에서 발송 | {current_time}<br>
                                    루틴: {routine.get('name', 'Unknown')} - {report_date}
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
                    <td style="text-align: center; color: #666; padding: 20px;">해당하는 작업이 없습니다</td>
                </tr>
            </table>
            """

        task_rows = ""
        for task in tasks:
            status = "✅" if task.completed else "⏳"
            text_style = "text-decoration: line-through; color: #666;" if task.completed else ""
            importance = "⭐ " if task.important else ""
            border_color = "#4caf50" if task.completed else "#2196f3"

            task_rows += f"""
            <tr>
                <td style="padding: 10px; background-color: #f8f9fa; border-left: 3px solid {border_color}; border-radius: 5px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="{text_style}">
                                <strong>{status} {importance}{self.escape_html(task.title)}</strong>
                                <span style="background-color: {self.get_category_color(task.category)}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 10px;">
                                    {task.category}
                                </span>
                            </td>
                        </tr>
                        {f'<tr><td style="font-size: 12px; color: #666; padding-top: 5px;">{self.escape_html(task.content[:50])}</td></tr>' if task.content else ''}
                    </table>
                </td>
            </tr>
            <tr><td style="height: 5px;"></td></tr>
            """

        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 20px;">
            <tr>
                <td style="padding: 10px 0 5px 0; border-bottom: 2px solid #e0e0e0;">
                    <h3 style="margin: 0; color: #333;">{title} ({len(tasks)}개)</h3>
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