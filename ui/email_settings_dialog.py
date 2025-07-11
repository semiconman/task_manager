#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QComboBox, QTimeEdit,
    QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox,
    QFrame, QWidget, QTabWidget, QButtonGroup, QRadioButton,
    QTextEdit, QSpinBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTime, QDate, QTimer
from PyQt6.QtGui import QFont


class AddressBookSelectionDialog(QDialog):
    """주소록 선택 대화상자"""

    def __init__(self, address_book, selected_emails=None):
        super().__init__()
        self.address_book = address_book
        self.selected_emails = selected_emails or []

        self.setWindowTitle("주소록에서 선택")
        self.setMinimumSize(450, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 안내 메시지
        info_label = QLabel("주소록에서 수신자를 선택하세요:")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # 주소록 목록
        self.address_list = QListWidget()
        self.address_list.setMinimumHeight(250)
        layout.addWidget(self.address_list)

        # 주소록 로드
        self.load_address_book()

        # 전체 선택/해제 버튼
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("전체 선택")
        select_all_btn.clicked.connect(self.select_all)
        select_all_btn.setStyleSheet("background: #28a745; color: white; padding: 6px 12px; border-radius: 3px;")

        select_none_btn = QPushButton("전체 해제")
        select_none_btn.clicked.connect(self.select_none)
        select_none_btn.setStyleSheet("background: #6c757d; color: white; padding: 6px 12px; border-radius: 3px;")

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(select_none_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 확인/취소 버튼
        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.button(QDialogButtonBox.StandardButton.Ok).setText("선택 완료")
        dialog_buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        layout.addWidget(dialog_buttons)

    def load_address_book(self):
        """주소록 로드"""
        for email in self.address_book:
            item = QListWidgetItem(email)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

            # 기존 선택된 이메일이면 체크
            if email in self.selected_emails:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

            self.address_list.addItem(item)

    def select_all(self):
        """전체 선택"""
        for i in range(self.address_list.count()):
            item = self.address_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)

    def select_none(self):
        """전체 해제"""
        for i in range(self.address_list.count()):
            item = self.address_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

    def get_selected_emails(self):
        """선택된 이메일 목록 반환"""
        selected = []
        for i in range(self.address_list.count()):
            item = self.address_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected


class EmailSettingsDialog(QDialog):
    """메일 발송 설정 대화상자 - 주소록 관리 + 데일리 리포트 루틴"""

    def __init__(self, storage_manager):
        super().__init__()

        self.storage_manager = storage_manager
        self.email_settings = self.load_email_settings()
        self.daily_routines = self.load_daily_routines()

        self.setWindowTitle("메일 발송 설정")
        self.setMinimumSize(800, 650)  # 크기 증가
        self.setMaximumSize(1000, 750)  # 최대 크기도 증가
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 탭 1: 주소록 관리
        self.create_address_book_tab()

        # 탭 2: 데일리 리포트 루틴 (스크롤 가능)
        self.create_daily_routine_tab()

        # 확인/취소 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("저장")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        button_box.accepted.connect(self.save_all_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_address_book_tab(self):
        """주소록 관리 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # 제목
        title_label = QLabel("📧 주소록 관리")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #333;")
        layout.addWidget(title_label)

        # 설명
        desc_label = QLabel("메일 발송 기능에서 사용할 주소록을 관리합니다.")
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # 주소 추가 영역
        add_group = QGroupBox("주소 추가")
        add_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        add_layout = QVBoxLayout(add_group)

        add_recipient_layout = QHBoxLayout()
        add_recipient_layout.addWidget(QLabel("이메일 주소:"))

        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("example@company.com")
        self.recipient_edit.returnPressed.connect(self.add_recipient)
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

        # 주소록 목록
        list_group = QGroupBox("주소록")
        list_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        list_layout = QVBoxLayout(list_group)

        self.recipients_list = QListWidget()
        self.recipients_list.setMinimumHeight(250)
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

        # 주소록 관리 버튼들
        button_layout = QHBoxLayout()

        remove_btn = QPushButton("선택한 주소 삭제")
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

        self.tab_widget.addTab(tab, "📧 주소록")

    def create_daily_routine_tab(self):
        """데일리 리포트 루틴 탭 생성 (스크롤 가능)"""
        # 메인 탭 위젯
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 스크롤 컨텐츠 위젯
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # 제목
        title_label = QLabel("🔄 데일리 리포트 루틴")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #333;")
        layout.addWidget(title_label)

        # 설명
        desc_label = QLabel("정해진 시간에 자동으로 데일리 리포트를 발송하는 루틴을 설정합니다.")
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc_label)

        # 좌우 분할
        main_layout = QHBoxLayout()

        # 왼쪽: 루틴 목록
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_frame.setMaximumWidth(300)  # 왼쪽 영역 너비 제한
        left_layout = QVBoxLayout(left_frame)

        routine_list_label = QLabel("📋 등록된 루틴")
        routine_list_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        left_layout.addWidget(routine_list_label)

        self.routine_list = QListWidget()
        self.routine_list.setMinimumHeight(180)
        self.routine_list.setMaximumHeight(220)
        self.routine_list.itemClicked.connect(self.on_routine_selected)
        left_layout.addWidget(self.routine_list)

        # 루틴 관리 버튼
        routine_btn_layout = QVBoxLayout()  # 세로 배치로 변경

        self.edit_routine_btn = QPushButton("수정")
        self.edit_routine_btn.clicked.connect(self.edit_routine)
        self.edit_routine_btn.setEnabled(False)
        self.edit_routine_btn.setStyleSheet("background: #ffc107; color: black; padding: 6px; border-radius: 3px;")

        self.delete_routine_btn = QPushButton("삭제")
        self.delete_routine_btn.clicked.connect(self.delete_routine)
        self.delete_routine_btn.setEnabled(False)
        self.delete_routine_btn.setStyleSheet("background: #dc3545; color: white; padding: 6px; border-radius: 3px;")

        self.toggle_routine_btn = QPushButton("ON/OFF")
        self.toggle_routine_btn.clicked.connect(self.toggle_routine)
        self.toggle_routine_btn.setEnabled(False)
        self.toggle_routine_btn.setStyleSheet("background: #6c757d; color: white; padding: 6px; border-radius: 3px;")

        routine_btn_layout.addWidget(self.edit_routine_btn)
        routine_btn_layout.addWidget(self.delete_routine_btn)
        routine_btn_layout.addWidget(self.toggle_routine_btn)
        left_layout.addLayout(routine_btn_layout)

        main_layout.addWidget(left_frame)

        # 오른쪽: 새 루틴 추가/편집
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)

        add_routine_label = QLabel("➕ 새 루틴 추가")
        add_routine_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(add_routine_label)

        # 기본 정보 (2열 배치)
        basic_info_layout = QHBoxLayout()

        # 첫 번째 열
        col1_layout = QVBoxLayout()

        # 루틴 이름
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("이름:"))
        self.routine_name_edit = QLineEdit()
        self.routine_name_edit.setPlaceholderText("예: 퇴근전 확인할용도")
        name_layout.addWidget(self.routine_name_edit)
        col1_layout.addLayout(name_layout)

        # 발송 시간
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("시간:"))
        self.routine_time_edit = QTimeEdit()
        self.routine_time_edit.setTime(QTime(18, 0))
        self.routine_time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.routine_time_edit)
        col1_layout.addLayout(time_layout)

        basic_info_layout.addLayout(col1_layout)

        # 두 번째 열
        col2_layout = QVBoxLayout()

        # 메일 제목
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("제목:"))
        self.routine_subject_edit = QLineEdit()
        self.routine_subject_edit.setPlaceholderText("예: 일일 업무 현황")
        subject_layout.addWidget(self.routine_subject_edit)
        col2_layout.addLayout(subject_layout)

        basic_info_layout.addLayout(col2_layout)
        right_layout.addLayout(basic_info_layout)

        # 발송 요일 (컴팩트하게)
        weekday_group = QGroupBox("발송 요일")
        weekday_layout = QVBoxLayout(weekday_group)
        weekday_group.setMaximumHeight(100)

        # 요일 체크박스들 (한 줄에)
        self.weekday_checks = {}
        weekdays = [
            ("monday", "월"), ("tuesday", "화"), ("wednesday", "수"),
            ("thursday", "목"), ("friday", "금"), ("saturday", "토"), ("sunday", "일")
        ]

        weekday_grid = QHBoxLayout()
        for day_code, day_name in weekdays:
            check = QCheckBox(day_name)
            self.weekday_checks[day_code] = check
            weekday_grid.addWidget(check)

        weekday_layout.addLayout(weekday_grid)

        # 평일/주말 선택 버튼 (작게)
        weekday_preset_layout = QHBoxLayout()

        weekdays_btn = QPushButton("평일")
        weekdays_btn.clicked.connect(self.select_weekdays)
        weekdays_btn.setStyleSheet(
            "background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;")

        weekend_btn = QPushButton("주말")
        weekend_btn.clicked.connect(self.select_weekend)
        weekend_btn.setStyleSheet(
            "background: #6f42c1; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;")

        all_days_btn = QPushButton("매일")
        all_days_btn.clicked.connect(self.select_all_days)
        all_days_btn.setStyleSheet(
            "background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;")

        clear_days_btn = QPushButton("해제")
        clear_days_btn.clicked.connect(self.clear_all_days)
        clear_days_btn.setStyleSheet(
            "background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;")

        weekday_preset_layout.addWidget(weekdays_btn)
        weekday_preset_layout.addWidget(weekend_btn)
        weekday_preset_layout.addWidget(all_days_btn)
        weekday_preset_layout.addWidget(clear_days_btn)
        weekday_preset_layout.addStretch()

        weekday_layout.addLayout(weekday_preset_layout)
        right_layout.addWidget(weekday_group)

        # 포함 내용 + 수신자 (2열 배치)
        content_recipient_layout = QHBoxLayout()

        # 포함 내용
        content_group = QGroupBox("포함 내용")
        content_layout = QVBoxLayout(content_group)
        content_group.setMaximumHeight(80)

        content_check_layout = QHBoxLayout()
        self.routine_all_check = QCheckBox("전체")
        self.routine_all_check.setChecked(True)
        self.routine_completed_check = QCheckBox("완료")
        self.routine_incomplete_check = QCheckBox("미완료")

        content_check_layout.addWidget(self.routine_all_check)
        content_check_layout.addWidget(self.routine_completed_check)
        content_check_layout.addWidget(self.routine_incomplete_check)
        content_layout.addLayout(content_check_layout)

        content_recipient_layout.addWidget(content_group)

        # 수신자 선택
        recipient_group = QGroupBox("수신자")
        recipient_layout = QVBoxLayout(recipient_group)

        # 주소록에서 선택 버튼
        select_from_address_btn = QPushButton("📋 주소록에서 선택")
        select_from_address_btn.clicked.connect(self.select_recipients_from_address_book)
        select_from_address_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        recipient_layout.addWidget(select_from_address_btn)

        # 선택된 수신자 표시
        self.selected_recipients_label = QLabel("선택된 수신자: 없음")
        self.selected_recipients_label.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        recipient_layout.addWidget(self.selected_recipients_label)

        content_recipient_layout.addWidget(recipient_group)
        right_layout.addLayout(content_recipient_layout)

        # 추가 메모 (작게)
        memo_group = QGroupBox("추가 메모 (선택사항)")
        memo_layout = QVBoxLayout(memo_group)
        memo_group.setMaximumHeight(100)

        self.routine_memo_edit = QTextEdit()
        self.routine_memo_edit.setPlaceholderText("루틴 리포트에 포함할 추가 내용...")
        self.routine_memo_edit.setMaximumHeight(60)
        memo_layout.addWidget(self.routine_memo_edit)

        right_layout.addWidget(memo_group)

        # 루틴 추가/수정 버튼
        routine_action_layout = QHBoxLayout()

        self.add_routine_btn = QPushButton("➕ 루틴 추가")
        self.add_routine_btn.clicked.connect(self.add_routine)
        self.add_routine_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)

        self.update_routine_btn = QPushButton("💾 루틴 수정")
        self.update_routine_btn.clicked.connect(self.update_routine)
        self.update_routine_btn.setVisible(False)
        self.update_routine_btn.setStyleSheet("""
            QPushButton {
                background: #ffc107;
                color: black;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)

        self.cancel_edit_btn = QPushButton("❌ 취소")
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)
        self.cancel_edit_btn.setVisible(False)
        self.cancel_edit_btn.setStyleSheet("background: #6c757d; color: white; padding: 8px 16px; border-radius: 4px;")

        routine_action_layout.addWidget(self.add_routine_btn)
        routine_action_layout.addWidget(self.update_routine_btn)
        routine_action_layout.addWidget(self.cancel_edit_btn)
        routine_action_layout.addStretch()

        right_layout.addLayout(routine_action_layout)

        main_layout.addWidget(right_frame)
        layout.addLayout(main_layout)

        # 스크롤 영역 설정
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)

        self.tab_widget.addTab(tab, "🔄 데일리 루틴")

        # 편집 모드 상태
        self.editing_routine_id = None
        self.selected_routine_recipients = []

    # === 주소록 관리 메서드 ===
    def add_recipient(self):
        """주소록에 추가"""
        email = self.recipient_edit.text().strip()
        if not email:
            return

        if "@" not in email:
            QMessageBox.warning(self, "이메일 오류", "올바른 이메일 주소를 입력하세요.")
            return

        # 중복 확인
        for i in range(self.recipients_list.count()):
            if self.recipients_list.item(i).text() == email:
                QMessageBox.warning(self, "중복 오류", "이미 추가된 이메일 주소입니다.")
                return

        # 주소록에 추가
        item = QListWidgetItem(email)
        item.setToolTip(f"주소: {email}")
        self.recipients_list.addItem(item)
        self.recipient_edit.clear()
        self.recipient_edit.setFocus()

    def remove_recipient(self):
        """선택한 주소 삭제"""
        current_item = self.recipients_list.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self, "주소 삭제",
                f"'{current_item.text()}'를 삭제하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                row = self.recipients_list.row(current_item)
                self.recipients_list.takeItem(row)
        else:
            QMessageBox.information(self, "선택 없음", "삭제할 주소를 선택하세요.")

    def clear_all_recipients(self):
        """모든 주소 삭제"""
        if self.recipients_list.count() == 0:
            QMessageBox.information(self, "목록 없음", "삭제할 주소가 없습니다.")
            return

        reply = QMessageBox.question(
            self, "전체 삭제",
            f"모든 주소({self.recipients_list.count()}개)를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.recipients_list.clear()

    def send_test_email(self):
        """테스트 메일 발송"""
        try:
            from utils.email_sender import EmailSender

            # 주소록 확인
            recipients = []
            for i in range(self.recipients_list.count()):
                recipients.append(self.recipients_list.item(i).text())

            if not recipients:
                QMessageBox.warning(self, "주소록 없음", "테스트 메일을 보낼 주소가 없습니다.\n먼저 주소록에 이메일을 추가하세요.")
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

    # === 데일리 루틴 관리 메서드 ===
    def select_recipients_from_address_book(self):
        """주소록에서 수신자 선택"""
        # 현재 주소록 가져오기
        address_book = []
        for i in range(self.recipients_list.count()):
            address_book.append(self.recipients_list.item(i).text())

        if not address_book:
            QMessageBox.warning(self, "주소록 없음", "주소록이 비어있습니다.\n먼저 주소록 탭에서 이메일 주소를 추가하세요.")
            return

        # 주소록 선택 대화상자 열기
        dialog = AddressBookSelectionDialog(address_book, self.selected_routine_recipients)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_routine_recipients = dialog.get_selected_emails()
            self.update_selected_recipients_display()

    def update_selected_recipients_display(self):
        """선택된 수신자 표시 업데이트"""
        count = len(self.selected_routine_recipients)
        if count == 0:
            self.selected_recipients_label.setText("선택된 수신자: 없음")
        elif count <= 3:
            # 3명 이하면 모든 이메일 표시
            emails = ", ".join(self.selected_routine_recipients)
            self.selected_recipients_label.setText(f"선택된 수신자: {emails}")
        else:
            # 3명 초과면 처음 2명만 표시하고 나머지는 개수로
            first_two = ", ".join(self.selected_routine_recipients[:2])
            self.selected_recipients_label.setText(f"선택된 수신자: {first_two} 외 {count - 2}명")

    def select_weekdays(self):
        """평일만 선택"""
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        for day in self.weekday_checks:
            self.weekday_checks[day].setChecked(day in weekdays)

    def select_weekend(self):
        """주말만 선택"""
        weekend = ["saturday", "sunday"]
        for day in self.weekday_checks:
            self.weekday_checks[day].setChecked(day in weekend)

    def select_all_days(self):
        """매일 선택"""
        for check in self.weekday_checks.values():
            check.setChecked(True)

    def clear_all_days(self):
        """전체 요일 해제"""
        for check in self.weekday_checks.values():
            check.setChecked(False)

    def add_routine(self):
        """새 루틴 추가"""
        if not self.validate_routine_inputs():
            return

        try:
            routine_data = self.collect_routine_data()
            routine_data["id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            routine_data["created_at"] = datetime.now().isoformat()
            routine_data["enabled"] = True

            self.daily_routines.append(routine_data)
            self.refresh_routine_list()
            self.clear_routine_form()

            QMessageBox.information(self, "성공", f"루틴 '{routine_data['name']}'이 추가되었습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"루틴 추가 중 오류가 발생했습니다:\n{e}")

    def update_routine(self):
        """루틴 수정"""
        if not self.editing_routine_id or not self.validate_routine_inputs():
            return

        try:
            routine_data = self.collect_routine_data()

            # 기존 루틴 찾아서 업데이트
            for i, routine in enumerate(self.daily_routines):
                if routine["id"] == self.editing_routine_id:
                    routine_data["id"] = self.editing_routine_id
                    routine_data["created_at"] = routine.get("created_at", datetime.now().isoformat())
                    routine_data["enabled"] = routine.get("enabled", True)
                    self.daily_routines[i] = routine_data
                    break

            self.refresh_routine_list()
            self.cancel_edit()

            QMessageBox.information(self, "성공", f"루틴 '{routine_data['name']}'이 수정되었습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"루틴 수정 중 오류가 발생했습니다:\n{e}")

    def edit_routine(self):
        """선택한 루틴 편집"""
        current_item = self.routine_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택 없음", "편집할 루틴을 선택하세요.")
            return

        routine = current_item.data(Qt.ItemDataRole.UserRole)
        self.editing_routine_id = routine["id"]

        # 폼에 데이터 로드
        self.load_routine_to_form(routine)

        # 버튼 상태 변경
        self.add_routine_btn.setVisible(False)
        self.update_routine_btn.setVisible(True)
        self.cancel_edit_btn.setVisible(True)

    def cancel_edit(self):
        """편집 취소"""
        self.editing_routine_id = None
        self.clear_routine_form()

        # 버튼 상태 복원
        self.add_routine_btn.setVisible(True)
        self.update_routine_btn.setVisible(False)
        self.cancel_edit_btn.setVisible(False)

    def delete_routine(self):
        """선택한 루틴 삭제"""
        current_item = self.routine_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택 없음", "삭제할 루틴을 선택하세요.")
            return

        routine = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self, "루틴 삭제",
            f"루틴 '{routine['name']}'을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.daily_routines = [r for r in self.daily_routines if r["id"] != routine["id"]]
            self.refresh_routine_list()
            QMessageBox.information(self, "삭제 완료", "루틴이 삭제되었습니다.")

    def toggle_routine(self):
        """선택한 루틴 활성화/비활성화"""
        current_item = self.routine_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택 없음", "변경할 루틴을 선택하세요.")
            return

        routine = current_item.data(Qt.ItemDataRole.UserRole)

        # 상태 토글
        for r in self.daily_routines:
            if r["id"] == routine["id"]:
                r["enabled"] = not r.get("enabled", True)
                break

        self.refresh_routine_list()

    def on_routine_selected(self, item):
        """루틴 선택 시 버튼 활성화"""
        self.edit_routine_btn.setEnabled(True)
        self.delete_routine_btn.setEnabled(True)
        self.toggle_routine_btn.setEnabled(True)

    def validate_routine_inputs(self):
        """루틴 입력값 검증"""
        if not self.routine_name_edit.text().strip():
            QMessageBox.warning(self, "입력 오류", "루틴 이름을 입력하세요.")
            return False

        if not self.routine_subject_edit.text().strip():
            QMessageBox.warning(self, "입력 오류", "메일 제목을 입력하세요.")
            return False

        # 요일 선택 확인
        selected_weekdays = [day for day, check in self.weekday_checks.items() if check.isChecked()]
        if not selected_weekdays:
            QMessageBox.warning(self, "입력 오류", "발송할 요일을 최소 1개 선택하세요.")
            return False

        # 내용 선택 확인
        if not (
                self.routine_all_check.isChecked() or self.routine_completed_check.isChecked() or self.routine_incomplete_check.isChecked()):
            QMessageBox.warning(self, "입력 오류", "포함할 내용을 최소 1개 선택하세요.")
            return False

        # 수신자 선택 확인
        if not self.selected_routine_recipients:
            QMessageBox.warning(self, "입력 오류", "주소록에서 수신자를 최소 1명 선택하세요.")
            return False

        return True

    def collect_routine_data(self):
        """루틴 폼 데이터 수집"""
        selected_weekdays = [day for day, check in self.weekday_checks.items() if check.isChecked()]

        content_types = []
        if self.routine_all_check.isChecked(): content_types.append("all")
        if self.routine_completed_check.isChecked(): content_types.append("completed")
        if self.routine_incomplete_check.isChecked(): content_types.append("incomplete")

        return {
            "name": self.routine_name_edit.text().strip(),
            "subject": self.routine_subject_edit.text().strip(),
            "send_time": self.routine_time_edit.time().toString("HH:mm"),
            "weekdays": selected_weekdays,
            "content_types": content_types,
            "recipients": self.selected_routine_recipients.copy(),
            "memo": self.routine_memo_edit.toPlainText().strip()
        }

    def load_routine_to_form(self, routine):
        """루틴 데이터를 폼에 로드"""
        self.routine_name_edit.setText(routine.get("name", ""))
        self.routine_subject_edit.setText(routine.get("subject", ""))

        # 시간 설정
        time_str = routine.get("send_time", "18:00")
        time = QTime.fromString(time_str, "HH:mm")
        self.routine_time_edit.setTime(time)

        # 요일 설정
        weekdays = routine.get("weekdays", [])
        for day, check in self.weekday_checks.items():
            check.setChecked(day in weekdays)

        # 내용 설정
        content_types = routine.get("content_types", [])
        self.routine_all_check.setChecked("all" in content_types)
        self.routine_completed_check.setChecked("completed" in content_types)
        self.routine_incomplete_check.setChecked("incomplete" in content_types)

        # 수신자 설정
        self.selected_routine_recipients = routine.get("recipients", []).copy()
        self.update_selected_recipients_display()

        # 메모 설정
        self.routine_memo_edit.setPlainText(routine.get("memo", ""))

    def clear_routine_form(self):
        """루틴 폼 초기화"""
        self.routine_name_edit.clear()
        self.routine_subject_edit.clear()
        self.routine_time_edit.setTime(QTime(18, 0))

        for check in self.weekday_checks.values():
            check.setChecked(False)

        self.routine_all_check.setChecked(True)
        self.routine_completed_check.setChecked(False)
        self.routine_incomplete_check.setChecked(False)

        self.selected_routine_recipients = []
        self.update_selected_recipients_display()
        self.routine_memo_edit.clear()

    def refresh_routine_list(self):
        """루틴 목록 새로고침"""
        self.routine_list.clear()

        for routine in self.daily_routines:
            name = routine.get("name", "이름없음")
            enabled = "✅" if routine.get("enabled", True) else "❌"
            time = routine.get("send_time", "00:00")

            # 요일 정보
            weekdays = routine.get("weekdays", [])
            weekday_names = {
                "monday": "월", "tuesday": "화", "wednesday": "수",
                "thursday": "목", "friday": "금", "saturday": "토", "sunday": "일"
            }
            weekday_str = "/".join([weekday_names.get(day, day) for day in weekdays])

            # 수신자 수
            recipient_count = len(routine.get("recipients", []))

            display_text = f"{enabled} {name}\n{weekday_str} {time} | {recipient_count}명"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, routine)
            self.routine_list.addItem(item)

    # === 데이터 로드/저장 메서드 ===
    def load_current_settings(self):
        """현재 설정을 UI에 로드"""
        try:
            # 주소록
            recipients = self.email_settings.get("recipients", [])
            for recipient in recipients:
                item = QListWidgetItem(recipient)
                item.setToolTip(f"주소: {recipient}")
                self.recipients_list.addItem(item)

            # 루틴 목록 새로고침
            self.refresh_routine_list()

        except Exception as e:
            print(f"설정 로드 중 오류: {e}")

    def save_all_settings(self):
        """모든 설정 저장"""
        try:
            # 주소록 수집
            recipients = []
            for i in range(self.recipients_list.count()):
                recipients.append(self.recipients_list.item(i).text())

            # 이메일 설정 저장
            email_settings = {
                "recipients": recipients,
                "custom_title": "업무현황보고",
                "content_types": ["all", "completed", "incomplete"],
                "period": "오늘"
            }
            self.save_email_settings(email_settings)

            # 데일리 루틴 저장
            self.save_daily_routines()

            QMessageBox.information(
                self, "저장 완료",
                f"설정이 저장되었습니다.\n• 주소록: {len(recipients)}개\n• 등록된 루틴: {len(self.daily_routines)}개"
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

    def load_daily_routines(self):
        """데일리 루틴 설정 로드"""
        try:
            routines_file = "data/daily_routines.json"
            if os.path.exists(routines_file):
                with open(routines_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"데일리 루틴 로드 중 오류: {e}")

        return []

    def save_daily_routines(self):
        """데일리 루틴 설정 저장"""
        try:
            os.makedirs("data", exist_ok=True)
            routines_file = "data/daily_routines.json"

            with open(routines_file, "w", encoding="utf-8") as f:
                json.dump(self.daily_routines, f, ensure_ascii=False, indent=2)

            print("데일리 루틴 저장 완료")
        except Exception as e:
            print(f"데일리 루틴 저장 중 오류: {e}")

    def accept(self):
        """대화상자 확인"""
        super().accept()