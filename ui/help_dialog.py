#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QMessageBox, QFrame, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class BugReportDialog(QDialog):
    """버그 제보 및 개선 요청 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("개발자에게 버그 제보 및 개선 요청")
        self.setMinimumSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 제목
        title_label = QLabel("버그 제보 및 개선 요청")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 안내 메시지
        info_label = QLabel(
            "발견한 버그나 개선 사항을 자세히 적어주세요.\n"
            "개발자가 빠르게 확인하고 대응하겠습니다."
        )
        info_label.setStyleSheet("color: #666; margin-bottom: 15px; line-height: 1.4;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 메시지 입력 영역
        message_label = QLabel("메시지:")
        message_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(message_label)

        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText(
            "예시:\n"
            "- 요청자 : PM파트 안영준\n"
            "- 버그 내용: 작업 순서 변경 시 프로그램이 느려집니다.\n"
            "- 재현 방법: 1. 작업 5개 생성 2. 드래그로 순서 변경\n"
            "- 개선 요청: 달력에 월간 뷰 기능을 추가해주세요.\n\n"
            "구체적으로 작성해주시면 더 빠른 해결이 가능합니다."
        )
        self.message_edit.setMinimumHeight(200)
        layout.addWidget(self.message_edit)

        # 개발자 정보
        dev_info_frame = QFrame()
        dev_info_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px; padding: 10px; margin-top: 10px;")
        dev_info_layout = QVBoxLayout(dev_info_frame)

        dev_info_label = QLabel("발송 대상: PM파트 안영준 사원 (youngjun.ahn@amkor.co.kr)")
        dev_info_label.setStyleSheet("font-size: 12px; color: #666;")
        dev_info_layout.addWidget(dev_info_label)

        layout.addWidget(dev_info_frame)

        # 버튼
        button_layout = QHBoxLayout()

        send_button = QPushButton("개발자에게 전송")
        send_button.clicked.connect(self.send_bug_report)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)

        button_layout.addWidget(send_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def send_bug_report(self):
        """버그 리포트 전송"""
        message = self.message_edit.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "입력 오류", "메시지를 입력해주세요.")
            return

        try:
            # pywin32 사용 가능 여부 확인
            try:
                import win32com.client as win32
            except ImportError:
                QMessageBox.critical(
                    self, "메일 기능 사용 불가", 
                    "pywin32 라이브러리가 설치되지 않았습니다.\n\n"
                    "설치 방법:\n"
                    "1. 명령 프롬프트를 관리자 권한으로 실행\n"
                    "2. 'pip install pywin32' 입력\n"
                    "3. 프로그램 재시작"
                )
                return

            # Outlook 연결 시도
            try:
                outlook = win32.Dispatch('outlook.application')
            except Exception as e:
                QMessageBox.critical(
                    self, "Outlook 연결 실패",
                    f"Outlook 연결에 실패했습니다:\n{str(e)}\n\n"
                    "Outlook이 설치되어 있고 로그인되어 있는지 확인하세요."
                )
                return

            # 메일 생성
            mail = outlook.CreateItem(0)
            mail.To = "youngjun.ahn@amkor.co.kr"
            mail.Subject = "Todolist 개선 개발 건"
            
            # 현재 시간
            from datetime import datetime
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
            
            # 메일 본문
            mail.Body = f"""안녕하세요,

Todolist PM 사용자로부터 다음과 같은 피드백이 전송되었습니다.

발송 시간: {current_time}

=== 사용자 메시지 ===
{message}
==================

검토 부탁드립니다.

※ 이 메일은 Todolist PM에서 자동으로 전송되었습니다.
"""

            # 메일 발송
            mail.Send()

            QMessageBox.information(
                self, "전송 완료",
                "개발자에게 메시지가 성공적으로 전송되었습니다.\n"
                "빠른 시일 내에 검토 후 연락드리겠습니다.\n\n"
                "감사합니다! 🙏"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self, "전송 실패",
                f"메시지 전송 중 오류가 발생했습니다:\n{e}\n\n"
                "다시 시도하거나 직접 이메일로 연락 부탁드립니다."
            )


class HelpDialog(QDialog):
    """도움말 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Todolist PM - 사용법 및 지원")
        self.setMinimumSize(600, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 스크롤 컨텐츠 위젯
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)

        # 제목
        title_label = QLabel("Todolist PM 도움말")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)

        # 사용법 안내
        usage_frame = QFrame()
        usage_frame.setStyleSheet("background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 20px; margin-bottom: 20px;")
        usage_layout = QVBoxLayout(usage_frame)

        usage_title = QLabel("사용 방법")
        usage_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976d2; margin-bottom: 10px;")
        usage_layout.addWidget(usage_title)

        usage_text = QLabel(
            "사용 방법은 파일에 포함된 설명서 참고를 부탁드리며 "
            "추가 개발로 인하여 설명되지 않은 부분은 PM파트 안영준 사원에게 "
            "메일 또는 연락 부탁드립니다."
        )
        usage_text.setStyleSheet("color: #333; line-height: 1.6; font-size: 14px;")
        usage_text.setWordWrap(True)
        usage_layout.addWidget(usage_text)

        content_layout.addWidget(usage_frame)

        # 개발자 연락처
        contact_frame = QFrame()
        contact_frame.setStyleSheet("background-color: #f3e5f5; border: 1px solid #9c27b0; border-radius: 8px; padding: 20px; margin-bottom: 20px;")
        contact_layout = QVBoxLayout(contact_frame)

        contact_title = QLabel("개발자 연락처")
        contact_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #7b1fa2; margin-bottom: 10px;")
        contact_layout.addWidget(contact_title)

        contact_info = QLabel(
            "이메일: youngjun.ahn@amkor.co.kr\n"
            "연락처: 010-9441-1659\n"
            "담당자: PM파트 안영준 사원"
        )
        contact_info.setStyleSheet("color: #333; line-height: 1.8; font-size: 14px; font-family: 'Consolas', monospace;")
        contact_layout.addWidget(contact_info)

        content_layout.addWidget(contact_frame)

        # 주요 기능 안내
        features_frame = QFrame()
        features_frame.setStyleSheet("background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 8px; padding: 20px; margin-bottom: 20px;")
        features_layout = QVBoxLayout(features_frame)

        features_title = QLabel("주요 기능")
        features_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2e7d32; margin-bottom: 10px;")
        features_layout.addWidget(features_title)

        features_text = QLabel(
            "• 작업 관리: 작업 추가, 편집, 삭제, 완료 처리\n"
            "• 달력 뷰: 날짜별 작업 현황 확인\n"
            "• 카테고리: 작업 분류 및 색상 관리\n"
            "• 메일 발송: 데일리 리포트, 개별 작업 공유\n"
            "• 자동 루틴: 정기적인 리포트 자동 발송\n"
            "• CSV 내보내기: 데이터 백업 및 분석\n"
            "• 템플릿: 자주 사용하는 작업 양식 저장"
        )
        features_text.setStyleSheet("color: #333; line-height: 1.8; font-size: 14px;")
        features_layout.addWidget(features_text)

        content_layout.addWidget(features_frame)

        # 버그 제보 버튼
        bug_report_frame = QFrame()
        bug_report_frame.setStyleSheet("background-color: #fff3e0; border: 1px solid #ff9800; border-radius: 8px; padding: 20px;")
        bug_report_layout = QVBoxLayout(bug_report_frame)

        bug_report_title = QLabel("버그 제보 및 개선 요청")
        bug_report_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f57c00; margin-bottom: 10px;")
        bug_report_layout.addWidget(bug_report_title)

        bug_report_desc = QLabel(
            "프로그램 사용 중 문제가 발생하거나 개선 아이디어가 있으시면\n"
            "아래 버튼을 통해 개발자에게 직접 전달해주세요."
        )
        bug_report_desc.setStyleSheet("color: #333; margin-bottom: 15px; line-height: 1.6;")
        bug_report_desc.setWordWrap(True)
        bug_report_layout.addWidget(bug_report_desc)

        bug_report_button = QPushButton("개발자에게 버그 제보 및 개선 요청")
        bug_report_button.clicked.connect(self.open_bug_report_dialog)
        bug_report_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        bug_report_layout.addWidget(bug_report_button)

        content_layout.addWidget(bug_report_frame)

        # 스크롤 영역 설정
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # 닫기 버튼
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        close_button_layout = QHBoxLayout()
        close_button_layout.addStretch()
        close_button_layout.addWidget(close_button)
        close_button_layout.addStretch()
        layout.addLayout(close_button_layout)

    def open_bug_report_dialog(self):
        """버그 제보 다이얼로그 열기"""
        dialog = BugReportDialog(self)
        dialog.exec()
