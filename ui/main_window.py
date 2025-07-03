#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QMenuBar, QMenu, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QIcon

from datetime import datetime
from ui.calendar_widget import CalendarWidget
from ui.task_list import TaskListWidget
from ui.task_form import TaskForm
from ui.export_dialog import ExportDialog
from ui.category_dialog import CategoryDialog
from utils.date_utils import get_current_date_str, format_date_for_display


class MainWindow(QMainWindow):
    """애플리케이션 메인 윈도우"""

    def __init__(self, storage_manager):
        """메인 윈도우 초기화

        Args:
            storage_manager (StorageManager): 데이터 저장소 관리자
        """
        super().__init__()

        self.storage_manager = storage_manager
        self.current_date = get_current_date_str()

        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        # 윈도우 설정
        self.setWindowTitle("Todolist_PM")
        self.setMinimumSize(900, 600)

        # 메뉴바 설정
        self.setup_menu_bar()

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QHBoxLayout(central_widget)

        # 스플리터 (좌측: 달력, 우측: 작업 목록)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # 좌측: 달력 위젯
        self.calendar_container = QWidget()
        calendar_layout = QVBoxLayout(self.calendar_container)
        calendar_layout.setContentsMargins(10, 10, 10, 10)

        # 달력 타이틀
        calendar_title = QLabel("달력")
        calendar_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        calendar_layout.addWidget(calendar_title)

        # 달력 위젯
        self.calendar_widget = CalendarWidget(self.storage_manager)
        self.calendar_widget.date_selected.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar_widget)

        self.splitter.addWidget(self.calendar_container)

        # 우측: 작업 영역
        self.task_container = QWidget()
        task_layout = QVBoxLayout(self.task_container)
        task_layout.setContentsMargins(10, 10, 10, 10)

        # 상단 바: 날짜 표시 + 버튼
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 10)

        # 날짜 표시
        self.date_label = QLabel(format_date_for_display(self.current_date))
        self.date_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_bar_layout.addWidget(self.date_label)

        top_bar_layout.addStretch()

        # 새 작업 버튼
        self.add_task_button = QPushButton("새 작업")
        self.add_task_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_task_button.clicked.connect(self.on_add_task)
        top_bar_layout.addWidget(self.add_task_button)

        # 옵션 버튼
        self.options_button = QPushButton("옵션")
        self.options_button.setIcon(QIcon("resources/icons/options.png"))
        self.options_button.clicked.connect(self.show_options_menu)
        top_bar_layout.addWidget(self.options_button)

        task_layout.addWidget(top_bar)

        # 작업 목록
        self.task_list = TaskListWidget(self.storage_manager)
        self.task_list.task_edited.connect(self.refresh_ui)
        task_layout.addWidget(self.task_list)

        self.splitter.addWidget(self.task_container)

        # 스플리터 비율 설정 (좌:우 = 1:3)
        self.splitter.setSizes([200, 600])

        # 현재 날짜의 작업 로드
        self.load_current_date_tasks()

        # 달력 뷰 모드 상태 초기화
        self.calendar_view_mode = False

    def setup_menu_bar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일")

        # 새 작업
        new_task_action = QAction("새 작업", self)
        new_task_action.setShortcut("Ctrl+N")
        new_task_action.triggered.connect(self.on_add_task)
        file_menu.addAction(new_task_action)

        file_menu.addSeparator()

        # CSV 내보내기
        export_action = QAction("CSV 내보내기...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.on_export_csv)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # 종료
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 보기 메뉴
        view_menu = menubar.addMenu("보기")

        # 오늘 날짜로 이동
        today_action = QAction("오늘", self)
        today_action.setShortcut("Ctrl+T")
        today_action.triggered.connect(self.go_to_today)
        view_menu.addAction(today_action)

        # 달력 뷰 모드 전환
        self.calendar_view_action = QAction("달력 뷰", self)
        self.calendar_view_action.setShortcut("Ctrl+D")
        self.calendar_view_action.setCheckable(True)
        self.calendar_view_action.toggled.connect(self.toggle_calendar_view)
        view_menu.addAction(self.calendar_view_action)

        # 옵션 메뉴
        options_menu = menubar.addMenu("옵션")

        # 카테고리 관리
        category_action = QAction("카테고리 관리", self)
        category_action.triggered.connect(self.on_manage_categories)
        options_menu.addAction(category_action)

        # 메일 설정
        email_action = QAction("메일 설정", self)
        email_action.triggered.connect(self.on_email_settings)
        options_menu.addAction(email_action)

        # 메일 관리 (간단버전)
        simple_email_action = QAction("메일 관리", self)
        simple_email_action.triggered.connect(self.on_simple_email)
        options_menu.addAction(simple_email_action)

    def on_date_selected(self, date):
        """날짜 선택 이벤트 처리

        Args:
            date (QDate): 선택된 날짜
        """
        try:
            # QDate를 문자열로 변환 (YYYY-MM-DD)
            selected_date = date.toString("yyyy-MM-dd")
            self.current_date = selected_date

            # UI 업데이트
            self.date_label.setText(format_date_for_display(selected_date))
            self.load_current_date_tasks()
        except Exception as e:
            print(f"날짜 선택 처리 중 오류: {e}")

    def load_current_date_tasks(self):
        """현재 선택된 날짜의 작업 로드"""
        try:
            tasks = self.storage_manager.get_tasks_by_date(self.current_date)
            self.task_list.load_tasks(tasks, self.current_date)
        except Exception as e:
            print(f"작업 로드 중 오류: {e}")

    def on_add_task(self):
        """새 작업 추가 버튼 클릭 이벤트 처리"""
        try:
            dialog = TaskForm(self.storage_manager, self.current_date)
            if dialog.exec():
                self.refresh_ui()
        except Exception as e:
            print(f"작업 추가 중 오류: {e}")

    def show_options_menu(self):
        """옵션 버튼 클릭 시 메뉴 표시"""
        menu = QMenu(self)

        # 카테고리 관리
        category_action = QAction("카테고리 관리", self)
        category_action.triggered.connect(self.on_manage_categories)
        menu.addAction(category_action)

        # CSV 내보내기
        export_action = QAction("CSV 내보내기", self)
        export_action.triggered.connect(self.on_export_csv)
        menu.addAction(export_action)

        # 메일 설정
        email_action = QAction("메일 설정", self)
        email_action.triggered.connect(self.on_email_settings)
        menu.addAction(email_action)

        # 즉시 메일 발송
        send_mail_action = QAction("즉시 메일 발송", self)
        send_mail_action.triggered.connect(self.on_send_immediate_email)
        menu.addAction(send_mail_action)

        # 달력 뷰 모드 전환
        calendar_view_action = QAction("달력 뷰 모드", self)
        calendar_view_action.setCheckable(True)
        calendar_view_action.setChecked(self.calendar_view_mode)
        calendar_view_action.toggled.connect(self.toggle_calendar_view)
        menu.addAction(calendar_view_action)

        # 메뉴 표시
        menu.exec(self.options_button.mapToGlobal(self.options_button.rect().bottomLeft()))

    def on_manage_categories(self):
        """카테고리 관리 대화상자 표시"""
        try:
            dialog = CategoryDialog(self.storage_manager)
            if dialog.exec():
                self.refresh_ui()
        except Exception as e:
            print(f"카테고리 관리 중 오류: {e}")

    def on_export_csv(self):
        """CSV 내보내기 대화상자 표시"""
        try:
            dialog = ExportDialog(self.storage_manager)
            dialog.exec()
        except Exception as e:
            print(f"CSV 내보내기 중 오류: {e}")

    def go_to_today(self):
        """오늘 날짜로 이동"""
        try:
            today = QDate.currentDate()
            self.calendar_widget.setSelectedDate(today)
            self.on_date_selected(today)
        except Exception as e:
            print(f"오늘 날짜로 이동 중 오류: {e}")

    def toggle_calendar_view(self, checked):
        """달력 뷰 모드 전환

        Args:
            checked (bool): 달력 뷰 활성화 여부
        """
        try:
            # 달력 뷰 모드 상태 저장
            self.calendar_view_mode = checked

            # 달력 뷰 모드 액션 상태 동기화
            self.calendar_view_action.setChecked(checked)

            if checked:
                # 달력 뷰 모드로 전환
                self.task_container.hide()
                # 달력 크기 조정
                self.splitter.setSizes([self.width(), 0])
                # 달력 위젯에 뷰 모드 설정
                if hasattr(self.calendar_widget, 'setCalendarViewMode'):
                    self.calendar_widget.setCalendarViewMode(True)
            else:
                # 기본 모드로 전환
                self.task_container.show()
                # 스플리터 비율 복원
                self.splitter.setSizes([200, 600])
                # 달력 위젯에 뷰 모드 해제
                if hasattr(self.calendar_widget, 'setCalendarViewMode'):
                    self.calendar_widget.setCalendarViewMode(False)

            # UI 새로고침
            self.refresh_ui()
        except Exception as e:
            print(f"달력 뷰 모드 전환 중 오류 발생: {e}")

    def refresh_ui(self):
        """UI 새로고침"""
        try:
            self.load_current_date_tasks()
            self.calendar_widget.update_calendar()
        except Exception as e:
            print(f"UI 새로고침 중 오류: {e}")

    def closeEvent(self, event):
        """애플리케이션 종료 이벤트 처리

        Args:
            event: 종료 이벤트
        """
        # 종료 전에 데이터 저장
        self.storage_manager.save_data()
        event.accept()

    def on_email_settings(self):
        """메일 설정 대화상자 표시"""
        try:
            from ui.email_settings_dialog import EmailSettingsDialog
            dialog = EmailSettingsDialog(self.storage_manager)
            dialog.exec()
        except Exception as e:
            print(f"메일 설정 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"메일 설정 중 오류가 발생했습니다:\n{e}")

    def on_simple_email(self):
        """간단한 메일 관리 대화상자 표시"""
        try:
            from ui.simple_email_dialog import SimpleEmailDialog
            dialog = SimpleEmailDialog(self.storage_manager)
            dialog.exec()
        except Exception as e:
            print(f"메일 관리 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"메일 관리 중 오류가 발생했습니다:\n{e}")
    def on_email_schedule(self):
        """메일 예약 관리 대화상자 표시"""
        try:
            from ui.email_schedule_dialog import EmailScheduleDialog
            dialog = EmailScheduleDialog(self.storage_manager)
            dialog.exec()
        except Exception as e:
            print(f"메일 예약 관리 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"메일 예약 관리 중 오류가 발생했습니다:\n{e}")
    def on_send_immediate_email(self):
        """즉시 메일 발송"""
        try:
            from utils.email_sender import EmailSender
            import json
            import os

            # 메일 기능 사용 가능 여부 먼저 확인
            sender = EmailSender(self.storage_manager)
            available, error_msg = sender.check_availability()
            if not available:
                QMessageBox.critical(self, "메일 기능 사용 불가", error_msg)
                return

            # 메일 설정 로드
            settings_file = "data/email_settings.json"
            if not os.path.exists(settings_file):
                QMessageBox.warning(self, "설정 없음",
                                    "메일 설정이 없습니다.\n먼저 '옵션 > 메일 설정'에서 설정을 완료하세요.")
                return

            with open(settings_file, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # 수신자 확인
            if not settings.get("recipients"):
                QMessageBox.warning(self, "수신자 없음",
                                    "수신자가 설정되지 않았습니다.\n먼저 메일 설정에서 수신자를 추가하세요.")
                return

            # 메일 발송 확인
            recipients_text = ", ".join(settings["recipients"])
            reply = QMessageBox.question(
                self, "메일 발송 확인",
                f"다음 수신자에게 메일을 발송하시겠습니까?\n\n{recipients_text}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 메일 발송
                success = sender.send_scheduled_email(settings, is_test=False)

                if success:
                    QMessageBox.information(self, "발송 완료", "메일이 성공적으로 발송되었습니다.")
                else:
                    QMessageBox.critical(self, "발송 실패", "메일 발송에 실패했습니다.\n\nOutlook이 실행 중인지 확인하세요.")

        except Exception as e:
            print(f"즉시 메일 발송 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"메일 발송 중 오류가 발생했습니다:\n{e}")
