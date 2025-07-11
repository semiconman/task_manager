#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QDateEdit, QTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QDialogButtonBox, QFrame
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
        self.setMinimumSize(600, 700)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()
        self.load_default_settings()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 제목
        title_label = QLabel("데일리 리포트 발송")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; color: #333;")
        layout.addWidget(title_label)

        # === 기본 정보 ===
        basic_group = QGroupBox("기본 정보")
        basic_layout = QVBoxLayout(basic_group)

        # 메일 제목
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("메일 제목:"))
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("예: 일일 업무 보고")
        subject_layout.addWidget(self.subject_edit)
        basic_layout.addLayout(subject_layout)

        # 보고 날짜 선택
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("보고 날짜:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.fromString(self.current_date, "yyyy-MM-dd"))
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        basic_layout.addLayout(date_layout)

        layout.addWidget(basic_group)

        # === 수신자 선택 (주소록 방식) ===
        recipient_group = QGroupBox("수신자 선택")
        recipient_layout = QVBoxLayout(recipient_group)

        # 주소록에서 선택 버튼
        select_from_address_btn = QPushButton("📋 주소록에서 선택")
        select_from_address_btn.clicked.connect(self.select_recipients_from_address_book)
        select_from_address_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 8px 16px;
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
        self.selected_recipients_label.setStyleSheet(
            "color: #666; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px;")
        recipient_layout.addWidget(self.selected_recipients_label)

        # 수신자 직접 추가 (보조 기능)
        direct_add_layout = QHBoxLayout()
        self.recipient_edit = QLineEdit()
        self.recipient_edit.setPlaceholderText("또는 이메일 주소를 직접 입력")

        add_recipient_btn = QPushButton("추가")
        add_recipient_btn.clicked.connect(self.add_recipient_directly)
        add_recipient_btn.setStyleSheet("background: #28a745; color: white; padding: 6px 12px; border-radius: 3px;")

        clear_recipients_btn = QPushButton("전체 해제")
        clear_recipients_btn.clicked.connect(self.clear_recipients)
        clear_recipients_btn.setStyleSheet("background: #dc3545; color: white; padding: 6px 12px; border-radius: 3px;")

        direct_add_layout.addWidget(self.recipient_edit)
        direct_add_layout.addWidget(add_recipient_btn)
        direct_add_layout.addWidget(clear_recipients_btn)
        recipient_layout.addLayout(direct_add_layout)

        layout.addWidget(recipient_group)

        # === 포함 내용 선택 ===
        content_group = QGroupBox("포함 내용")
        content_layout = QVBoxLayout(content_group)

        content_check_layout = QHBoxLayout()
        self.all_tasks_check = QCheckBox("전체 작업")
        self.all_tasks_check.setChecked(True)
        self.completed_tasks_check = QCheckBox("완료된 작업만")
        self.incomplete_tasks_check = QCheckBox("미완료 작업만")

        content_check_layout.addWidget(self.all_tasks_check)
        content_check_layout.addWidget(self.completed_tasks_check)
        content_check_layout.addWidget(self.incomplete_tasks_check)
        content_check_layout.addStretch()
        content_layout.addLayout(content_check_layout)

        layout.addWidget(content_group)

        # === 추가 메모 ===
        memo_group = QGroupBox("추가 메모 (선택사항)")
        memo_layout = QVBoxLayout(memo_group)

        self.memo_edit = QTextEdit()
        self.memo_edit.setPlaceholderText("리포트에 포함할 추가 내용이나 메모를 입력하세요...")
        self.memo_edit.setMaximumHeight(80)
        memo_layout.addWidget(self.memo_edit)

        layout.addWidget(memo_group)

        # === 미리보기 ===
        preview_group = QGroupBox("리포트 미리보기")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setStyleSheet("background: #f8f9fa; border: 1px solid #dee2e6;")
        preview_layout.addWidget(self.preview_text)

        preview_btn = QPushButton("🔍 미리보기 생성")
        preview_btn.clicked.connect(self.generate_preview)
        preview_btn.setStyleSheet("""
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
        preview_layout.addWidget(preview_btn)

        layout.addWidget(preview_group)

        # === 버튼 ===
        button_layout = QHBoxLayout()

        test_send_btn = QPushButton("🧪 테스트 발송")
        test_send_btn.clicked.connect(self.test_send)
        test_send_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)

        send_btn = QPushButton("📧 발송")
        send_btn.clicked.connect(self.send_report)
        send_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)

        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background: #6c757d; color: white; padding: 10px 20px; border-radius: 4px;")

        button_layout.addWidget(test_send_btn)
        button_layout.addWidget(send_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

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
        """지정된 날짜의 작업 데이터 수집"""
        all_tasks = self.storage_manager.get_tasks_by_date(date_str)
        # 해당 날짜에 생성된 작업만 필터링 (다른 날짜의 중요 작업 제외)
        date_tasks = [t for t in all_tasks if t.created_date == date_str]

        return {
            "all": date_tasks,
            "completed": [t for t in date_tasks if t.completed],
            "incomplete": [t for t in date_tasks if not t.completed],
            "total": len(date_tasks),
            "completed_count": len([t for t in date_tasks if t.completed]),
            "completion_rate": (
                        len([t for t in date_tasks if t.completed]) / len(date_tasks) * 100) if date_tasks else 0
        }

    def create_preview_text(self, tasks_data, date_str):
        """미리보기 텍스트 생성"""
        preview = f"=== {date_str} 일일 업무 보고 ===\n\n"

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

        # 추가 메모
        memo = self.memo_edit.toPlainText().strip()
        if memo:
            preview += f"📝 추가 메모\n{memo}\n\n"

        preview += f"---\n보고 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        return preview

    def test_send(self):
        """테스트 발송"""
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

            # 테스트 발송
            success = self.send_daily_report(is_test=True)

            if success:
                QMessageBox.information(self, "테스트 발송 완료", "테스트 메일이 성공적으로 발송되었습니다.")
            else:
                QMessageBox.critical(self, "테스트 발송 실패", "테스트 메일 발송에 실패했습니다.")

        except Exception as e:
            QMessageBox.critical(self, "오류", f"테스트 발송 중 오류가 발생했습니다:\n{e}")

    def send_report(self):
        """리포트 발송"""
        if not self.validate_inputs():
            return

        try:
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

            # 작업 데이터 수집
            tasks_data = self.collect_tasks_data(selected_date)

            # HTML 메일 내용 생성
            html_body = self.create_html_report(tasks_data, selected_date, is_test)
            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            print(f"데일리 리포트 발송 완료: {subject}")
            return True

        except Exception as e:
            print(f"데일리 리포트 발송 중 오류: {e}")
            return False

    def create_html_report(self, tasks_data, date_str, is_test=False):
        """HTML 데일리 리포트 생성 (예약발송 메일과 동일한 양식)"""
        current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
        report_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")

        # 테스트 메시지
        test_message = ""
        if is_test:
            test_message = '''
            <div style="background: #fff3cd; padding: 10px; margin-bottom: 20px; border-radius: 5px;"><strong>테스트 메일입니다</strong></div>
            '''

        # 간단한 요약
        summary = f"""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: #1976d2; margin-top: 0;">오늘의 요약</h2>
            <div style="display: flex; gap: 20px; justify-content: space-around; margin: 15px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #2196f3;">{tasks_data['total']}</div>
                    <div style="font-size: 12px; color: #666;">전체 작업</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #4caf50;">{tasks_data['completed_count']}</div>
                    <div style="font-size: 12px; color: #666;">완료됨</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #f44336;">{tasks_data['total'] - tasks_data['completed_count']}</div>
                    <div style="font-size: 12px; color: #666;">미완료</div>
                </div>
            </div>
            <div style="background: #fff; padding: 10px; border-radius: 5px; margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span>완료율</span>
                    <span style="font-weight: bold; color: #4caf50;">{tasks_data['completion_rate']:.0f}%</span>
                </div>
                <div style="background: #e0e0e0; height: 8px; border-radius: 4px; margin-top: 5px;">
                    <div style="background: #4caf50; height: 8px; border-radius: 4px; width: {tasks_data['completion_rate']:.0f}%;"></div>
                </div>
            </div>
        </div>
        """

        # 작업 목록 (간단하게)
        task_lists = ""

        if self.all_tasks_check.isChecked() and tasks_data['all']:
            task_lists += self.create_simple_task_section("전체 작업", tasks_data['all'][:5])
        if self.completed_tasks_check.isChecked() and tasks_data['completed']:
            task_lists += self.create_simple_task_section("완료된 작업", tasks_data['completed'][:5])
        if self.incomplete_tasks_check.isChecked() and tasks_data['incomplete']:
            task_lists += self.create_simple_task_section("미완료 작업", tasks_data['incomplete'][:5])

        # 추가 메모 섹션
        memo_section = ""
        memo = self.memo_edit.toPlainText().strip()
        if memo:
            memo_section = f'''
            <div style="margin-bottom: 20px;">
                <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">추가 메모</h3>
                <div style="background: #f8f9fa; margin: 5px 0; padding: 10px; border-radius: 5px;">
                    {self.escape_html(memo).replace(chr(10), "<br>")}
                </div>
            </div>
            '''

        # 전체 HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">Todolist 리포트</h1>
                    <div>{current_time}</div>
                </div>
                <div class="content">
                    {test_message}
                    {summary}
                    {task_lists}
                    {memo_section}
                </div>
                <div class="footer">
                    Todolist PM에서 자동 생성 | {current_time}
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def create_simple_task_section(self, title, tasks):
        """작업 섹션 생성 (예약발송과 동일한 양식)"""
        if not tasks:
            return f"""
            <div style="margin-bottom: 20px;">
                <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">{title}</h3>
                <div style="text-align: center; color: #666; padding: 20px;">작업이 없습니다</div>
            </div>
            """

        task_items = ""
        for task in tasks:
            status = "✓" if task.completed else "○"
            style = "text-decoration: line-through; color: #666;" if task.completed else ""
            importance = "★" if task.important else ""

            task_items += f"""
            <div style="background: #f8f9fa; margin: 5px 0; padding: 10px; border-radius: 5px; border-left: 3px solid {'#4caf50' if task.completed else '#2196f3'};">
                <div style="{style}">
                    {status} {importance} <strong>{self.escape_html(task.title)}</strong>
                    <span style="background: #e0e0e0; color: #666; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 10px;">{task.category}</span>
                </div>
                {f'<div style="font-size: 12px; color: #666; margin-top: 5px;">{self.escape_html(task.content[:50])}</div>' if task.content else ''}
            </div>
            """

        return f"""
        <div style="margin-bottom: 20px;">
            <h3 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">{title}</h3>
            {task_items}
        </div>
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