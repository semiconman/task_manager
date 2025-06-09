#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


# 배포 환경에서 콘솔 출력 완전 차단
def hide_console_in_build():
    """배포된 실행 파일에서 콘솔 출력 숨기기"""
    if hasattr(sys, 'frozen'):  # cx_freeze로 빌드된 경우
        import ctypes
        import ctypes.wintypes

        # Windows에서 콘솔 창 숨기기
        if sys.platform == "win32":
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32

            # 콘솔 창 핸들 가져오기
            console_window = kernel32.GetConsoleWindow()
            if console_window:
                # 콘솔 창 숨기기
                user32.ShowWindow(console_window, 0)  # 0 = SW_HIDE

        # stdout, stderr 리다이렉트 (모든 print 출력 차단)
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')


# 콘솔 숨기기 실행
hide_console_in_build()

from ui.main_window import MainWindow
from utils.storage import StorageManager


# 예외 처리기 설정 (빌드 환경에서는 로그 파일로만 저장)
def exception_hook(exctype, value, tb):
    """예외 처리기"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))

    # 개발 환경에서만 콘솔 출력
    if not hasattr(sys, 'frozen'):
        print(f"예외 발생:\n{error_msg}")

    # 빌드 환경에서는 파일로만 저장
    try:
        with open("error_log.txt", 'a', encoding='utf-8') as f:
            f.write(f"\n\nError Time: {datetime.now()}\n")
            f.write(f"Exception Type: {exctype.__name__}\n")
            f.write(f"Exception Value: {value}\n")
            f.write(f"Traceback:\n{''.join(traceback.format_tb(tb))}\n")
    except:
        pass  # 로그 파일 쓰기도 실패하면 조용히 무시

    sys.__excepthook__(exctype, value, tb)


sys.excepthook = exception_hook

# 현재 시간 가져오기 (오류 로그용)
from datetime import datetime

import_time = datetime.now()

# 개발 환경에서만 출력
if not hasattr(sys, 'frozen'):
    print(f"프로그램 시작: {import_time}")
    print("오류 발생 시 error_log.txt 파일을 확인하세요.")


def main():
    """애플리케이션 진입점"""
    try:
        # QApplication 인스턴스 생성
        app = QApplication(sys.argv)
        app.setApplicationName("MacOS Task Manager")

        # 스타일시트 적용 (맥OS 스타일)
        try:
            with open("resources/styles/macos_style.qss", "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            # 빌드 환경에서는 조용히 무시
            if not hasattr(sys, 'frozen'):
                print(f"스타일시트 로딩 중 오류: {e}")

        # 스토리지 매니저 초기화
        storage_manager = StorageManager()

        # 메인 윈도우 생성
        main_window = MainWindow(storage_manager)
        main_window.show()

        # 자동 저장 타이머 설정 (1초 간격)
        auto_save_timer = QTimer()
        auto_save_timer.timeout.connect(storage_manager.save_data)
        auto_save_timer.start(1000)  # 1초마다 저장

        # 애플리케이션 실행
        return app.exec()
    except Exception as e:
        # 빌드 환경에서는 로그 파일로만 저장
        if not hasattr(sys, 'frozen'):
            print(f"main() 함수 내에서 오류 발생: {e}")
            traceback.print_exc()
        else:
            try:
                with open("error_log.txt", 'a', encoding='utf-8') as f:
                    f.write(f"\n\nMain Error: {e}\n")
                    f.write(traceback.format_exc())
            except:
                pass
        return 1


if __name__ == "__main__":
    # 리소스 디렉토리 확인 및 생성
    for dir_path in ["resources/icons", "resources/styles", "data"]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            # 빌드 환경에서는 출력 안함
            if not hasattr(sys, 'frozen'):
                print(f"디렉토리 생성: {dir_path}")

    # 메인 함수 실행
    try:
        exit_code = main()
        if not hasattr(sys, 'frozen'):
            print(f"프로그램 정상 종료. 종료 코드: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        if not hasattr(sys, 'frozen'):
            print(f"프로그램 실행 중 치명적인 오류 발생: {e}")
            traceback.print_exc()
        sys.exit(1)