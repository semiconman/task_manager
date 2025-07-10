#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QComboBox,
    QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox,
    QFrame, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class EmailSettingsDialog(QDialog):
    """메일 발송 설정 대화상자 - 수신자 관리만 포함"""

    def __init__(self, storage_manager):
        super().__init__()

        self.storage_manager = storage_manager
        self.email_settings = self.load_email_settings()

        self.setWindowTitle("메일 발송 설정")
        self.setMinimumSize(600, 500)
        self.setMaximumSize(800, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 제목
        title_label = QLabel("📧 메일 수신자 관리")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #333;")
        layout.addWidget(title_label)

        # 설명
        desc_label = QLabel("메일 발송 기능에서 사용할 수신자 목록을 관리합니다.")
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # 수신자 추가 영역
        add_group = QGroupBox("수신자 추가")
        add_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        add_layout = QVBoxLayout(add_group)

        add_recipient_layout = QHBoxLayout()
        add_recipient_layout.addWidget(QLabel("이메일 주소:"))

        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("example@company.com")
        self.recipient_edit.returnPressed.connect(self.add_recipient)  # Enter 키로 추가
        add_recipient_layout.addWidget(self.recipient_edit)

        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self.add_recipient)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
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
        list_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        list_layout = QVBoxLayout(list_group)

        self.recipients_list = QListWidget()
        self.recipients_list.setMinimumHeight(200)
        self.recipients_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        list_layout.addWidget(self.recipients_list)

        # 수신자 관리 버튼들
        button_layout = QHBoxLayout()

        remove_btn = QPushButton("선택한 수신자 삭제")
        remove_btn.clicked.connect(self.remove_recipient)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        button_layout.addWidget(remove_btn)

        clear_all_btn = QPushButton("전체 삭제")
        clear_all_btn.clicked.connect(self.clear_all_recipients)
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(clear_all_btn)

        button_layout.addStretch()
        list_layout.addLayout(button_layout)

        layout.addWidget(list_group)

        # 하단 버튼들
        bottom_layout = QHBoxLayout()

        # 테스트 메일 발송 버튼
        test_btn = QPushButton("📧 테스트 메일 발송")
        test_btn.clicked.connect(self.send_test_email)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
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
        item = QListWidgetItem(email)
        item.setToolTip(f"수신자: {email}")
        self.recipients_list.addItem(item)
        self.recipient_edit.clear()
        self.recipient_edit.setFocus()

    def remove_recipient(self):
        """선택한 수신자 삭제"""
        current_item = self.recipients_list.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self, "수신자 삭제",
                f"'{current_item.text()}'를 삭제하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                row = self.recipients_list.row(current_item)
                self.recipients_list.takeItem(row)
        else:
            QMessageBox.information(self, "선택 없음", "삭제할 수신자를 선택하세요.")

    def clear_all_recipients(self):
        """모든 수신자 삭제"""
        if self.recipients_list.count() == 0:
            QMessageBox.information(self, "목록 없음", "삭제할 수신자가 없습니다.")
            return

        reply = QMessageBox.question(
            self, "전체 삭제",
            f"모든 수신자({self.recipients_list.count()}명)를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.recipients_list.clear()

    def send_test_email(self):
        """테스트 메일 발송"""
        try:
            from utils.email_sender import EmailSender

            # 수신자 확인
            recipients = []
            for i in range(self.recipients_list.count()):
                recipients.append(self.recipients_list.item(i).text())

            if not recipients:
                QMessageBox.warning(self, "수신자 없음", "테스트 메일을 보낼 수신자를 먼저 추가하세요.")
                return

            # 메일 기능 사용 가능 여부 확인
            sender = EmailSender(self.storage_manager)
            available, error_msg = sender.check_availability()
            if not available:
                QMessageBox.critical(self, "메일 기능 사용 불가", error_msg)
                return

            # 테스트 설정 생성
            test_settings = {
                "custom_title": "테스트 메일",
                "recipients": recipients,
                "content_types": ["all"],
                "period": "오늘"
            }

            # 테스트 메일 발송
            success = sender.send_scheduled_email(test_settings, is_test=True)

            if success:
                QMessageBox.information(
                    self, "발송 완료",
                    f"테스트 메일이 {len(recipients)}명에게 성공적으로 발송되었습니다."
                )
            else:
                QMessageBox.critical(
                    self, "발송 실패",
                    "테스트 메일 발송에 실패했습니다.\n\nOutlook이 실행 중인지 확인하세요."
                )

        except Exception as e:
            print(f"테스트 메일 발송 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"테스트 메일 발송 중 오류가 발생했습니다:\n{e}")

    def load_current_settings(self):
        """현재 설정을 UI에 로드"""
        try:
            # 수신자 목록
            recipients = self.email_settings.get("recipients", [])
            for recipient in recipients:
                item = QListWidgetItem(recipient)
                item.setToolTip(f"수신자: {recipient}")
                self.recipients_list.addItem(item)

        except Exception as e:
            print(f"설정 로드 중 오류: {e}")

    def collect_current_settings(self):
        """현재 UI 설정 수집"""
        # 수신자 수집
        recipients = []
        for i in range(self.recipients_list.count()):
            recipients.append(self.recipients_list.item(i).text())

        return {
            "recipients": recipients,
            # 기본값들 (메일 관리에서 사용)
            "custom_title": "업무현황보고",
            "content_types": ["all", "completed", "incomplete"],
            "period": "오늘"
        }

    def save_settings(self):
        """설정 저장"""
        try:
            # 수신자 확인
            if self.recipients_list.count() == 0:
                reply = QMessageBox.question(
                    self, "수신자 없음",
                    "수신자가 한 명도 등록되지 않았습니다.\n그래도 저장하시겠습니까?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.No:
                    return

            # 설정 수집 및 저장
            settings = self.collect_current_settings()
            self.save_email_settings(settings)

            QMessageBox.information(
                self, "저장 완료",
                f"메일 설정이 저장되었습니다.\n등록된 수신자: {len(settings['recipients'])}명"
            )
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