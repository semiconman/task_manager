#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QComboBox,
    QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox,
    QFrame, QWidget, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class EmailSettingsDialog(QDialog):
    """메일 발송 설정 대화상자 (간소화 버전)"""

    def __init__(self, storage_manager):
        super().__init__()

        self.storage_manager = storage_manager
        self.email_settings = self.load_email_settings()

        self.setWindowTitle("메일 발송 설정")
        self.setMinimumSize(700, 500)
        self.setMaximumSize(900, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 탭 1: 기본 설정
        self.create_basic_settings_tab()

        # 탭 2: 수신자 관리
        self.create_recipients_tab()

        # 하단 버튼들
        bottom_layout = QHBoxLayout()

        # 테스트 메일 발송 버튼
        test_btn = QPushButton("테스트 메일 발송")
        test_btn.clicked.connect(self.send_test_email)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
        """)
        bottom_layout.addWidget(test_btn)
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

        # 확인/취소 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("저장")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 초기 제목 미리보기 업데이트
        self.update_title_preview()

    def create_basic_settings_tab(self):
        """기본 설정 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # 1. 메일 제목 설정
        title_group = QGroupBox("메일 제목 설정")
        title_layout = QVBoxLayout(title_group)

        title_info = QLabel("형식: [날짜] + Todolist + [사용자 지정 문구]")
        title_info.setStyleSheet("color: #666666; font-size: 11px;")
        title_layout.addWidget(title_info)

        title_example = QLabel("예시: 2025-07-03 Todolist 업무현황보고")
        title_example.setStyleSheet("color: #4285F4; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_example)

        custom_title_layout = QHBoxLayout()
        custom_title_layout.addWidget(QLabel("사용자 지정 문구:"))
        self.custom_title_edit = QLineEdit()
        self.custom_title_edit.setPlaceholderText("예: 업무현황보고")
        self.custom_title_edit.textChanged.connect(self.update_title_preview)
        custom_title_layout.addWidget(self.custom_title_edit)
        title_layout.addLayout(custom_title_layout)

        # 제목 미리보기
        self.title_preview = QLabel("")
        self.title_preview.setStyleSheet(
            "background-color: #F5F5F5; padding: 8px; border-radius: 4px; margin-top: 5px;")
        title_layout.addWidget(self.title_preview)

        layout.addWidget(title_group)

        # 2. 메일 내용 설정
        content_group = QGroupBox("메일 내용 설정")
        content_layout = QVBoxLayout(content_group)

        # 가로 배치로 변경
        content_main_layout = QHBoxLayout()

        # 왼쪽: 내용 타입 선택
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("포함할 내용:"))

        self.content_checkboxes = {}
        content_types = {
            "all": "전체 일정",
            "completed": "완료 일정",
            "incomplete": "미완료 일정"
        }

        for key, label in content_types.items():
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            self.content_checkboxes[key] = checkbox
            left_layout.addWidget(checkbox)

        content_main_layout.addLayout(left_layout)

        # 오른쪽: 기간 선택
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("기간 선택:"))

        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "오늘",
            "이번 주",
            "저번 주",
            "이번 달",
            "저번 달"
        ])
        self.period_combo.setCurrentText("오늘")
        right_layout.addWidget(self.period_combo)
        right_layout.addStretch()

        content_main_layout.addLayout(right_layout)
        content_layout.addLayout(content_main_layout)
        layout.addWidget(content_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📋 기본 설정")

    def create_recipients_tab(self):
        """수신자 관리 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # 수신자 추가 영역
        add_group = QGroupBox("수신자 추가")
        add_layout = QVBoxLayout(add_group)

        add_recipient_layout = QHBoxLayout()
        add_recipient_layout.addWidget(QLabel("이메일 주소:"))

        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("example@company.com")
        add_recipient_layout.addWidget(self.recipient_edit)

        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self.add_recipient)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_recipient_layout.addWidget(add_btn)

        add_layout.addLayout(add_recipient_layout)
        layout.addWidget(add_group)

        # 수신자 목록
        list_group = QGroupBox("수신자 목록")
        list_layout = QVBoxLayout(list_group)

        self.recipients_list = QListWidget()
        self.recipients_list.setMinimumHeight(150)
        list_layout.addWidget(self.recipients_list)

        # 수신자 삭제 버튼
        remove_btn = QPushButton("선택한 수신자 삭제")
        remove_btn.clicked.connect(self.remove_recipient)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        list_layout.addWidget(remove_btn)

        layout.addWidget(list_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "📧 수신자")

    def update_title_preview(self):
        """제목 미리보기 업데이트"""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        custom_text = self.custom_title_edit.text().strip()

        if custom_text:
            preview = f"{today} Todolist {custom_text}"
        else:
            preview = f"{today} Todolist"

        self.title_preview.setText(f"미리보기: {preview}")

    def add_recipient(self):
        """수신자 추가"""
        email = self.recipient_edit.text().strip()
        if not email:
            QMessageBox.warning(self, "입력 오류", "이메일 주소를 입력하세요.")
            return

        # 간단한 이메일 형식 검증
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "형식 오류", "올바른 이메일 주소 형식이 아닙니다.")
            return

        # 중복 확인
        for i in range(self.recipients_list.count()):
            if self.recipients_list.item(i).text() == email:
                QMessageBox.warning(self, "중복 오류", "이미 추가된 이메일 주소입니다.")
                return

        # 수신자 추가
        self.recipients_list.addItem(email)
        self.recipient_edit.clear()

    def remove_recipient(self):
        """선택한 수신자 삭제"""
        current_item = self.recipients_list.currentItem()
        if current_item:
            row = self.recipients_list.row(current_item)
            self.recipients_list.takeItem(row)
        else:
            QMessageBox.information(self, "선택 없음", "삭제할 수신자를 선택하세요.")

    def send_test_email(self):
        """테스트 메일 발송"""
        try:
            from utils.email_sender import EmailSender

            # 현재 설정으로 테스트 메일 생성
            sender = EmailSender(self.storage_manager)

            # 메일 기능 사용 가능 여부 확인
            available, error_msg = sender.check_availability()
            if not available:
                QMessageBox.critical(self, "메일 기능 사용 불가", error_msg)
                return

            # 수신자 확인
            recipients = []
            for i in range(self.recipients_list.count()):
                recipients.append(self.recipients_list.item(i).text())

            if not recipients:
                QMessageBox.warning(self, "수신자 없음", "테스트 메일을 보낼 수신자를 추가하세요.")
                return

            # 현재 설정 수집
            settings = self.collect_current_settings()

            # 테스트 메일 발송
            success = sender.send_scheduled_email(settings, is_test=True)

            if success:
                QMessageBox.information(self, "발송 완료", "테스트 메일이 성공적으로 발송되었습니다.")
            else:
                QMessageBox.critical(self, "발송 실패", "테스트 메일 발송에 실패했습니다.\n\nOutlook이 실행 중인지 확인하세요.")

        except Exception as e:
            print(f"테스트 메일 발송 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"테스트 메일 발송 중 오류가 발생했습니다:\n{e}")

    def load_current_settings(self):
        """현재 설정을 UI에 로드"""
        try:
            # 사용자 지정 문구
            self.custom_title_edit.setText(self.email_settings.get("custom_title", ""))

            # 내용 타입
            content_types = self.email_settings.get("content_types", ["all"])
            for key, checkbox in self.content_checkboxes.items():
                checkbox.setChecked(key in content_types)

            # 기간
            period = self.email_settings.get("period", "오늘")
            index = self.period_combo.findText(period)
            if index >= 0:
                self.period_combo.setCurrentIndex(index)

            # 수신자 목록
            recipients = self.email_settings.get("recipients", [])
            for recipient in recipients:
                self.recipients_list.addItem(recipient)

        except Exception as e:
            print(f"설정 로드 중 오류: {e}")

    def collect_current_settings(self):
        """현재 UI 설정 수집"""
        # 내용 타입 수집
        content_types = []
        for key, checkbox in self.content_checkboxes.items():
            if checkbox.isChecked():
                content_types.append(key)

        # 수신자 수집
        recipients = []
        for i in range(self.recipients_list.count()):
            recipients.append(self.recipients_list.item(i).text())

        return {
            "custom_title": self.custom_title_edit.text().strip(),
            "content_types": content_types,
            "period": self.period_combo.currentText(),
            "recipients": recipients
        }

    def save_settings(self):
        """설정 저장"""
        try:
            # 유효성 검사
            if not self.custom_title_edit.text().strip():
                QMessageBox.warning(self, "입력 오류", "사용자 지정 문구를 입력하세요.")
                return

            # 내용 타입 확인
            content_selected = any(cb.isChecked() for cb in self.content_checkboxes.values())
            if not content_selected:
                QMessageBox.warning(self, "선택 오류", "포함할 내용을 최소 하나 이상 선택하세요.")
                return

            # 설정 수집 및 저장
            settings = self.collect_current_settings()
            self.save_email_settings(settings)

            QMessageBox.information(self, "저장 완료", "메일 설정이 저장되었습니다.")
            self.accept()

        except Exception as e:
            print(f"설정 저장 중 오류: {e}")
            QMessageBox.critical(self, "저장 실패", f"설정 저장 중 오류가 발생했습니다:\n{e}")

    def load_email_settings(self):
        """메일 설정 로드"""
        try:
            settings_file = "data/email_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"메일 설정 로드 중 오류: {e}")

        # 기본 설정 반환
        return {
            "custom_title": "업무현황보고",
            "content_types": ["all", "completed", "incomplete"],
            "period": "오늘",
            "recipients": []
        }

    def save_email_settings(self, settings):
        """메일 설정 저장"""
        try:
            os.makedirs("data", exist_ok=True)
            settings_file = "data/email_settings.json"

            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)

            print("메일 설정 저장 완료")
        except Exception as e:
            print(f"메일 설정 저장 중 오류: {e}")

    def accept(self):
        """대화상자 확인"""
        super().accept()