#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from ui.main_window import MainWindow
from utils.storage import StorageManager


# 예외 처리기 설정
def exception_hook(exctype, value, tb):
    """예외 처리기"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"예외 발생:\n{error_msg}")

    # 오류 메시지를 파일에 저장
    with open("error_log.txt", 'a', encoding='utf-8') as f:
        f.write(f"\n\nError Time: {import_time}\n")
        f.write(f"Exception Type: {exctype.__name__}\n")
        f.write(f"Exception Value: {value}\n")
        f.write(f"Traceback:\n{''.join(traceback.format_tb(tb))}\n")

    sys.__excepthook__(exctype, value, tb)


sys.excepthook = exception_hook

# 현재 시간 가져오기 (오류 로그용)
from datetime import datetime

import_time = datetime.now()

print(f"프로그램 시작: {import_time}")
print("오류 발생 시 error_log.txt 파일을 확인하세요.")


def main():
    """애플리케이션 진입점"""
    try:
        print("QApplication 인스턴스 생성 시작...")
        # QApplication 인스턴스 생성
        app = QApplication(sys.argv)
        app.setApplicationName("MacOS Task Manager")
        print("QApplication 인스턴스 생성 완료")

        print("스타일시트 적용 시작...")
        # 스타일시트 적용 (맥OS 스타일)
        try:
            with open("resources/styles/macos_style.qss", "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            print("스타일시트 적용 완료")
        except Exception as e:
            print(f"스타일시트 로딩 중 오류: {e}")

        print("스토리지 매니저 초기화 시작...")
        # 스토리지 매니저 초기화
        storage_manager = StorageManager()
        print("스토리지 매니저 초기화 완료")

        print("메인 윈도우 생성 시작...")
        # 메인 윈도우 생성
        main_window = MainWindow(storage_manager)
        print("메인 윈도우 생성 완료")

        print("메인 윈도우 표시...")
        main_window.show()
        print("메인 윈도우 표시 완료")

        print("자동 저장 타이머 설정...")
        # 자동 저장 타이머 설정 (1초 간격)
        auto_save_timer = QTimer()
        auto_save_timer.timeout.connect(storage_manager.save_data)
        auto_save_timer.start(1000)  # 1초마다 저장
        print("자동 저장 타이머 설정 완료")

        print("애플리케이션 실행...")
        # 애플리케이션 실행
        return app.exec()
    except Exception as e:
        print(f"main() 함수 내에서 오류 발생: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # 리소스 디렉토리 확인 및 생성
    for dir_path in ["resources/icons", "resources/styles", "data"]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"디렉토리 생성: {dir_path}")

    # 메인 함수 실행
    try:
        print("메인 함수 실행 시작...")
        exit_code = main()
        print(f"프로그램 정상 종료. 종료 코드: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"프로그램 실행 중 치명적인 오류 발생: {e}")
        traceback.print_exc()
        sys.exit(1)