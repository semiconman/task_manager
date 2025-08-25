#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QDateEdit, QTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox, QFrame,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class AddressBookSelectionDialog(QDialog):
    """주소록 선택 대화상자 (데일리 리포트용)"""

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


class DailyReportDialog(QDialog):
    """데일리 리포트 대화상자"""

    def __init__(self, storage_manager, current_date):
        super().__init__()

        self.storage_manager = storage_manager
        self.current_date = current_date
        self.selected_recipients = []

        self.setWindowTitle("데일리 리포트")
        self.setMinimumSize(700, 650)  # 높이 증가 (중요 일정 체크박스 추가로)
        self.setMaximumSize(800, 750)  # 최대 높이도 증가
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()
        self.load_default_settings()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 제목
        title_label = QLabel("데일리 리포트 발송")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; color: #333;")
        layout.addWidget(title_label)

        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 스크롤 컨텐츠 위젯
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)

        # === 기본 정보 (2열로 배치) ===
        basic_group = QGroupBox("기본 정보")
        basic_layout = QHBoxLayout(basic_group)

        # 왼쪽: 제목
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("메일 제목:"))
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("예: 일일 업무 보고")
        left_layout.addWidget(self.subject_edit)

        # 오른쪽: 날짜
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("보고 날짜:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.fromString(self.current_date, "yyyy-MM-dd"))
        self.date_edit.setCalendarPopup(True)
        right_layout.addWidget(self.date_edit)

        basic_layout.addLayout(left_layout, 2)
        basic_layout.addLayout(right_layout, 1)
        content_layout.addWidget(basic_group)

        # === 수신자 선택 ===
        recipient_group = QGroupBox("수신자 선택")
        recipient_layout = QVBoxLayout(recipient_group)

        # 버튼들을 한 줄에 배치
        button_row = QHBoxLayout()

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

        clear_recipients_btn = QPushButton("전체 해제")
        clear_recipients_btn.clicked.connect(self.clear_recipients)
        clear_recipients_btn.setStyleSheet("background: #dc3545; color: white; padding: 6px 12px; border-radius: 3px;")

        button_row.addWidget(select_from_address_btn)
        button_row.addWidget(clear_recipients_btn)
        button_row.addStretch()
        recipient_layout.addLayout(button_row)

        # 선택된 수신자 표시
        self.selected_recipients_label = QLabel("선택된 수신자: 없음")
        self.selected_recipients_label.setStyleSheet(
            "color: #666; margin: 8px 0; padding: 12px; background: #f8f9fa; border-radius: 4px; min-height: 20px;")
        self.selected_recipients_label.setWordWrap(True)
        recipient_layout.addWidget(self.selected_recipients_label)

        # 수신자 직접 추가
        direct_add_layout = QHBoxLayout()
        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("이메일 직접 입력")

        add_recipient_btn = QPushButton("추가")
        add_recipient_btn.clicked.connect(self.add_recipient_directly)
        add_recipient_btn.setStyleSheet("background: #28a745; color: white; padding: 6px 12px; border-radius: 3px;")

        direct_add_layout.addWidget(self.recipient_edit, 3)
        direct_add_layout.addWidget(add_recipient_btn, 1)
        recipient_layout.addLayout(direct_add_layout)

        content_layout.addWidget(recipient_group)

        # === 카테고리 필터 ===
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
        content_layout.addWidget(category_group)

        # === 포함 내용 + 추가 메모 (2열로 배치) ===
        content_memo_layout = QHBoxLayout()

        # 왼쪽: 포함 내용
        content_group = QGroupBox("포함 내용")
        content_layout_inner = QVBoxLayout(content_group)

        self.all_tasks_check = QCheckBox("전체 작업")
        self.all_tasks_check.setChecked(True)
        self.completed_tasks_check = QCheckBox("완료된 작업만")
        self.incomplete_tasks_check = QCheckBox("미완료 작업만")

        content_layout_inner.addWidget(self.all_tasks_check)
        content_layout_inner.addWidget(self.completed_tasks_check)
        content_layout_inner.addWidget(self.incomplete_tasks_check)

        # 중요 일정 포함 체크박스 추가
        self.include_important_check = QCheckBox("📌 미완료 중요 일정 포함 (지난 30일)")
        self.include_important_check.setChecked(True)  # 기본값: 체크됨
        self.include_important_check.setToolTip("지난 30일간의 다른 날짜 미완료 중요 작업을 별도 섹션으로 포함")
        self.include_important_check.setStyleSheet("font-weight: bold; color: #d32f2f; margin-top: 10px;")
        content_layout_inner.addWidget(self.include_important_check)

        # 오른쪽: 추가 메모
        memo_group = QGroupBox("추가 메모")
        memo_layout = QVBoxLayout(memo_group)

        self.memo_edit = QTextEdit()
        self.memo_edit.setPlaceholderText("추가 메모...")
        self.memo_edit.setMaximumHeight(80)
        memo_layout.addWidget(self.memo_edit)

        content_memo_layout.addWidget(content_group, 1)
        content_memo_layout.addWidget(memo_group, 2)
        content_layout.addLayout(content_memo_layout)

        # === 미리보기 ===
        preview_group = QGroupBox("리포트 미리보기")
        preview_layout = QVBoxLayout(preview_group)

        preview_btn_layout = QHBoxLayout()
        preview_btn = QPushButton("🔍 미리보기 생성")
        preview_btn.clicked.connect(self.generate_preview)
        preview_btn.setStyleSheet("""
            QPushButton {
                background: #ffc107;
                color: black;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        preview_btn_layout.addWidget(preview_btn)
        preview_btn_layout.addStretch()
        preview_layout.addLayout(preview_btn_layout)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(120)
        self.preview_text.setStyleSheet("background: #f8f9fa; border: 1px solid #dee2e6; font-size: 11px;")
        preview_layout.addWidget(self.preview_text)

        content_layout.addWidget(preview_group)

        # 스크롤 영역 설정
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # === 버튼 ===
        button_layout = QHBoxLayout()

        send_btn = QPushButton("📧 발송")
        send_btn.clicked.connect(self.send_report)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)

        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(
            "background: #6c757d; color: white; padding: 10px 20px; border-radius: 4px; font-size: 14px;")

        button_layout.addWidget(send_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

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
            print("카테고리 필터: 모든 카테고리 선택됨")
            return None  # 모든 카테고리

        selected_categories = []
        for category_name, check in self.category_checks.items():
            if check.isChecked():
                selected_categories.append(category_name)

        print(f"카테고리 필터: 선택된 카테고리 = {selected_categories}")
        return selected_categories if selected_categories else None

    def load_default_settings(self):
        """기본 설정 로드"""
        # 오늘 날짜로 기본 제목 설정
        today_str = datetime.now().strftime("%Y-%m-%d")
        default_subject = f"{today_str} 일일 업무 보고"
        self.subject_edit.setText(default_subject)

    def select_recipients_from_address_book(self):
        """주소록에서 수신자 선택"""
        try:
            # 주소록 로드
            address_book = self.load_address_book()

            if not address_book:
                QMessageBox.warning(self, "주소록 없음",
                                    "주소록이 비어있습니다.\n먼저 '옵션 > 메일 설정 > 주소록'에서 이메일 주소를 추가하세요.")
                return

            # 주소록 선택 대화상자 열기
            dialog = AddressBookSelectionDialog(address_book, self.selected_recipients)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.selected_recipients = dialog.get_selected_emails()
                self.update_selected_recipients_display()

        except Exception as e:
            QMessageBox.critical(self, "오류", f"주소록 불러오기 중 오류가 발생했습니다:\n{e}")

    def load_address_book(self):
        """저장된 주소록 로드"""
        try:
            settings_file = "data/email_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                return settings.get("recipients", [])
        except Exception as e:
            print(f"주소록 로드 중 오류: {e}")
        return []

    def update_selected_recipients_display(self):
        """선택된 수신자 표시 업데이트"""
        count = len(self.selected_recipients)
        if count == 0:
            self.selected_recipients_label.setText("선택된 수신자: 없음")
            self.selected_recipients_label.setStyleSheet(
                "color: #999; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px;")
        elif count <= 2:
            # 2명 이하면 모든 이메일 표시
            emails = ", ".join(self.selected_recipients)
            self.selected_recipients_label.setText(f"선택된 수신자: {emails}")
            self.selected_recipients_label.setStyleSheet(
                "color: #333; margin: 10px 0; padding: 10px; background: #e8f5e8; border-radius: 4px; border: 1px solid #4CAF50;")
        else:
            # 2명 초과면 처음 2명만 표시하고 나머지는 개수로
            first_two = ", ".join(self.selected_recipients[:2])
            self.selected_recipients_label.setText(f"선택된 수신자: {first_two} 외 {count - 2}명")
            self.selected_recipients_label.setStyleSheet(
                "color: #333; margin: 10px 0; padding: 10px; background: #e8f5e8; border-radius: 4px; border: 1px solid #4CAF50;")

    def add_recipient_directly(self):
        """수신자 직접 추가"""
        email = self.recipient_edit.text().strip()
        if not email:
            return

        if "@" not in email:
            QMessageBox.warning(self, "이메일 오류", "올바른 이메일 주소를 입력하세요.")
            return

        # 중복 확인
        if email in self.selected_recipients:
            QMessageBox.warning(self, "중복", "이미 추가된 수신자입니다.")
            return

        self.selected_recipients.append(email)
        self.update_selected_recipients_display()
        self.recipient_edit.clear()

    def clear_recipients(self):
        """모든 수신자 해제"""
        self.selected_recipients = []
        self.update_selected_recipients_display()

    def generate_preview(self):
        """리포트 미리보기 생성"""
        try:
            # 선택된 날짜의 작업 데이터 수집
            selected_date = self.date_edit.date().toString("yyyy-MM-dd")
            tasks_data = self.collect_tasks_data(selected_date)

            # 미리보기 텍스트 생성
            preview_text = self.create_preview_text(tasks_data, selected_date)
            self.preview_text.setPlainText(preview_text)

        except Exception as e:
            QMessageBox.critical(self, "미리보기 오류", f"미리보기 생성 중 오류가 발생했습니다:\n{e}")

    def collect_tasks_data(self, date_str):
        """지정된 날짜의 작업 데이터 수집 (카테고리 필터 적용)"""
        # 1단계: 해당 날짜에 생성된 작업만 먼저 필터링
        all_tasks = self.storage_manager.get_tasks_by_date(date_str)
        date_tasks = [t for t in all_tasks if t.created_date == date_str]

        print(f"1단계 - 날짜별 필터링: {date_str}에 생성된 작업 {len(date_tasks)}개")

        # 2단계: 카테고리 필터 적용
        selected_categories = self.get_selected_categories()
        if selected_categories is not None:  # 특정 카테고리만 선택된 경우
            filtered_tasks = [t for t in date_tasks if t.category in selected_categories]
            print(f"2단계 - 카테고리 필터링: {selected_categories} 카테고리로 필터링 -> {len(filtered_tasks)}개 작업")
        else:
            filtered_tasks = date_tasks
            print(f"2단계 - 카테고리 필터링: 모든 카테고리 포함 -> {len(filtered_tasks)}개 작업")

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

    def collect_important_tasks(self, date_str):
        """지난 30일간의 다른 날짜 미완료 중요 작업 수집 (카테고리 필터 적용)"""
        if not self.include_important_check.isChecked():
            return []

        try:
            # 지난 30일 범위 계산
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_date = current_date - timedelta(days=30)
            start_date_str = start_date.strftime("%Y-%m-%d")

            print(f"중요 작업 수집 범위: {start_date_str} ~ {date_str}")

            # 모든 작업에서 조건에 맞는 작업 필터링
            important_tasks = []
            selected_categories = self.get_selected_categories()

            for task in self.storage_manager.tasks:
                # 1. 다른 날짜의 작업인지 확인
                if task.created_date == date_str:
                    continue

                # 2. 지난 30일 범위 내인지 확인
                if task.created_date < start_date_str or task.created_date > date_str:
                    continue

                # 3. 중요하고 미완료인지 확인
                if not (task.important and not task.completed):
                    continue

                # 4. 카테고리 필터 적용
                if selected_categories is not None:
                    if task.category not in selected_categories:
                        continue

                important_tasks.append(task)

            # 날짜순으로 정렬 (최신순)
            important_tasks.sort(key=lambda x: x.created_date, reverse=True)

            print(f"수집된 중요 작업 수: {len(important_tasks)}")
            for task in important_tasks:
                print(f"  - {task.created_date} [{task.category}] {task.title}")

            return important_tasks

        except Exception as e:
            print(f"중요 작업 수집 중 오류: {e}")
            return []

    def create_preview_text(self, tasks_data, date_str):
        """미리보기 텍스트 생성"""
        preview = f"=== {date_str} 일일 업무 보고 ===\n\n"

        # 카테고리 필터 정보 표시
        selected_categories = self.get_selected_categories()
        if selected_categories is not None:
            preview += f"📂 포함된 카테고리: {', '.join(selected_categories)}\n\n"
        else:
            preview += f"📂 포함된 카테고리: 모든 카테고리\n\n"

        # 통계
        preview += f"업무 현황\n"
        preview += f"• 전체 작업: {tasks_data['total']}개\n"
        preview += f"• 완료: {tasks_data['completed_count']}개\n"
        preview += f"• 미완료: {tasks_data['total'] - tasks_data['completed_count']}개\n"
        preview += f"• 완료율: {tasks_data['completion_rate']:.1f}%\n\n"

        # 선택된 내용에 따라 작업 목록 추가
        if self.all_tasks_check.isChecked() and tasks_data['all']:
            preview += "📋 전체 작업 목록\n"
            for i, task in enumerate(tasks_data['all'], 1):
                status = "✅" if task.completed else "⏳"
                importance = "⭐ " if task.important else ""
                preview += f"{i}. {status} {importance}[{task.category}] {task.title}\n"
            preview += "\n"

        if self.completed_tasks_check.isChecked() and tasks_data['completed']:
            preview += "✅ 완료된 작업\n"
            for i, task in enumerate(tasks_data['completed'], 1):
                importance = "⭐ " if task.important else ""
                preview += f"{i}. {importance}[{task.category}] {task.title}\n"
            preview += "\n"

        if self.incomplete_tasks_check.isChecked() and tasks_data['incomplete']:
            preview += "⏳ 미완료 작업\n"
            for i, task in enumerate(tasks_data['incomplete'], 1):
                importance = "⭐ " if task.important else ""
                preview += f"{i}. {importance}[{task.category}] {task.title}\n"
            preview += "\n"

        # 중요 일정 섹션 추가
        if self.include_important_check.isChecked():
            important_tasks = self.collect_important_tasks(date_str)
            if important_tasks:
                preview += "📌 미완료 중요 일정 (지난 30일)\n"
                for i, task in enumerate(important_tasks, 1):
                    preview += f"{i}. ⭐ {task.created_date} [{task.category}] {task.title}\n"
                preview += "\n"

        # 추가 메모
        memo = self.memo_edit.toPlainText().strip()
        if memo:
            preview += f"📝 추가 메모\n{memo}\n\n"

        preview += f"---\n보고 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        return preview

    def send_report(self):
        """리포트 발송"""
        if not self.validate_inputs():
            return

        try:
            # 메일 기능 사용 가능 여부 확인
            from utils.email_sender import EmailSender
            sender = EmailSender(self.storage_manager)
            available, error_msg = sender.check_availability()

            if not available:
                QMessageBox.critical(self, "메일 기능 사용 불가", error_msg)
                return

            reply = QMessageBox.question(
                self, "리포트 발송 확인",
                f"다음 {len(self.selected_recipients)}명에게 데일리 리포트를 발송하시겠습니까?\n\n" + "\n".join(self.selected_recipients),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                success = self.send_daily_report(is_test=False)

                if success:
                    QMessageBox.information(self, "발송 완료",
                                            f"데일리 리포트가 {len(self.selected_recipients)}명에게 성공적으로 발송되었습니다.")
                    self.accept()
                else:
                    QMessageBox.critical(self, "발송 실패", "데일리 리포트 발송에 실패했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"리포트 발송 중 오류가 발생했습니다:\n{e}")

    def validate_inputs(self):
        """입력 값 검증"""
        if not self.subject_edit.text().strip():
            QMessageBox.warning(self, "입력 오류", "메일 제목을 입력하세요.")
            self.subject_edit.setFocus()
            return False

        if not self.selected_recipients:
            QMessageBox.warning(self, "수신자 오류", "주소록에서 수신자를 선택하거나 직접 추가하세요.")
            return False

        if not (
                self.all_tasks_check.isChecked() or self.completed_tasks_check.isChecked() or self.incomplete_tasks_check.isChecked()):
            QMessageBox.warning(self, "내용 선택 오류", "포함할 내용을 최소 1개 선택하세요.")
            return False

        # 카테고리 선택 확인
        selected_categories = self.get_selected_categories()
        if selected_categories is not None and len(selected_categories) == 0:
            QMessageBox.warning(self, "카테고리 오류", "최소 1개의 카테고리를 선택하세요.")
            return False

        return True

    def send_daily_report(self, is_test=False):
        """실제 데일리 리포트 메일 발송"""
        try:
            import win32com.client as win32

            # Outlook 연결
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            # 메일 제목
            subject = self.subject_edit.text().strip()
            if is_test:
                subject = "[테스트] " + subject
            mail.Subject = subject

            # 수신자
            mail.To = "; ".join(self.selected_recipients)

            # 선택된 날짜
            selected_date = self.date_edit.date().toString("yyyy-MM-dd")

            # 작업 데이터 수집 (카테고리 필터 적용)
            tasks_data = self.collect_tasks_data(selected_date)

            # 중요 작업 데이터 수집
            important_tasks = self.collect_important_tasks(selected_date)

            # HTML 메일 내용 생성
            html_body = self.create_html_report(tasks_data, important_tasks, selected_date, is_test)
            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            print(f"데일리 리포트 발송 완료: {subject}")
            return True

        except Exception as e:
            print(f"데일리 리포트 발송 중 오류: {e}")
            return False

    def create_html_report(self, tasks_data, important_tasks, date_str, is_test=False):
        """HTML 데일리 리포트 생성 (Outlook 호환성 개선 + 카테고리 필터 정보 + 중요 일정 섹션 추가)"""
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")

        # 카테고리 필터 정보 - 수정된 로직
        selected_categories = self.get_selected_categories()
        category_filter_info = ""

        print(f"HTML 생성 시 카테고리 필터: {selected_categories}")  # 디버그

        if selected_categories is not None and len(selected_categories) > 0:
            # 특정 카테고리가 선택된 경우
            category_filter_info = f'''
            <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #e8f4fd; border: 1px solid #bee5eb; border-radius: 5px; margin-bottom: 20px;">
                <tr><td style="text-align: center;">
                    <strong>📂 포함된 카테고리:</strong> {', '.join(selected_categories)}
                </td></tr>
            </table>
            '''
        else:
            # 모든 카테고리가 선택된 경우
            category_filter_info = f'''
            <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; margin-bottom: 20px;">
                <tr><td style="text-align: center;">
                    <strong>📂 포함된 카테고리:</strong> 모든 카테고리
                </td></tr>
            </table>
            '''

        # 테스트 메시지 (Outlook 호환)
        test_message = ""
        if is_test:
            test_message = '''
            <table width="100%" cellpadding="10" cellspacing="0" style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; margin-bottom: 20px;">
                <tr><td style="text-align: center; font-weight: bold;">🧪 테스트 메일입니다</td></tr>
            </table>
            '''

        # 작업 목록
        task_lists = ""

        if self.all_tasks_check.isChecked() and tasks_data['all']:
            task_lists += self.create_outlook_task_section("📋 전체 작업", tasks_data['all'])
        if self.completed_tasks_check.isChecked() and tasks_data['completed']:
            task_lists += self.create_outlook_task_section("✅ 완료된 작업", tasks_data['completed'])
        if self.incomplete_tasks_check.isChecked() and tasks_data['incomplete']:
            task_lists += self.create_outlook_task_section("⏳ 미완료 작업", tasks_data['incomplete'])

        # 중요 일정 섹션 (새로 추가)
        important_section = ""
        if self.include_important_check.isChecked() and important_tasks:
            important_section = self.create_important_tasks_section(important_tasks)

        # 추가 메모 섹션 (Outlook 호환)
        memo_section = ""
        memo = self.memo_edit.toPlainText().strip()
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
            <title>Todolist 리포트</title>
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
                                        📋 Todolist 리포트
                                    </h1>
                                    <div style="color: #ffffff; font-size: 16px; margin: 0;">
                                        {current_time}
                                    </div>
                                </td>
                            </tr>

                            <!-- 메인 컨텐츠 -->
                            <tr>
                                <td style="padding: 25px 20px;">

                                    {test_message}
                                    {category_filter_info}

                                    <!-- 데일리 리포트 요약 -->
                                    <table width="100%" cellpadding="20" cellspacing="0" style="background-color: #e3f2fd; border-radius: 10px; margin-bottom: 20px;">
                                        <tr>
                                            <td>
                                                <h2 style="margin: 0 0 15px 0; color: #1976d2; text-align: center;">📊 데일리 리포트</h2>

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

                                    {task_lists}
                                    {important_section}
                                    {memo_section}

                                </td>
                            </tr>

                            <!-- 푸터 -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 15px 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #e9ecef;">
                                    🤖 Todolist PM에서 자동 생성됨 | {current_time}
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
                    <td style="text-align: center; color: #666; padding: 20px;">작업이 없습니다</td>
                </tr>
            </table>
            """

        task_rows = ""
        for task in tasks:
            status = "✓" if task.completed else "○"
            text_style = "text-decoration: line-through; color: #666;" if task.completed else ""
            importance = "★ " if task.important else ""
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
                    <h3 style="margin: 0; color: #333;">{title}</h3>
                </td>
            </tr>
            <tr><td style="height: 10px;"></td></tr>
            {task_rows}
        </table>
        """

    def create_important_tasks_section(self, important_tasks):
        """중요 일정 섹션 생성 (테이블 기반)"""
        if not important_tasks:
            return ""

        task_rows = ""
        for task in important_tasks:
            # 날짜 정보 추가
            date_info = f"{task.created_date}"

            task_rows += f"""
            <tr>
                <td style="padding: 10px; background-color: #fff3e0; border-left: 3px solid #ff9800; border-radius: 5px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td>
                                <strong>⭐ {self.escape_html(task.title)}</strong>
                                <span style="background-color: {self.get_category_color(task.category)}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 10px;">
                                    {task.category}
                                </span>
                                <span style="background-color: #9e9e9e; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 5px;">
                                    {date_info}
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
                <td style="padding: 10px 0 5px 0; border-bottom: 2px solid #ff9800;">
                    <h3 style="margin: 0; color: #f57c00;">📌 미완료 중요 일정 (지난 30일)</h3>
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