#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QComboBox, QTimeEdit,
    QListWidget, QListWidgetItem, QMessageBox, QFrame,
    QButtonGroup, QRadioButton, QDateEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QTime, QDate, QTimer
from PyQt6.QtGui import QFont


class SimpleEmailDialog(QDialog):
    """간단한 메일 관리 대화상자 - 모든 기능을 하나로 통합"""

    def __init__(self, storage_manager):
        super().__init__()

        self.storage_manager = storage_manager
        self.email_schedules = self.load_email_schedules()

        # 자동 발송 타이머 (1분마다)
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.check_auto_send)
        self.auto_timer.start(60000)

        self.setWindowTitle("📧 메일 관리")
        self.setMinimumSize(950, 750)  # 크기 증가 (카테고리 선택 영역 추가로)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()
        self.load_schedule_list()

    def init_ui(self):
        """UI 초기화 - 왼쪽 목록, 오른쪽 설정"""
        layout = QHBoxLayout(self)

        # === 왼쪽: 예약 목록 ===
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_frame)

        # 제목
        title_label = QLabel("📋 메일 예약 목록")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        left_layout.addWidget(title_label)

        # 예약 목록
        self.schedule_list = QListWidget()
        self.schedule_list.itemClicked.connect(self.on_schedule_clicked)
        left_layout.addWidget(self.schedule_list)

        # 목록 버튼들
        list_btn_layout = QHBoxLayout()

        self.send_now_btn = QPushButton("즉시발송")
        self.send_now_btn.clicked.connect(self.send_now)
        self.send_now_btn.setStyleSheet("background: #28a745; color: white; padding: 8px; border-radius: 4px;")

        self.delete_btn = QPushButton("삭제")
        self.delete_btn.clicked.connect(self.delete_schedule)
        self.delete_btn.setStyleSheet("background: #dc3545; color: white; padding: 8px; border-radius: 4px;")

        self.toggle_btn = QPushButton("ON/OFF")
        self.toggle_btn.clicked.connect(self.toggle_schedule)
        self.toggle_btn.setStyleSheet("background: #6c757d; color: white; padding: 8px; border-radius: 4px;")

        list_btn_layout.addWidget(self.send_now_btn)
        list_btn_layout.addWidget(self.delete_btn)
        list_btn_layout.addWidget(self.toggle_btn)
        left_layout.addLayout(list_btn_layout)

        layout.addWidget(left_frame, 1)

        # === 오른쪽: 새 예약 추가 ===
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)

        # 제목
        add_title = QLabel("➕ 새 메일 예약")
        add_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        right_layout.addWidget(add_title)

        # 스크롤 영역 (내용이 많아졌으므로)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # === 1. 기본 정보 ===
        basic_group = QGroupBox("기본 정보")
        basic_layout = QVBoxLayout(basic_group)

        # 예약 이름
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("이름:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("예: 주간보고")
        name_layout.addWidget(self.name_edit)
        basic_layout.addLayout(name_layout)

        # 메일 제목
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("제목:"))
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("예: 업무현황")
        subject_layout.addWidget(self.subject_edit)
        basic_layout.addLayout(subject_layout)

        # 수신자 (메일설정에서 불러오기 + 직접 입력)
        recipient_layout = QVBoxLayout()
        recipient_top = QHBoxLayout()
        recipient_top.addWidget(QLabel("수신자:"))

        # 메일설정에서 불러오기 버튼
        load_recipients_btn = QPushButton("📋 저장된 수신자")
        load_recipients_btn.clicked.connect(self.load_saved_recipients)
        load_recipients_btn.setStyleSheet(
            "background: #17a2b8; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;")
        recipient_top.addWidget(load_recipients_btn)
        recipient_top.addStretch()

        recipient_layout.addLayout(recipient_top)

        # 수신자 목록 (여러명 지원)
        self.recipients_list_widget = QListWidget()
        self.recipients_list_widget.setMaximumHeight(60)
        recipient_layout.addWidget(self.recipients_list_widget)

        # 수신자 추가/삭제
        recipient_control = QHBoxLayout()
        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("abc@company.com")

        add_recipient_btn = QPushButton("추가")
        add_recipient_btn.clicked.connect(self.add_recipient_to_list)
        add_recipient_btn.setStyleSheet(
            "background: #28a745; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;")

        remove_recipient_btn = QPushButton("삭제")
        remove_recipient_btn.clicked.connect(self.remove_recipient_from_list)
        remove_recipient_btn.setStyleSheet(
            "background: #dc3545; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;")

        recipient_control.addWidget(self.recipient_edit)
        recipient_control.addWidget(add_recipient_btn)
        recipient_control.addWidget(remove_recipient_btn)
        recipient_layout.addLayout(recipient_control)

        basic_layout.addLayout(recipient_layout)
        scroll_layout.addWidget(basic_group)

        # === 2. 발송 설정 ===
        schedule_group = QGroupBox("발송 설정")
        schedule_layout = QVBoxLayout(schedule_group)

        # 발송 타입
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup()

        self.once_radio = QRadioButton("한번만")
        self.once_radio.setChecked(True)

        self.daily_radio = QRadioButton("매일")
        self.weekly_radio = QRadioButton("매주")

        self.type_group.addButton(self.once_radio)
        self.type_group.addButton(self.daily_radio)
        self.type_group.addButton(self.weekly_radio)

        # 라디오 버튼 그룹 시그널 연결
        self.type_group.buttonClicked.connect(self.on_type_changed)

        type_layout.addWidget(QLabel("타입:"))
        type_layout.addWidget(self.once_radio)
        type_layout.addWidget(self.daily_radio)
        type_layout.addWidget(self.weekly_radio)
        type_layout.addStretch()
        schedule_layout.addLayout(type_layout)

        # 날짜/시간 설정
        datetime_layout = QVBoxLayout()

        # 날짜 (한번만 발송시에만)
        date_time_row1 = QHBoxLayout()
        self.date_label = QLabel("날짜:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate().addDays(1))
        self.date_edit.setCalendarPopup(True)

        date_time_row1.addWidget(self.date_label)
        date_time_row1.addWidget(self.date_edit)
        date_time_row1.addStretch()
        datetime_layout.addLayout(date_time_row1)

        # 시간
        date_time_row2 = QHBoxLayout()
        time_label = QLabel("시간:")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(9, 0))
        self.time_edit.setDisplayFormat("HH:mm")

        date_time_row2.addWidget(time_label)
        date_time_row2.addWidget(self.time_edit)
        date_time_row2.addStretch()
        datetime_layout.addLayout(date_time_row2)

        # 요일 선택 (매주 발송시에만)
        weekday_row = QHBoxLayout()
        self.weekday_label = QLabel("요일:")
        self.weekday_combo = QComboBox()
        self.weekday_combo.addItems(["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"])

        weekday_row.addWidget(self.weekday_label)
        weekday_row.addWidget(self.weekday_combo)
        weekday_row.addStretch()
        datetime_layout.addLayout(weekday_row)

        schedule_layout.addLayout(datetime_layout)
        scroll_layout.addWidget(schedule_group)

        # === 3. 카테고리 필터 ===
        category_group = QGroupBox("카테고리 필터")
        category_layout = QVBoxLayout(category_group)

        # 안내 메시지
        category_info = QLabel("특정 카테고리의 작업만 포함하려면 선택하세요. 전체 선택 시 모든 카테고리가 포함됩니다.")
        category_info.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 8px;")
        category_info.setWordWrap(True)
        category_layout.addWidget(category_info)

        # 전체 선택 체크박스
        category_select_layout = QHBoxLayout()
        self.all_categories_check = QCheckBox("모든 카테고리")
        self.all_categories_check.setChecked(True)
        self.all_categories_check.stateChanged.connect(self.on_all_categories_changed)
        category_select_layout.addWidget(self.all_categories_check)

        # 카테고리별 체크박스
        self.category_checks = {}
        for category in self.storage_manager.categories:
            check = QCheckBox(category.name)
            check.setChecked(True)
            check.stateChanged.connect(self.on_category_check_changed)

            # 카테고리 색상으로 표시
            check.setStyleSheet(f"""
                QCheckBox {{
                    color: {category.color};
                    font-weight: bold;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {category.color};
                }}
            """)

            self.category_checks[category.name] = check
            category_select_layout.addWidget(check)

        category_layout.addLayout(category_select_layout)
        scroll_layout.addWidget(category_group)

        # === 4. 내용 설정 + 중요 일정 포함 (새로 추가) ===
        content_group = QGroupBox("메일 내용")
        content_layout = QVBoxLayout(content_group)

        # 포함할 내용 (첫 번째 줄)
        content_row1 = QHBoxLayout()
        self.all_check = QCheckBox("전체작업")
        self.all_check.setChecked(True)
        self.done_check = QCheckBox("완료작업")
        self.todo_check = QCheckBox("미완료작업")

        content_row1.addWidget(QLabel("포함:"))
        content_row1.addWidget(self.all_check)
        content_row1.addWidget(self.done_check)
        content_row1.addWidget(self.todo_check)

        # 기간 (첫 번째 줄 이어서)
        self.period_combo = QComboBox()
        self.period_combo.addItems(["오늘", "이번주", "저번주"])
        content_row1.addWidget(QLabel("기간:"))
        content_row1.addWidget(self.period_combo)
        content_row1.addStretch()

        content_layout.addLayout(content_row1)

        # 중요 일정 포함 (두 번째 줄) - 새로 추가
        important_row = QHBoxLayout()
        self.include_important_check = QCheckBox("📌 미완료 중요 일정 포함 (지난 30일)")
        self.include_important_check.setChecked(True)  # 기본값: 체크됨
        self.include_important_check.setToolTip("지난 30일간의 다른 날짜 미완료 중요 작업을 별도 섹션으로 포함")
        self.include_important_check.setStyleSheet("font-weight: bold; color: #d32f2f;")

        important_row.addWidget(self.include_important_check)
        important_row.addStretch()
        content_layout.addLayout(important_row)

        scroll_layout.addWidget(content_group)

        # 스크롤 영역 설정
        scroll_area.setWidget(scroll_content)
        right_layout.addWidget(scroll_area)

        # === 버튼들 ===
        btn_layout = QVBoxLayout()

        # 테스트 발송
        test_btn = QPushButton("🧪 테스트 발송")
        test_btn.clicked.connect(self.test_send)
        test_btn.setStyleSheet(
            "background: #17a2b8; color: white; padding: 12px; border-radius: 4px; font-weight: bold;")
        btn_layout.addWidget(test_btn)

        # 예약 추가
        add_btn = QPushButton("➕ 예약 추가")
        add_btn.clicked.connect(self.add_schedule)
        add_btn.setStyleSheet(
            "background: #007bff; color: white; padding: 12px; border-radius: 4px; font-weight: bold;")
        btn_layout.addWidget(add_btn)

        # 닫기
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background: #6c757d; color: white; padding: 8px; border-radius: 4px;")
        btn_layout.addWidget(close_btn)

        right_layout.addLayout(btn_layout)

        layout.addWidget(right_frame, 1)

        # 초기 상태 설정
        self.on_type_changed()

    def on_all_categories_changed(self, state):
        """모든 카테고리 체크박스 상태 변경"""
        checked = state == Qt.CheckState.Checked
        for check in self.category_checks.values():
            check.setChecked(checked)

    def on_category_check_changed(self):
        """개별 카테고리 체크박스 상태 변경"""
        # 모든 카테고리가 선택되었는지 확인
        all_checked = all(check.isChecked() for check in self.category_checks.values())
        any_checked = any(check.isChecked() for check in self.category_checks.values())

        # 전체 선택 체크박스 상태 업데이트
        self.all_categories_check.blockSignals(True)
        if all_checked:
            self.all_categories_check.setChecked(True)
        elif not any_checked:
            self.all_categories_check.setChecked(False)
        else:
            self.all_categories_check.setTristate(True)
            self.all_categories_check.setCheckState(Qt.CheckState.PartiallyChecked)
        self.all_categories_check.blockSignals(False)

    def get_selected_categories(self):
        """선택된 카테고리 목록 반환"""
        # 수정: 모든 카테고리 체크박스와 개별 체크박스 상태 모두 확인
        if self.all_categories_check.isChecked() and all(check.isChecked() for check in self.category_checks.values()):
            print("Simple Email - 카테고리 필터: 모든 카테고리 선택됨")
            return None  # 모든 카테고리

        selected_categories = []
        for category_name, check in self.category_checks.items():
            if check.isChecked():
                selected_categories.append(category_name)

        print(f"Simple Email - 카테고리 필터: 선택된 카테고리 = {selected_categories}")
        return selected_categories if selected_categories else None

    def on_type_changed(self, button=None):
        """발송 타입 변경시 - 버튼 클릭 시에만 호출됨"""
        try:
            # 현재 선택된 버튼 확인
            is_once = self.once_radio.isChecked()
            is_weekly = self.weekly_radio.isChecked()

            print(f"타입 변경: 한번만={is_once}, 매주={is_weekly}")  # 디버깅용

            # 날짜는 한번만 발송시에만 표시
            self.date_label.setVisible(is_once)
            self.date_edit.setVisible(is_once)

            # 요일은 매주 발송시에만 표시
            self.weekday_label.setVisible(is_weekly)
            self.weekday_combo.setVisible(is_weekly)

            print(f"요일 표시 상태: {is_weekly}")  # 디버깅용

        except Exception as e:
            print(f"타입 변경 중 오류: {e}")

    def load_saved_recipients(self):
        """메일설정에서 저장된 수신자 목록을 선택해서 추가"""
        try:
            settings_file = "data/email_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                saved_recipients = settings.get("recipients", [])
                if saved_recipients:
                    # 수신자 선택 다이얼로그 표시
                    self.show_recipient_selection_dialog(saved_recipients)
                else:
                    QMessageBox.information(self, "수신자 없음", "저장된 수신자가 없습니다.\n메일설정에서 수신자를 먼저 등록하세요.")
            else:
                QMessageBox.information(self, "설정 없음", "메일설정 파일이 없습니다.")

        except Exception as e:
            QMessageBox.warning(self, "오류", f"수신자 불러오기 실패:\n{e}")

    def show_recipient_selection_dialog(self, saved_recipients):
        """수신자 선택 다이얼로그 표시"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QCheckBox

        dialog = QDialog(self)
        dialog.setWindowTitle("수신자 선택")
        dialog.setMinimumSize(400, 300)

        layout = QVBoxLayout(dialog)

        # 안내 메시지
        info_label = QLabel("추가할 수신자를 선택하세요:")
        layout.addWidget(info_label)

        # 수신자 목록 (체크박스 형태)
        self.recipient_checkboxes = []
        current_recipients = self.get_current_recipients()

        for recipient in saved_recipients:
            checkbox = QCheckBox(recipient)
            # 이미 추가된 수신자는 비활성화
            if recipient in current_recipients:
                checkbox.setChecked(False)
                checkbox.setEnabled(False)
                checkbox.setText(f"{recipient} (이미 추가됨)")
            else:
                checkbox.setChecked(False)

            self.recipient_checkboxes.append(checkbox)
            layout.addWidget(checkbox)

        # 버튼
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("전체 선택")
        select_all_btn.clicked.connect(lambda: self.toggle_all_recipients(True))
        button_layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("전체 해제")
        select_none_btn.clicked.connect(lambda: self.toggle_all_recipients(False))
        button_layout.addWidget(select_none_btn)

        button_layout.addStretch()

        add_selected_btn = QPushButton("선택한 수신자 추가")
        add_selected_btn.clicked.connect(lambda: self.add_selected_recipients(dialog))
        add_selected_btn.setStyleSheet(
            "background: #28a745; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        button_layout.addWidget(add_selected_btn)

        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setStyleSheet("background: #6c757d; color: white; padding: 6px 12px; border-radius: 4px;")
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def toggle_all_recipients(self, select_all):
        """모든 수신자 선택/해제"""
        for checkbox in self.recipient_checkboxes:
            if checkbox.isEnabled():  # 비활성화된 것은 제외
                checkbox.setChecked(select_all)

    def add_selected_recipients(self, dialog):
        """선택된 수신자들을 목록에 추가"""
        selected_recipients = []

        for checkbox in self.recipient_checkboxes:
            if checkbox.isChecked() and checkbox.isEnabled():
                # 텍스트에서 이메일 주소만 추출
                email = checkbox.text().split(" (이미 추가됨)")[0]
                selected_recipients.append(email)

        if not selected_recipients:
            QMessageBox.information(dialog, "선택 없음", "추가할 수신자를 선택하세요.")
            return

        # 선택된 수신자들을 목록에 추가
        for recipient in selected_recipients:
            self.recipients_list_widget.addItem(recipient)

        QMessageBox.information(dialog, "추가 완료", f"{len(selected_recipients)}명의 수신자가 추가되었습니다.")
        dialog.accept()

    def add_recipient_to_list(self):
        """수신자 목록에 추가"""
        email = self.recipient_edit.text().strip()
        if not email:
            return

        if "@" not in email:
            QMessageBox.warning(self, "이메일 오류", "올바른 이메일 주소를 입력하세요.")
            return

        # 중복 확인
        current_recipients = self.get_current_recipients()
        if email in current_recipients:
            QMessageBox.warning(self, "중복", "이미 추가된 수신자입니다.")
            return

        self.recipients_list_widget.addItem(email)
        self.recipient_edit.clear()

    def remove_recipient_from_list(self):
        """선택한 수신자 삭제"""
        current_item = self.recipients_list_widget.currentItem()
        if current_item:
            row = self.recipients_list_widget.row(current_item)
            self.recipients_list_widget.takeItem(row)
        else:
            QMessageBox.information(self, "선택 없음", "삭제할 수신자를 선택하세요.")

    def get_current_recipients(self):
        """현재 수신자 목록 반환"""
        recipients = []
        for i in range(self.recipients_list_widget.count()):
            recipients.append(self.recipients_list_widget.item(i).text())
        return recipients

    def add_schedule(self):
        """새 예약 추가"""
        try:
            # 입력 검증
            name = self.name_edit.text().strip()
            subject = self.subject_edit.text().strip()
            recipients = self.get_current_recipients()

            if not name or not subject:
                QMessageBox.warning(self, "입력 오류", "이름과 제목을 입력하세요.")
                return

            if not recipients:
                QMessageBox.warning(self, "수신자 오류", "수신자를 최소 1명 추가하세요.")
                return

            # 내용 타입 수집
            content_types = []
            if self.all_check.isChecked(): content_types.append("all")
            if self.done_check.isChecked(): content_types.append("completed")
            if self.todo_check.isChecked(): content_types.append("incomplete")

            if not content_types:
                QMessageBox.warning(self, "내용 오류", "포함할 내용을 최소 1개 선택하세요.")
                return

            # 카테고리 선택 확인
            selected_categories = self.get_selected_categories()
            if selected_categories is not None and len(selected_categories) == 0:
                QMessageBox.warning(self, "카테고리 오류", "최소 1개의 카테고리를 선택하세요.")
                return

            # 예약 데이터 생성
            schedule = {
                "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "name": name,
                "custom_title": subject,
                "recipients": recipients,
                "content_types": content_types,
                "period": self.period_combo.currentText(),
                "send_time": self.time_edit.time().toString("HH:mm"),
                "enabled": True,
                "created_at": datetime.now().isoformat(),
                "last_sent_date": None,
                "last_sent_time": None,
                "total_sent_count": 0,
                "selected_categories": selected_categories,
                "include_important_tasks": self.include_important_check.isChecked()  # 중요 일정 포함 여부 추가
            }

            # 발송 타입에 따라 설정
            if self.once_radio.isChecked():
                schedule["is_recurring"] = False
                schedule["send_date"] = self.date_edit.date().toString("yyyy-MM-dd")
            elif self.daily_radio.isChecked():
                schedule["is_recurring"] = True
                schedule["frequency"] = "daily"
            elif self.weekly_radio.isChecked():
                schedule["is_recurring"] = True
                schedule["frequency"] = "weekly"
                # 요일 정보 추가
                weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                selected_weekday = weekdays[self.weekday_combo.currentIndex()]
                schedule["weekday"] = selected_weekday

            # 저장
            self.email_schedules.append(schedule)
            self.save_email_schedules()
            self.load_schedule_list()
            self.clear_inputs()

            QMessageBox.information(self, "성공", f"'{name}' 예약이 추가되었습니다!")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"예약 추가 실패:\n{e}")

    def clear_inputs(self):
        """입력 필드 초기화"""
        self.name_edit.clear()
        self.subject_edit.clear()
        self.recipients_list_widget.clear()
        self.recipient_edit.clear()
        self.once_radio.setChecked(True)
        self.include_important_check.setChecked(True)  # 중요 일정 포함 기본값

        # 카테고리 선택 초기화
        self.all_categories_check.setChecked(True)
        for check in self.category_checks.values():
            check.setChecked(True)

        self.on_type_changed()

    def load_schedule_list(self):
        """예약 목록 로드"""
        self.schedule_list.clear()

        for schedule in self.email_schedules:
            # 표시 텍스트 생성
            name = schedule.get("name", "이름없음")
            enabled = "✅" if schedule.get("enabled", True) else "⏸️"

            if schedule.get("is_recurring", False):
                freq_map = {"daily": "매일", "weekly": "매주"}
                freq = freq_map.get(schedule.get("frequency", "daily"), "매일")
                time_info = f"{freq} {schedule.get('send_time', '09:00')}"

                # 매주인 경우 요일 추가
                if schedule.get("frequency") == "weekly" and schedule.get("weekday"):
                    weekday_map = {
                        "monday": "월", "tuesday": "화", "wednesday": "수",
                        "thursday": "목", "friday": "금", "saturday": "토", "sunday": "일"
                    }
                    weekday_kr = weekday_map.get(schedule.get("weekday"), "월")
                    time_info = f"매주 {weekday_kr}요일 {schedule.get('send_time', '09:00')}"

                type_icon = "🔄"
            else:
                date = schedule.get("send_date", "날짜미정")
                time = schedule.get("send_time", "09:00")
                time_info = f"{date} {time}"
                type_icon = "📧"

            # 카테고리 필터 정보 추가
            category_info = ""
            selected_categories = schedule.get("selected_categories")
            if selected_categories is not None and len(selected_categories) > 0:
                if len(selected_categories) <= 2:
                    category_info = f" [카테고리: {', '.join(selected_categories)}]"
                else:
                    category_info = f" [카테고리: {', '.join(selected_categories[:2])} 외 {len(selected_categories) - 2}개]"

            # 중요 일정 포함 표시 추가
            important_info = ""
            if schedule.get("include_important_tasks", False):
                important_info = " 📌"

            # 발송 이력 정보 추가 - 개선된 표시
            last_sent_info = ""
            last_sent_date = schedule.get("last_sent_date")
            last_sent_time = schedule.get("last_sent_time")
            total_sent = schedule.get("total_sent_count", 0)

            if last_sent_date and last_sent_time:
                last_sent_info = f"\n최근발송: {last_sent_date} {last_sent_time}"
                if total_sent > 1:
                    last_sent_info += f" | 총 {total_sent}회"
            elif total_sent > 0:
                last_sent_info = f"\n총 발송: {total_sent}회"

            display_text = f"{enabled} {type_icon} {name} | {time_info}{category_info}{important_info}{last_sent_info}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, schedule)
            self.schedule_list.addItem(item)

    def send_now(self):
        """선택한 예약 즉시 발송"""
        current_item = self.schedule_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택없음", "발송할 예약을 선택하세요.")
            return

        schedule = current_item.data(Qt.ItemDataRole.UserRole)
        if self.send_email(schedule):
            # 발송 성공 시 발송 이력 업데이트
            self.update_schedule_send_history(schedule)
            QMessageBox.information(self, "발송완료", f"'{schedule['name']}' 메일을 발송했습니다!")

    def update_schedule_send_history(self, schedule):
        """예약 발송 이력 업데이트"""
        try:
            current_time = datetime.now()
            schedule_id = schedule["id"]

            # 해당 스케줄 찾아서 업데이트
            for s in self.email_schedules:
                if s["id"] == schedule_id:
                    s["last_sent_date"] = current_time.strftime("%Y-%m-%d")
                    s["last_sent_time"] = current_time.strftime("%H:%M")
                    s["total_sent_count"] = s.get("total_sent_count", 0) + 1
                    print(
                        f"예약 '{s['name']}' 발송 이력 업데이트: {s['last_sent_date']} {s['last_sent_time']} (총 {s['total_sent_count']}회)")
                    break

            # 저장하고 목록 새로고침
            self.save_email_schedules()
            self.load_schedule_list()

        except Exception as e:
            print(f"예약 발송 이력 업데이트 중 오류: {e}")

    def check_auto_send(self):
        """자동 발송 체크 (1분마다 실행)"""
        try:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M")
            current_weekday = now.weekday()

            for schedule in self.email_schedules:
                if not schedule.get("enabled", True):
                    continue

                if schedule.get("send_time") != current_time:
                    continue

                if schedule.get("last_sent_date") == current_date:
                    continue

                should_send = False

                if schedule.get("is_recurring", False):
                    freq = schedule.get("frequency", "daily")
                    if freq == "daily":
                        should_send = True
                    elif freq == "weekly":
                        # 매주 발송: 지정된 요일인지 확인
                        schedule_weekday = schedule.get("weekday", "monday")
                        weekday_map = {
                            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                            "friday": 4, "saturday": 5, "sunday": 6
                        }
                        target_weekday = weekday_map.get(schedule_weekday, 0)
                        if current_weekday == target_weekday:
                            should_send = True
                else:
                    if schedule.get("send_date") == current_date:
                        should_send = True

                if should_send:
                    if self.send_email(schedule):
                        # 발송 이력 업데이트
                        schedule["last_sent_date"] = current_date
                        schedule["last_sent_time"] = current_time
                        schedule["total_sent_count"] = schedule.get("total_sent_count", 0) + 1

                        if not schedule.get("is_recurring", False):
                            schedule["enabled"] = False

                        self.save_email_schedules()
                        self.load_schedule_list()
                        print(f"자동 발송 완료: {schedule['name']} (총 {schedule['total_sent_count']}회)")

        except Exception as e:
            print(f"자동 발송 체크 오류: {e}")

    def on_schedule_clicked(self, item):
        """예약 선택시"""
        pass

    def delete_schedule(self):
        """선택한 예약 삭제"""
        current_item = self.schedule_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택없음", "삭제할 예약을 선택하세요.")
            return

        schedule = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "삭제확인", f"'{schedule['name']}' 예약을 삭제하시겠습니까?")

        if reply == QMessageBox.StandardButton.Yes:
            self.email_schedules = [s for s in self.email_schedules if s["id"] != schedule["id"]]
            self.save_email_schedules()
            self.load_schedule_list()
            QMessageBox.information(self, "삭제완료", "예약이 삭제되었습니다.")

    def toggle_schedule(self):
        """선택한 예약 활성화/비활성화"""
        current_item = self.schedule_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택없음", "변경할 예약을 선택하세요.")
            return

        schedule = current_item.data(Qt.ItemDataRole.UserRole)
        schedule_id = schedule["id"]

        # 상태 토글
        for s in self.email_schedules:
            if s["id"] == schedule_id:
                s["enabled"] = not s.get("enabled", True)
                break

        self.save_email_schedules()
        self.load_schedule_list()

    def test_send(self):
        """테스트 메일 발송"""
        recipients = self.get_current_recipients()
        if not recipients:
            QMessageBox.warning(self, "수신자 오류", "테스트할 수신자를 추가하세요.")
            return

        # 카테고리 필터 확인
        selected_categories = self.get_selected_categories()
        if selected_categories is not None and len(selected_categories) == 0:
            QMessageBox.warning(self, "카테고리 오류", "최소 1개의 카테고리를 선택하세요.")
            return

        temp_schedule = {
            "custom_title": self.subject_edit.text().strip() or "테스트",
            "recipients": recipients,
            "content_types": ["all"],
            "period": "오늘",
            "selected_categories": selected_categories,
            "include_important_tasks": self.include_important_check.isChecked()  # 중요 일정 포함 여부 추가
        }

        if self.send_email(temp_schedule, is_test=True):
            QMessageBox.information(self, "테스트완료", f"{len(recipients)}명에게 테스트 메일을 발송했습니다!")

    def send_email(self, schedule, is_test=False):
        """실제 메일 발송"""
        try:
            from utils.email_sender import EmailSender

            sender = EmailSender(self.storage_manager)
            available, error_msg = sender.check_availability()

            if not available:
                if is_test:
                    QMessageBox.critical(self, "메일 불가", error_msg)
                return False

            return sender.send_scheduled_email(schedule, is_test=is_test)

        except Exception as e:
            if is_test:
                QMessageBox.critical(self, "발송 실패", f"메일 발송 실패:\n{e}")
            print(f"메일 발송 오류: {e}")
            return False

    def load_email_schedules(self):
        """예약 데이터 로드"""
        try:
            file_path = "data/email_schedules.json"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    schedules = json.load(f)

                # 기존 예약에 중요 일정 포함 필드가 없으면 기본값으로 추가
                for schedule in schedules:
                    if "last_sent_date" not in schedule:
                        schedule["last_sent_date"] = None
                    if "last_sent_time" not in schedule:
                        schedule["last_sent_time"] = None
                    if "total_sent_count" not in schedule:
                        schedule["total_sent_count"] = 0
                    if "include_important_tasks" not in schedule:
                        schedule["include_important_tasks"] = True  # 기존 예약은 기본값으로 포함

                return schedules
        except Exception as e:
            print(f"예약 로드 오류: {e}")
        return []

    def save_email_schedules(self):
        """예약 데이터 저장"""
        try:
            os.makedirs("data", exist_ok=True)
            file_path = "data/email_schedules.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.email_schedules, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"예약 저장 오류: {e}")

    def closeEvent(self, event):
        """창 닫기 시 타이머 정리"""
        if hasattr(self, 'auto_timer'):
            self.auto_timer.stop()
        event.accept()