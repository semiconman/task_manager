#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import json
import sys
from datetime import datetime, timedelta


class EmailScheduler:
    """Windows 작업 스케줄러를 활용한 메일 자동 발송 관리"""

    def __init__(self):
        """스케줄러 초기화"""
        self.task_name_prefix = "TodolistEmailSender"
        self.script_path = self.create_scheduler_script()

    def setup_schedule(self, settings):
        """자동 발송 스케줄 설정

        Args:
            settings (dict): 메일 설정 정보
        """
        try:
            # 기존 스케줄 삭제
            self.remove_existing_schedules()

            # 새 스케줄 생성
            if settings.get("auto_send_enabled", False):
                self.create_schedule(settings)
                print("자동 발송 스케줄이 설정되었습니다.")
            else:
                print("자동 발송이 비활성화되었습니다.")

        except Exception as e:
            print(f"스케줄 설정 중 오류: {e}")
            raise

    def create_schedule(self, settings):
        """스케줄 생성

        Args:
            settings (dict): 메일 설정 정보
        """
        frequency = settings.get("frequency", "daily")
        send_time = settings.get("send_time", "09:00")

        # 작업 이름 생성
        task_name = f"{self.task_name_prefix}_{frequency}"

        if frequency == "daily":
            self.create_daily_schedule(task_name, send_time)
        elif frequency == "weekdays":
            self.create_weekdays_schedule(task_name, send_time)
        elif frequency == "weekly":
            self.create_weekly_schedule(task_name, send_time)
        elif frequency == "custom":
            # 사용자 지정은 일단 daily로 처리
            self.create_daily_schedule(task_name, send_time)

    def create_daily_schedule(self, task_name, send_time):
        """매일 스케줄 생성"""
        cmd = f'''schtasks /create /tn "{task_name}" /tr "python \\"{self.script_path}\\"" /sc daily /st {send_time} /ru SYSTEM /f'''
        self.execute_command(cmd)

    def create_weekdays_schedule(self, task_name, send_time):
        """평일 스케줄 생성 (월-금)"""
        cmd = f'''schtasks /create /tn "{task_name}" /tr "python \\"{self.script_path}\\"" /sc weekly /d MON,TUE,WED,THU,FRI /st {send_time} /ru SYSTEM /f'''
        self.execute_command(cmd)

    def create_weekly_schedule(self, task_name, send_time):
        """주간 스케줄 생성 (매주 월요일)"""
        cmd = f'''schtasks /create /tn "{task_name}" /tr "python \\"{self.script_path}\\"" /sc weekly /d MON /st {send_time} /ru SYSTEM /f'''
        self.execute_command(cmd)

    def remove_existing_schedules(self):
        """기존 스케줄 삭제"""
        try:
            # 기존 작업들 삭제
            frequencies = ["daily", "weekdays", "weekly", "custom"]
            for freq in frequencies:
                task_name = f"{self.task_name_prefix}_{freq}"
                cmd = f'schtasks /delete /tn "{task_name}" /f'
                self.execute_command(cmd, ignore_errors=True)

        except Exception as e:
            print(f"기존 스케줄 삭제 중 오류 (무시 가능): {e}")

    def execute_command(self, cmd, ignore_errors=False):
        """명령어 실행

        Args:
            cmd (str): 실행할 명령어
            ignore_errors (bool): 오류 무시 여부
        """
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='cp949')
            if result.returncode != 0 and not ignore_errors:
                print(f"명령어 실행 실패: {cmd}")
                print(f"오류: {result.stderr}")
                raise Exception(f"스케줄러 명령 실행 실패: {result.stderr}")
            else:
                print(f"명령어 실행 성공: {cmd}")
        except Exception as e:
            if not ignore_errors:
                raise
            print(f"명령어 실행 중 오류 (무시됨): {e}")

    def create_scheduler_script(self):
        """스케줄러에서 실행할 스크립트 파일 생성

        Returns:
            str: 생성된 스크립트 파일 경로
        """
        try:
            # 현재 디렉토리에 스크립트 생성
            script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows 작업 스케줄러에서 실행되는 메일 발송 스크립트
"""

import sys
import os
import json
from datetime import datetime

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from utils.storage import StorageManager
    from utils.email_sender import EmailSender

    def load_email_settings():
        """메일 설정 로드"""
        try:
            settings_file = os.path.join(current_dir, "data", "email_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"메일 설정 로드 중 오류: {e}")

        return None

    def main():
        """메인 실행 함수"""
        try:
            print(f"자동 메일 발송 시작: {datetime.now()}")

            # 설정 로드
            settings = load_email_settings()
            if not settings:
                print("메일 설정을 찾을 수 없습니다.")
                return

            if not settings.get("auto_send_enabled", False):
                print("자동 발송이 비활성화되어 있습니다.")
                return

            # 스토리지 매니저 초기화
            storage_manager = StorageManager()

            # 메일 발송
            sender = EmailSender(storage_manager)
            success = sender.send_scheduled_email(settings, is_test=False)

            if success:
                print("자동 메일 발송 완료")
            else:
                print("자동 메일 발송 실패")

        except Exception as e:
            print(f"자동 메일 발송 중 오류: {e}")
            import traceback
            traceback.print_exc()

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"모듈 임포트 오류: {e}")
    print(f"현재 디렉토리: {current_dir}")
    print(f"Python 경로: {sys.path}")
except Exception as e:
    print(f"스크립트 실행 중 오류: {e}")
    import traceback
    traceback.print_exc()
'''

            # 스크립트 파일 경로
            script_path = os.path.join(os.getcwd(), "scheduled_email_sender.py")

            # 스크립트 파일 작성
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)

            print(f"스케줄러 스크립트 생성: {script_path}")
            return script_path

        except Exception as e:
            print(f"스케줄러 스크립트 생성 중 오류: {e}")
            raise

    def get_schedule_status(self):
        """현재 스케줄 상태 조회

        Returns:
            dict: 스케줄 상태 정보
        """
        try:
            result = subprocess.run(
                f'schtasks /query /tn "{self.task_name_prefix}_*" /fo csv',
                shell=True, capture_output=True, text=True, encoding='cp949'
            )

            status = {
                "active_schedules": [],
                "last_run": None,
                "next_run": None
            }

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # 헤더 제외
                    for line in lines[1:]:
                        if line.strip():
                            parts = line.split(',')
                            if len(parts) >= 4:
                                task_name = parts[0].strip('"')
                                task_status = parts[3].strip('"')
                                status["active_schedules"].append({
                                    "name": task_name,
                                    "status": task_status
                                })

            return status

        except Exception as e:
            print(f"스케줄 상태 조회 중 오류: {e}")
            return {"error": str(e)}

    def disable_all_schedules(self):
        """모든 자동 발송 스케줄 비활성화"""
        try:
            self.remove_existing_schedules()
            print("모든 자동 발송 스케줄이 비활성화되었습니다.")
        except Exception as e:
            print(f"스케줄 비활성화 중 오류: {e}")
            raise