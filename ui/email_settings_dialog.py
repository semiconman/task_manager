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
        self.setMinimumSize(800, 700)  # 크기 증가 (중요 일정 포함 체크박스 추가로)
        self.setMaximumSize(1000, 800)  # 최대 크기도 증가
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
        routine_list_label.setStyleSheet("font-weight: bold; margin-bottom: 3px; font-size: 12px;")  # 크기 줄임
        left_layout.addWidget(routine_list_label)

        self.routine_list = QListWidget()
        self.routine_list.setMinimumHeight(280)  # 180 → 280으로 증가
        self.routine_list.setMaximumHeight(320)  # 220 → 320으로 증가
        self.routine_list.itemClicked.connect(self.on_routine_selected)
        left_layout.addWidget(self.routine_list)

        # 루틴 관리 버튼
        routine_btn_layout = QHBoxLayout()  # 가로 배치로 변경

        # 즉시 발송 버튼 추가 (새로운 기능)
        self.send_now_routine_btn = QPushButton("즉시 발송")
        self.send_now_routine_btn.clicked.connect(self.send_routine_now)
        self.send_now_routine_btn.setEnabled(False)
        self.send_now_routine_btn.setStyleSheet(
            "background: #28a745; color: white; padding: 6px; border-radius: 3px; font-size: 11px;")

        self.edit_routine_btn = QPushButton("수정")
        self.edit_routine_btn.clicked.connect(self.edit_routine)
        self.edit_routine_btn.setEnabled(False)
        self.edit_routine_btn.setStyleSheet(
            "background: #ffc107; color: black; padding: 6px; border-radius: 3px; font-size: 11px;")

        self.delete_routine_btn = QPushButton("삭제")
        self.delete_routine_btn.clicked.connect(self.delete_routine)
        self.delete_routine_btn.setEnabled(False)
        self.delete_routine_btn.setStyleSheet(
            "background: #dc3545; color: white; padding: 6px; border-radius: 3px; font-size: 11px;")

        self.toggle_routine_btn = QPushButton("ON/OFF")
        self.toggle_routine_btn.clicked.connect(self.toggle_routine)
        self.toggle_routine_btn.setEnabled(False)
        self.toggle_routine_btn.setStyleSheet(
            "background: #6c757d; color: white; padding: 6px; border-radius: 3px; font-size: 11px;")

        routine_btn_layout.addWidget(self.send_now_routine_btn)
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

        # 카테고리 필터 + 포함 내용 (2열 배치)
        category_content_layout = QHBoxLayout()

        # 카테고리 필터 (새로 추가)
        category_group = QGroupBox("카테고리 필터")
        category_layout = QVBoxLayout(category_group)
        category_group.setMaximumHeight(120)

        # 안내 메시지
        category_info = QLabel("특정 카테고리만 포함")
        category_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        category_layout.addWidget(category_info)

        # 전체 선택 체크박스
        self.routine_all_categories_check = QCheckBox("모든 카테고리")
        self.routine_all_categories_check.setChecked(True)
        self.routine_all_categories_check.stateChanged.connect(self.on_routine_all_categories_changed)
        category_layout.addWidget(self.routine_all_categories_check)

        # 개별 카테고리 체크박스 (2열로 배치)
        self.routine_category_checks = {}
        category_grid_layout = QVBoxLayout()

        row1_layout = QHBoxLayout()
        row2_layout = QHBoxLayout()

        for idx, category in enumerate(self.storage_manager.categories):
            check = QCheckBox(category.name)
            check.setChecked(True)
            check.stateChanged.connect(self.on_routine_category_check_changed)
            check.setStyleSheet(f"color: {category.color}; font-weight: bold; font-size: 10px;")

            self.routine_category_checks[category.name] = check

            # 2열로 배치
            if idx < 2:
                row1_layout.addWidget(check)
            else:
                row2_layout.addWidget(check)

        # 남은 공간 채우기
        row1_layout.addStretch()
        row2_layout.addStretch()

        category_grid_layout.addLayout(row1_layout)
        category_grid_layout.addLayout(row2_layout)
        category_layout.addLayout(category_grid_layout)

        category_content_layout.addWidget(category_group)

        # 포함 내용
        content_group = QGroupBox("포함 내용")
        content_layout = QVBoxLayout(content_group)
        content_group.setMaximumHeight(120)

        content_check_layout = QHBoxLayout()
        self.routine_all_check = QCheckBox("전체")
        self.routine_all_check.setChecked(True)
        self.routine_completed_check = QCheckBox("완료")
        self.routine_incomplete_check = QCheckBox("미완료")

        content_check_layout.addWidget(QLabel("포함:"))
        content_check_layout.addWidget(self.routine_all_check)
        content_check_layout.addWidget(self.routine_completed_check)
        content_check_layout.addWidget(self.routine_incomplete_check)

        # 기간 (첫 번째 줄 이어서)
        self.period_combo = QComboBox()
        self.period_combo.addItems(["오늘", "이번주", "저번주"])
        content_check_layout.addWidget(QLabel("기간:"))
        content_check_layout.addWidget(self.period_combo)
        content_check_layout.addStretch()

        content_layout.addLayout(content_check_layout)

        # 중요 일정 포함 (두 번째 줄) - 새로 추가
        important_row = QHBoxLayout()
        self.routine_include_important_check = QCheckBox("📌 미완료 중요 일정 포함 (지난 30일)")
        self.routine_include_important_check.setChecked(True)  # 기본값: 체크됨
        self.routine_include_important_check.setToolTip("지난 30일간의 다른 날짜 미완료 중요 작업을 별도 섹션으로 포함")
        self.routine_include_important_check.setStyleSheet("font-weight: bold; color: #d32f2f; font-size: 10px;")

        important_row.addWidget(self.routine_include_important_check)
        important_row.addStretch()
        content_layout.addLayout(important_row)

        category_content_layout.addWidget(content_group)
        right_layout.addLayout(category_content_layout)

        # 수신자 + 메모 (2열 배치)
        recipient_memo_layout = QHBoxLayout()

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

        recipient_memo_layout.addWidget(recipient_group)

        # 추가 메모 (작게)
        memo_group = QGroupBox("추가 메모 (선택사항)")
        memo_layout = QVBoxLayout(memo_group)
        memo_group.setMaximumHeight(100)

        self.routine_memo_edit = QTextEdit()
        self.routine_memo_edit.setPlaceholderText("루틴 리포트에 포함할 추가 내용...")
        self.routine_memo_edit.setMaximumHeight(60)
        memo_layout.addWidget(self.routine_memo_edit)

        recipient_memo_layout.addWidget(memo_group)
        right_layout.addLayout(recipient_memo_layout)

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

        # 중복 확인 - 수정된 부분
        existing_emails = []
        for idx in range(self.recipients_list.count()):
            existing_emails.append(self.recipients_list.item(idx).text())

        if email in existing_emails:
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
            for idx in range(self.recipients_list.count()):
                recipients.append(self.recipients_list.item(idx).text())

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
                "period": "오늘",
                "include_important_tasks": True  # 중요 일정 포함
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
    def on_routine_all_categories_changed(self, state):
        """루틴 - 모든 카테고리 체크박스 상태 변경"""
        checked = state == Qt.CheckState.Checked
        for check in self.routine_category_checks.values():
            check.setChecked(checked)

    def on_routine_category_check_changed(self):
        """루틴 - 개별 카테고리 체크박스 상태 변경"""
        # 모든 카테고리가 선택되었는지 확인
        all_checked = all(check.isChecked() for check in self.routine_category_checks.values())
        any_checked = any(check.isChecked() for check in self.routine_category_checks.values())

        # 전체 선택 체크박스 상태 업데이트
        self.routine_all_categories_check.blockSignals(True)
        if all_checked:
            self.routine_all_categories_check.setChecked(True)
        elif not any_checked:
            self.routine_all_categories_check.setChecked(False)
        else:
            self.routine_all_categories_check.setTristate(True)
            self.routine_all_categories_check.setCheckState(Qt.CheckState.PartiallyChecked)
        self.routine_all_categories_check.blockSignals(False)

    def get_routine_selected_categories(self):
        """루틴 - 선택된 카테고리 목록 반환 (수정된 로직)"""
        # 모든 카테고리 체크박스가 체크되어 있고, 개별 체크박스도 모두 체크되어 있으면 전체
        if (self.routine_all_categories_check.isChecked() and
                all(check.isChecked() for check in self.routine_category_checks.values())):
            print("루틴 카테고리 선택: 모든 카테고리")
            return None  # 모든 카테고리

        # 개별 체크박스에서 선택된 카테고리만 반환
        selected_categories = []
        for category_name, check in self.routine_category_checks.items():
            if check.isChecked():
                selected_categories.append(category_name)

        print(f"루틴 카테고리 선택: {selected_categories}")
        return selected_categories if selected_categories else None

    def select_recipients_from_address_book(self):
        """주소록에서 수신자 선택"""
        # 현재 주소록 가져오기
        address_book = []
        for idx in range(self.recipients_list.count()):
            address_book.append(self.recipients_list.item(idx).text())

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
            # 발송 이력 필드 추가
            routine_data["last_sent_date"] = None
            routine_data["last_sent_time"] = None
            routine_data["total_sent_count"] = 0

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
            for idx, routine in enumerate(self.daily_routines):
                if routine["id"] == self.editing_routine_id:
                    routine_data["id"] = self.editing_routine_id
                    routine_data["created_at"] = routine.get("created_at", datetime.now().isoformat())
                    routine_data["enabled"] = routine.get("enabled", True)
                    # 발송 이력 유지
                    routine_data["last_sent_date"] = routine.get("last_sent_date")
                    routine_data["last_sent_time"] = routine.get("last_sent_time")
                    routine_data["total_sent_count"] = routine.get("total_sent_count", 0)

                    self.daily_routines[idx] = routine_data
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
        routine_id = routine["id"]

        # 상태 토글
        for r in self.daily_routines:
            if r["id"] == routine_id:
                r["enabled"] = not r.get("enabled", True)
                break

        self.refresh_routine_list()

    def send_routine_now(self):
        """선택한 루틴 즉시 발송 (새로운 기능)"""
        current_item = self.routine_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택 없음", "즉시 발송할 루틴을 선택하세요.")
            return

        routine = current_item.data(Qt.ItemDataRole.UserRole)

        # 확인 대화상자
        reply = QMessageBox.question(
            self, "루틴 즉시 발송",
            f"루틴 '{routine['name']}'을 지금 즉시 발송하시겠습니까?\n\n"
            f"수신자: {len(routine.get('recipients', []))}명",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 루틴 즉시 실행
                success = self.execute_routine_immediately(routine)

                if success:
                    # 발송 이력 업데이트
                    self.update_routine_send_history(routine["id"])
                    QMessageBox.information(
                        self, "발송 완료",
                        f"루틴 '{routine['name']}'이 성공적으로 발송되었습니다!"
                    )
                else:
                    QMessageBox.critical(
                        self, "발송 실패",
                        f"루틴 '{routine['name']}' 발송에 실패했습니다.\n\nOutlook이 실행 중인지 확인하세요."
                    )

            except Exception as e:
                print(f"루틴 즉시 발송 중 오류: {e}")
                QMessageBox.critical(self, "오류", f"루틴 발송 중 오류가 발생했습니다:\n{e}")

    def execute_routine_immediately(self, routine):
        """루틴 즉시 실행"""
        try:
            from utils.email_sender import EmailSender

            # 메일 기능 사용 가능 여부 확인
            sender = EmailSender(self.storage_manager)
            available, error_msg = sender.check_availability()
            if not available:
                QMessageBox.critical(self, "메일 기능 사용 불가", error_msg)
                return False

            # 루틴을 daily_routine_checker와 동일한 방식으로 실행
            return self.send_routine_report(routine)

        except Exception as e:
            print(f"루틴 즉시 실행 중 오류: {e}")
            return False

    def send_routine_report(self, routine):
        """루틴 리포트 메일 발송 (daily_routine_checker와 동일한 로직)"""
        try:
            import win32com.client as win32
            from datetime import datetime, timedelta

            # Outlook 연결
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            # 메일 제목
            subject = routine.get("subject", "데일리 리포트")
            mail.Subject = f"[즉시발송] {subject}"

            # 수신자
            recipients = routine.get("recipients", [])
            if not recipients:
                print("수신자가 없어 루틴 실행을 건너뜁니다.")
                return False

            mail.To = "; ".join(recipients)

            # 현재 날짜 사용
            current_date = datetime.now().strftime("%Y-%m-%d")

            # 작업 데이터 수집 (카테고리 필터 + 중요 일정 포함 적용)
            tasks_data = self.collect_routine_tasks_data(current_date, routine.get("selected_categories"),
                                                         routine.get("include_important_tasks", True))

            # HTML 메일 내용 생성
            html_body = self.create_routine_html_report(routine, tasks_data, current_date)
            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            print(f"루틴 리포트 즉시 발송 완료: {routine.get('name', 'Unknown')}")
            return True

        except Exception as e:
            print(f"루틴 리포트 발송 중 오류: {e}")
            return False

    def collect_routine_tasks_data(self, date_str, selected_categories=None, include_important_tasks=True):
        """루틴용 작업 데이터 수집 (daily_routine_checker와 동일한 로직)"""
        all_tasks = self.storage_manager.get_tasks_by_date(date_str)

        # 1단계: 해당 날짜에 생성된 작업만 먼저 필터링
        date_tasks = [t for t in all_tasks if t.created_date == date_str]
        print(f"루틴 - 1단계 날짜별 필터링: {date_str}에 생성된 작업 {len(date_tasks)}개")

        # 2단계: 카테고리 필터 적용
        if selected_categories is not None and len(selected_categories) > 0:
            filtered_tasks = [t for t in date_tasks if t.category in selected_categories]
            print(f"루틴 - 2단계 카테고리 필터링: {selected_categories} 카테고리로 필터링 -> {len(filtered_tasks)}개 작업")
        else:
            filtered_tasks = date_tasks
            print(f"루틴 - 2단계 카테고리 필터링: 모든 카테고리 포함 -> {len(filtered_tasks)}개 작업")

        # 3단계: 미완료 중요 일정 수집 (설정 확인)
        important_tasks = []
        if include_important_tasks:
            important_tasks = self.get_important_incomplete_tasks(date_str, selected_categories)
            print(f"루틴 - 3단계 미완료 중요 일정: {len(important_tasks)}개")

        return {
            "all": filtered_tasks,
            "completed": [t for t in filtered_tasks if t.completed],
            "incomplete": [t for t in filtered_tasks if not t.completed],
            "total": len(filtered_tasks),
            "completed_count": len([t for t in filtered_tasks if t.completed]),
            "completion_rate": (
                    len([t for t in filtered_tasks if t.completed]) / len(
                filtered_tasks) * 100) if filtered_tasks else 0,
            "important_tasks": important_tasks
        }

    def get_important_incomplete_tasks(self, current_date, selected_categories):
        """지난 30일간의 다른 날짜 미완료 중요 작업 수집"""
        try:
            from datetime import datetime, timedelta

            # 30일 전 날짜 계산
            current_dt = datetime.strptime(current_date, "%Y-%m-%d")
            thirty_days_ago = current_dt - timedelta(days=30)
            thirty_days_ago_str = thirty_days_ago.strftime("%Y-%m-%d")

            # 모든 작업에서 조건에 맞는 작업 필터링
            important_tasks = []
            for task in self.storage_manager.tasks:
                # 조건: 다른 날짜 + 미완료 + 중요 + 최근 30일 내
                if (task.created_date != current_date and
                        not task.completed and
                        task.important and
                        thirty_days_ago_str <= task.created_date <= current_date):

                    # 카테고리 필터 적용
                    if selected_categories is None or task.category in selected_categories:
                        important_tasks.append(task)

            # 날짜순으로 정렬 (최신순)
            important_tasks.sort(key=lambda x: x.created_date, reverse=True)

            print(f"루틴 - 미완료 중요 일정 수집: {len(important_tasks)}개 (기간: {thirty_days_ago_str} ~ {current_date})")
            return important_tasks

        except Exception as e:
            print(f"루틴 - 미완료 중요 일정 수집 중 오류: {e}")
            return []

    def create_routine_html_report(self, routine, tasks_data, date_str):
        """루틴용 HTML 리포트 생성 (daily_routine_checker와 동일한 로직)"""
        from datetime import datetime

        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")

        # 카테고리 필터 정보
        selected_categories = routine.get("selected_categories")
        category_filter_info = ""

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

        # 즉시 발송 정보 섹션
        immediate_send_info = f'''
        <table width="100%" cellpadding="15" cellspacing="0" style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; margin-bottom: 20px;">
            <tr>
                <td style="text-align: center;">
                    <strong style="color: #856404; font-size: 16px;">⚡ 즉시 발송 리포트</strong>
                    <div style="font-size: 12px; color: #856404; margin-top: 5px;">
                        루틴명: {routine.get('name', 'Unknown')} | 수동 실행
                    </div>
                </td>
            </tr>
        </table>
        '''

        # 작업 목록 섹션들
        task_sections = ""
        content_types = routine.get("content_types", ["all"])

        if "all" in content_types and tasks_data['all']:
            task_sections += self.create_outlook_task_section("📋 전체 작업", tasks_data['all'])

        if "completed" in content_types and tasks_data['completed']:
            task_sections += self.create_outlook_task_section("✅ 완료된 작업", tasks_data['completed'])

        if "incomplete" in content_types and tasks_data['incomplete']:
            task_sections += self.create_outlook_task_section("⏳ 미완료 작업", tasks_data['incomplete'])

        # 미완료 중요 일정 섹션
        important_section = ""
        if routine.get("include_important_tasks", True) and tasks_data.get("important_tasks"):
            important_section = self.create_important_tasks_section(tasks_data["important_tasks"][:10])

        # 추가 메모 섹션
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

        # HTML 생성 (Outlook 호환)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>루틴 리포트 (즉시 발송)</title>
            <!--[if mso]>
            <style type="text/css">
                table {{ border-collapse: collapse; }}
                .header-table {{ background-color: #4facfe !important; }}
            </style>
            <![endif]-->
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f5f5f5;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px;">
                <tr>
                    <td align="center">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                            <tr>
                                <td class="header-table" style="background-color: #4facfe; padding: 25px 20px; text-align: center;">
                                    <h1 style="margin: 0 0 10px 0; color: #ffffff; font-size: 24px; font-weight: bold;">
                                        ⚡ 루틴 리포트 (즉시 발송)
                                    </h1>
                                    <div style="color: #ffffff; font-size: 16px; margin: 0;">
                                        {current_time}
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 25px 20px;">
                                    {immediate_send_info}
                                    {category_filter_info}

                                    <!-- 데일리 리포트 요약 -->
                                    <table width="100%" cellpadding="20" cellspacing="0" style="background-color: #e3f2fd; border-radius: 10px; margin-bottom: 20px;">
                                        <tr>
                                            <td>
                                                <h2 style="margin: 0 0 15px 0; color: #1976d2; text-align: center;">📊 {report_date} 업무 현황</h2>
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
                                    {important_section}
                                    {memo_section}
                                </td>
                            </tr>
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 15px 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #e9ecef;">
                                    ⚡ Todolist PM 루틴 즉시 발송 | {current_time}<br>
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
        """Outlook 호환 작업 섹션 생성"""
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

    def create_important_tasks_section(self, important_tasks):
        """미완료 중요 일정 섹션 생성"""
        if not important_tasks:
            return ""

        task_rows = ""
        for task in important_tasks:
            from datetime import datetime
            date_display = datetime.strptime(task.created_date, "%Y-%m-%d").strftime("%m/%d")

            task_rows += f"""
            <tr>
                <td style="padding: 10px; background-color: #fff3e0; border-left: 3px solid #ff6b00; border-radius: 5px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td>
                                <strong>⭐ {self.escape_html(task.title)}</strong>
                                <span style="background-color: {self.get_category_color(task.category)}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 5px;">
                                    {task.category}
                                </span>
                                <span style="background-color: #ff6b00; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 5px;">
                                    {date_display}
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
                <td style="padding: 10px 0 5px 0; border-bottom: 2px solid #ff6b00;">
                    <h3 style="margin: 0; color: #ff6b00;">📌 미완료 중요 일정 (최근 30일)</h3>
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
        return "#6c757d"

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

    def update_routine_send_history(self, routine_id):
        """루틴 발송 이력 업데이트"""
        try:
            current_time = datetime.now()
            current_date = current_time.strftime("%Y-%m-%d")
            current_time_str = current_time.strftime("%H:%M")

            # 해당 루틴 찾아서 이력 업데이트
            for routine in self.daily_routines:
                if routine.get("id") == routine_id:
                    routine["last_sent_date"] = current_date
                    routine["last_sent_time"] = current_time_str
                    routine["total_sent_count"] = routine.get("total_sent_count", 0) + 1
                    print(
                        f"루틴 '{routine.get('name')}' 즉시 발송 이력 업데이트: {current_date} {current_time_str} (총 {routine['total_sent_count']}회)")
                    break

            # 루틴 목록 새로고침
            self.refresh_routine_list()

        except Exception as e:
            print(f"루틴 발송 이력 업데이트 중 오류: {e}")

    def on_routine_selected(self, item):
        """루틴 선택 시 버튼 활성화"""
        self.send_now_routine_btn.setEnabled(True)  # 즉시 발송 버튼 활성화
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

        # 카테고리 선택 확인
        selected_categories = self.get_routine_selected_categories()
        if selected_categories is not None and len(selected_categories) == 0:
            QMessageBox.warning(self, "카테고리 오류", "최소 1개의 카테고리를 선택하세요.")
            return False

        return True

    def collect_routine_data(self):
        """루틴 폼 데이터 수집 (중요 일정 포함 설정 추가)"""
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
            "memo": self.routine_memo_edit.toPlainText().strip(),
            "selected_categories": self.get_routine_selected_categories(),  # 카테고리 필터
            "include_important_tasks": self.routine_include_important_check.isChecked()  # 중요 일정 포함 (새로 추가)
        }

    def load_routine_to_form(self, routine):
        """루틴 데이터를 폼에 로드 (중요 일정 포함 설정 추가 + 카테고리 선택 로직 수정)"""
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

        # 카테고리 설정 (완전히 수정된 로직)
        selected_categories = routine.get("selected_categories")

        print(f"루틴 '{routine.get('name')}' 편집 시 저장된 카테고리 설정: {selected_categories}")

        # 시그널 차단하여 무한 루프 방지
        self.routine_all_categories_check.blockSignals(True)
        for check in self.routine_category_checks.values():
            check.blockSignals(True)

        # 먼저 모든 체크박스 해제
        self.routine_all_categories_check.setChecked(False)
        for check in self.routine_category_checks.values():
            check.setChecked(False)

        if selected_categories is None:
            # 저장될 때 None이었다면 정말로 모든 카테고리가 선택된 것
            print("루틴 편집: 저장된 설정이 '모든 카테고리'였음 - 모든 체크박스 활성화")
            self.routine_all_categories_check.setChecked(True)
            for check in self.routine_category_checks.values():
                check.setChecked(True)
        else:
            # 특정 카테고리들이 선택되어 있었던 경우
            print(f"루틴 편집: 저장된 설정에서 선택된 카테고리들 = {selected_categories}")

            # 선택된 카테고리만 체크
            for category_name in selected_categories:
                if category_name in self.routine_category_checks:
                    self.routine_category_checks[category_name].setChecked(True)
                    print(f"  - {category_name} 체크박스 활성화")

            # 모든 카테고리가 선택된 경우에만 "모든 카테고리" 체크박스도 활성화
            if len(selected_categories) == len(self.routine_category_checks):
                all_selected = all(cat_name in selected_categories for cat_name in self.routine_category_checks.keys())
                if all_selected:
                    print("  - 모든 개별 카테고리가 선택되어 있어서 '모든 카테고리' 체크박스도 활성화")
                    self.routine_all_categories_check.setChecked(True)

        # 시그널 복원
        self.routine_all_categories_check.blockSignals(False)
        for check in self.routine_category_checks.values():
            check.blockSignals(False)

        # 중요 일정 포함 설정
        include_important = routine.get("include_important_tasks", True)
        self.routine_include_important_check.setChecked(include_important)

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

        # 카테고리 선택 초기화
        self.routine_all_categories_check.setChecked(True)
        for check in self.routine_category_checks.values():
            check.setChecked(True)

        # 중요 일정 포함 초기화 (기본값 True)
        self.routine_include_important_check.setChecked(True)

        self.routine_memo_edit.clear()

    def refresh_routine_list(self):
        """루틴 목록 새로고침 - 발송 이력 + 중요 일정 포함 상태 표시"""
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

            # 카테고리 정보
            category_info = ""
            selected_categories = routine.get("selected_categories")
            if selected_categories is not None:
                if len(selected_categories) <= 2:
                    category_info = f" [{', '.join(selected_categories)}]"
                else:
                    category_info = f" [{', '.join(selected_categories[:2])} 외 {len(selected_categories) - 2}개]"

            # 중요 일정 포함 상태 (새로 추가)
            important_status = ""
            if routine.get("include_important_tasks", True):
                important_status = " 📌"

            # 발송 이력 정보 추가
            last_sent_info = ""
            last_sent_date = routine.get("last_sent_date")
            total_sent = routine.get("total_sent_count", 0)

            if last_sent_date:
                last_sent_info = f"\n최근발송: {last_sent_date} | 총 {total_sent}회"
            elif total_sent > 0:
                last_sent_info = f"\n총 발송: {total_sent}회"

            display_text = f"{enabled} {name}{important_status}\n{weekday_str} {time} | {recipient_count}명{category_info}{last_sent_info}"

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
            for idx in range(self.recipients_list.count()):
                recipients.append(self.recipients_list.item(idx).text())

            # 이메일 설정 저장
            email_settings = {
                "recipients": recipients,
                "custom_title": "업무현황보고",
                "content_types": ["all", "completed", "incomplete"],
                "period": "오늘",
                "include_important_tasks": True  # 중요 일정 포함 기본값
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
            "recipients": [],
            "include_important_tasks": True  # 중요 일정 포함 기본값
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
                    routines = json.load(f)

                # 기존 루틴에 발송 이력 필드가 없으면 추가
                for routine in routines:
                    if "last_sent_date" not in routine:
                        routine["last_sent_date"] = None
                    if "last_sent_time" not in routine:
                        routine["last_sent_time"] = None
                    if "total_sent_count" not in routine:
                        routine["total_sent_count"] = 0
                    if "include_important_tasks" not in routine:
                        routine["include_important_tasks"] = True  # 기존 루틴에 중요 일정 포함 기본값 설정

                return routines
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