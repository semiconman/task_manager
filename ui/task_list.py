from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton, QCheckBox, QMessageBox, QApplication,
    QDialog, QListWidget, QListWidgetItem, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QColor, QDrag, QPixmap, QPainter
from PyQt6.QtCore import QMimeData

from ui.task_form import TaskForm


class EmailRecipientDialog(QDialog):
    """메일 수신자 선택 다이얼로그"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("메일 수신자 선택")
        self.setMinimumSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.selected_recipients = []
        self.init_ui()
        self.load_recipients()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 안내 메시지
        info_label = QLabel("메일을 받을 수신자를 선택하세요:")
        layout.addWidget(info_label)

        # 수신자 목록
        self.recipients_list = QListWidget()
        layout.addWidget(self.recipients_list)

        # 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("발송")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_recipients(self):
        """저장된 수신자 목록 로드"""
        try:
            import os
            import json

            settings_file = "data/email_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                recipients = settings.get("recipients", [])
                if recipients:
                    for recipient in recipients:
                        item = QListWidgetItem(recipient)
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.recipients_list.addItem(item)
                else:
                    item = QListWidgetItem("저장된 수신자가 없습니다.")
                    item.setFlags(Qt.ItemFlag.NoItemFlags)
                    self.recipients_list.addItem(item)
            else:
                item = QListWidgetItem("메일 설정을 먼저 완료하세요.")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self.recipients_list.addItem(item)

        except Exception as e:
            print(f"수신자 목록 로드 중 오류: {e}")
            item = QListWidgetItem("수신자 목록을 로드할 수 없습니다.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recipients_list.addItem(item)

    def accept(self):
        """확인 버튼 클릭 처리"""
        self.selected_recipients = []

        for i in range(self.recipients_list.count()):
            item = self.recipients_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_recipients.append(item.text())

        if not self.selected_recipients:
            QMessageBox.warning(self, "선택 없음", "메일을 받을 수신자를 선택하세요.")
            return

        super().accept()


class TaskItemWidget(QFrame):
    """작업 항목 위젯"""

    # 커스텀 시그널
    task_toggled = pyqtSignal(str, bool)  # 작업 완료 상태 변경 (id, completed)
    edit_task = pyqtSignal(str)  # 작업 편집 요청 (id)
    delete_task = pyqtSignal(str)  # 작업 삭제 요청 (id)

    def __init__(self, task, current_date, storage_manager=None):
        """작업 항목 위젯 초기화

        Args:
            task (Task): 표시할 작업 객체
            current_date (str): 현재 선택된 날짜
            storage_manager (StorageManager): 스토리지 매니저 (카테고리 색상 참조용)
        """
        super().__init__()

        self.task = task
        self.current_date = current_date
        self.storage_manager = storage_manager
        self.drag_start_position = QPoint()
        self.content_expanded = False  # 내용 확장 상태

        # 스타일 설정
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)

        # 다른 날짜의 중요 작업인 경우 스타일 변경
        is_other_date = task.created_date != current_date

        if is_other_date and task.important and not task.completed:
            self.setStyleSheet(
                "background-color: #FFF8E1; border: 1px solid #FFE082; border-radius: 5px; margin: 2px;"
            )
        else:
            self.setStyleSheet(
                "background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 5px; margin: 2px;"
            )

        # 레이아웃 설정
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 완료 체크박스
        self.complete_checkbox = QCheckBox()
        self.complete_checkbox.setChecked(self.task.completed)
        self.complete_checkbox.toggled.connect(self.on_complete_toggled)
        main_layout.addWidget(self.complete_checkbox)

        # 작업 정보 영역 (고정 크기)
        info_widget = QWidget()
        info_widget.setMinimumWidth(400)  # 최소 너비 설정
        info_widget.setMaximumWidth(600)  # 최대 너비 설정
        info_widget.setStyleSheet("background: transparent;")  # 배경 투명으로 설정
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # 제목 행
        title_layout = QHBoxLayout()

        # 중요 표시 아이콘 (완료 여부와 관계없이 중요 작업이면 표시)
        if self.task.important:
            important_icon = QLabel("🔥")
            important_icon.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                margin-right: 5px;
                border: none;
            """)
            important_icon.setToolTip("중요 작업")
            title_layout.addWidget(important_icon)

        # 카테고리 라벨
        category_label = QLabel(self.task.category)
        if self.task.important and not self.task.completed:
            category_label.setStyleSheet(
                f"color: white; background-color: {self.get_category_color()}; "
                f"padding: 2px 5px; border: none; border-radius: 3px; font-size: 10px;"
            )
        else:
            category_label.setStyleSheet(
                f"color: white; background-color: {self.get_category_color()}; "
                f"padding: 2px 5px; border-radius: 3px; font-size: 10px;"
            )
        category_label.setMaximumHeight(20)
        title_layout.addWidget(category_label)

        # 제목 라벨
        title_text = self.task.title
        if self.task.important and not self.task.completed:
            title_text = f"【중요】{self.task.title}"

        title_label = QLabel(title_text)
        title_label.setWordWrap(True)  # 제목 줄바꿈 허용

        # 제목 스타일 설정
        if self.task.completed:
            title_label.setStyleSheet("text-decoration: line-through; color: #9E9E9E; font-size: 14px; border: none;")
        elif self.task.important:
            title_label.setStyleSheet("""
                font-weight: bold; 
                font-size: 15px; 
                color: #D32F2F;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                border: none;
            """)
        else:
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")

        title_layout.addWidget(title_label, stretch=1)

        # 다른 날짜의 작업인 경우 날짜 표시
        if self.task.created_date != self.current_date:
            date_label = QLabel(self.task.created_date)
            date_label.setStyleSheet("color: #9E9E9E; font-size: 10px; border: none;")
            title_layout.addWidget(date_label)

        info_layout.addLayout(title_layout)

        # 내용 라벨 (있는 경우에만)
        if self.task.content:
            self.create_content_area(info_layout)

        main_layout.addWidget(info_widget, stretch=1)

        # 기능 버튼 영역 (고정 크기)
        button_widget = QWidget()
        button_widget.setFixedWidth(180)  # 기능 영역 고정 너비
        button_widget.setStyleSheet("background: transparent;")  # 배경 투명으로 설정
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 0, 0, 0)
        button_layout.setSpacing(3)  # 버튼 간격 줄임

        # 더보기 버튼 (내용이 길 때만 표시)
        if self.task.content and self.needs_truncation():
            self.toggle_button = self.create_function_button("더보기")
            self.toggle_button.clicked.connect(self.toggle_content)
            button_layout.addWidget(self.toggle_button)
        else:
            self.toggle_button = None

        # 메일 발송 버튼
        self.email_button = self.create_function_button("메일")
        self.email_button.clicked.connect(self.on_email_clicked)
        button_layout.addWidget(self.email_button)

        # 편집 버튼
        edit_button = self.create_function_button("편집")
        edit_button.clicked.connect(self.on_edit_clicked)
        button_layout.addWidget(edit_button)

        # 삭제 버튼
        delete_button = self.create_function_button("삭제", color="#E53935")
        delete_button.clicked.connect(self.on_delete_clicked)
        button_layout.addWidget(delete_button)

        main_layout.addWidget(button_widget)

        # 작업 배경색 설정
        self.apply_task_style()

    def create_function_button(self, text, color="#333333"):
        """통일된 스타일의 기능 버튼 생성"""
        button = QPushButton(text)
        button.setFixedSize(35, 22)  # 크기 축소 (기존 40x25 → 35x22)

        if self.task.important and not self.task.completed:
            # 중요 작업용 스타일 (테두리 없음)
            button.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; 
                    border: none;
                    outline: none;
                    border-radius: 3px; 
                    padding: 1px; 
                    font-size: 10px;
                    color: {color};
                }}
                QPushButton:hover {{
                    background-color: rgba(0,0,0,0.1);
                    border: none;
                    outline: none;
                }}
                QPushButton:focus {{
                    border: none;
                    outline: none;
                }}
            """)
        else:
            # 일반 작업용 스타일 (테두리 있음)
            button.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; 
                    border: 1px solid #CCCCCC; 
                    border-radius: 3px; 
                    padding: 1px; 
                    font-size: 10px;
                    color: {color};
                }}
                QPushButton:hover {{
                    background-color: rgba(0,0,0,0.05);
                }}
                QPushButton:focus {{
                    border: 1px solid #4285F4;
                }}
            """)

        return button

    def needs_truncation(self):
        """내용 줄임이 필요한지 확인"""
        if not self.task.content:
            return False

        content_text = self.task.content.strip()
        lines = content_text.split('\n')
        return len(lines) > 2 or len(content_text) > 80

    def create_content_area(self, parent_layout):
        """내용 영역 생성 (줄임/확장 기능 포함)"""
        content_text = self.task.content.strip()

        # 내용 길이 체크
        needs_truncation = self.needs_truncation()

        if needs_truncation:
            # 줄임 버전 생성
            lines = content_text.split('\n')
            if len(lines) > 2:
                truncated_text = '\n'.join(lines[:2])
            else:
                truncated_text = content_text[:80]

            if len(truncated_text) < len(content_text):
                truncated_text += "..."

            # 내용 라벨
            self.content_label = QLabel(truncated_text if not self.content_expanded else content_text)
            self.content_label.setWordWrap(True)
            self.content_label.setMaximumWidth(580)  # 내용 최대 너비 제한

            parent_layout.addWidget(self.content_label)
        else:
            # 짧은 내용은 그대로 표시
            self.content_label = QLabel(content_text)
            self.content_label.setWordWrap(True)
            self.content_label.setMaximumWidth(580)  # 내용 최대 너비 제한
            parent_layout.addWidget(self.content_label)

        # 내용 스타일 설정
        self.update_content_style()

    def toggle_content(self):
        """내용 확장/축소 토글"""
        if not self.toggle_button:
            return

        self.content_expanded = not self.content_expanded

        content_text = self.task.content.strip()

        if self.content_expanded:
            # 전체 내용 표시
            self.content_label.setText(content_text)
            self.toggle_button.setText("접기")
        else:
            # 줄인 내용 표시
            lines = content_text.split('\n')
            if len(lines) > 2:
                truncated_text = '\n'.join(lines[:2])
            else:
                truncated_text = content_text[:80]

            if len(truncated_text) < len(content_text):
                truncated_text += "..."

            self.content_label.setText(truncated_text)
            self.toggle_button.setText("더보기")

    def update_content_style(self):
        """내용 스타일 업데이트"""
        if hasattr(self, 'content_label'):
            if self.task.completed:
                self.content_label.setStyleSheet("color: #9E9E9E; font-size: 12px; border: none;")
            elif self.task.important:
                self.content_label.setStyleSheet("""
                    color: #D32F2F; 
                    font-size: 12px; 
                    font-weight: 500;
                    border: none;
                """)
            else:
                self.content_label.setStyleSheet("color: #616161; font-size: 12px; border: none;")

    def get_category_color(self):
        """작업 카테고리에 해당하는 색상 반환"""
        if self.storage_manager:
            for category in self.storage_manager.categories:
                if category.name == self.task.category:
                    return category.color

        # 기본 색상
        default_colors = {
            "LB": "#4285F4",
            "Tester": "#FBBC05",
            "Handler": "#34A853",
            "ETC": "#EA4335"
        }
        return default_colors.get(self.task.category, "#9E9E9E")

    def on_complete_toggled(self, checked):
        """완료 상태 변경 처리"""
        self.task_toggled.emit(self.task.id, checked)

    def on_email_clicked(self):
        """메일 발송 버튼 클릭 처리"""
        try:
            # 메일 기능 사용 가능 여부 확인
            from utils.email_sender import EmailSender

            sender = EmailSender(self.storage_manager)
            available, error_msg = sender.check_availability()

            if not available:
                QMessageBox.critical(self, "메일 기능 사용 불가", error_msg)
                return

            # 수신자 선택 다이얼로그
            dialog = EmailRecipientDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                recipients = dialog.selected_recipients
                if recipients:
                    success = self.send_task_email(recipients)
                    if success:
                        QMessageBox.information(self, "메일 발송 완료",
                                                f"'{self.task.title}' 일정이 {len(recipients)}명에게 발송되었습니다.")
                    else:
                        QMessageBox.critical(self, "메일 발송 실패",
                                             "메일 발송에 실패했습니다.\nOutlook이 실행 중인지 확인하세요.")

        except Exception as e:
            print(f"메일 발송 중 오류: {e}")
            QMessageBox.critical(self, "오류", f"메일 발송 중 오류가 발생했습니다:\n{e}")

    def send_task_email(self, recipients):
        """개별 작업 메일 발송"""
        try:
            import win32com.client as win32
            from datetime import datetime

            # Outlook 연결
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            # 메일 제목 설정
            status = "완료" if self.task.completed else "미완료"
            mail.Subject = f"[{status}] {self.task.title}"

            # 수신자 설정
            mail.To = "; ".join(recipients)

            # 메일 내용 생성
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .status {{ 
                        display: inline-block; 
                        padding: 5px 15px; 
                        border-radius: 20px; 
                        font-weight: bold; 
                        background: {'#4CAF50' if self.task.completed else '#FF9800'}; 
                        color: white; 
                        margin-bottom: 15px; 
                    }}
                    .task-content {{ 
                        background: #f8f9fa; 
                        padding: 15px; 
                        border-radius: 5px; 
                        border-left: 4px solid {'#4CAF50' if self.task.completed else '#FF9800'}; 
                    }}
                    .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">📋 일정 공유</h1>
                        <div>{current_time}</div>
                    </div>
                    <div class="content">
                        <div class="status">{status}</div>

                        <h2 style="color: #333; margin-bottom: 15px;">{self.escape_html(self.task.title)}</h2>

                        <div style="margin-bottom: 15px;">
                            <strong>카테고리:</strong> 
                            <span style="background: {self.get_category_color()}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">
                                {self.task.category}
                            </span>
                        </div>

                        <div style="margin-bottom: 15px;">
                            <strong>생성일:</strong> {self.task.created_date}
                        </div>

                        {f'<div class="task-content"><strong>일정 내용:</strong><br>{self.escape_html(self.task.content).replace(chr(10), "<br>")}</div>' if self.task.content else '<div style="color: #666; font-style: italic;">내용이 없습니다.</div>'}
                    </div>
                    <div class="footer">
                        🤖 Todolist PM에서 자동 생성 | {current_time}
                    </div>
                </div>
            </body>
            </html>
            """

            mail.HTMLBody = html_body

            # 메일 발송
            mail.Send()

            print(f"개별 작업 메일 발송 완료: {self.task.title}")
            return True

        except Exception as e:
            print(f"개별 작업 메일 발송 중 오류: {e}")
            return False

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

    def on_edit_clicked(self):
        """편집 버튼 클릭 처리"""
        self.edit_task.emit(self.task.id)

    def on_delete_clicked(self):
        """삭제 버튼 클릭 처리"""
        self.delete_task.emit(self.task.id)

    def apply_task_style(self):
        """작업 스타일 적용 (배경색, 중요 표시 등)"""
        # 배경색 설정
        bg_color = "#FFFFFF"
        border_color = "#E0E0E0"

        if self.task.completed:
            bg_color = "#F5F5F5"
            border_color = "#CCCCCC"
        elif self.task.important:
            bg_color = "#FFF3E0"
            border_color = "#FF6B00"

            if self.task.created_date != self.current_date:
                bg_color = "#FFE0B2"
                border_color = "#FF5722"
        elif hasattr(self.task, 'bg_color') and self.task.bg_color != "none":
            try:
                bg_color = self.task.get_bg_color_hex()
                border_color = bg_color
            except Exception as e:
                print(f"배경색 설정 중 오류: {e}")

        border_width = "3px" if (self.task.important and not self.task.completed) else "1px"

        style = f"""
            QFrame {{
                background-color: {bg_color}; 
                border: {border_width} solid {border_color}; 
                border-radius: 8px; 
                margin: 2px;
            }}
            QWidget {{
                background-color: {bg_color};
            }}
            QLabel {{
                background-color: transparent;
            }}
            QPushButton {{
                background-color: transparent;
            }}
            QCheckBox {{
                background-color: transparent;
            }}
        """

        if self.task.important and not self.task.completed:
            style += f"""
            QFrame:hover {{
                background-color: #FFCC80;
                border: 3px solid #FF5722;
            }}
            QFrame:hover QWidget {{
                background-color: #FFCC80;
            }}
            """

        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        """마우스 누름 이벤트 처리"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, 'get_task_index'):
            parent_widget = parent_widget.parent()

        if parent_widget:
            index = parent_widget.get_task_index(self)
            if index >= 0:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(f"task-{index}")
                drag.setMimeData(mime_data)

                pixmap = self.grab()
                painter = QPainter(pixmap)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
                painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
                painter.end()
                drag.setPixmap(pixmap)

                drag.exec(Qt.DropAction.MoveAction)


class TaskListWidget(QScrollArea):
    """작업 목록 위젯"""

    # 커스텀 시그널
    task_edited = pyqtSignal()

    def __init__(self, storage_manager):
        """작업 목록 위젯 초기화"""
        super().__init__()

        self.storage_manager = storage_manager
        self.tasks = []
        self.current_date = ""
        self.drag_source_index = -1
        self.drag_target_index = -1
        self.saved_scroll_position = 0  # 스크롤 위치 저장

        # 드래그 앤 드롭 활성화
        self.setAcceptDrops(True)

        # 스크롤 영역 설정
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # 컨테이너 위젯
        self.container = QWidget()
        self.setWidget(self.container)

        # 레이아웃
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(5)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 빈 상태 메시지
        self.create_empty_label()

    def create_empty_label(self):
        """빈 상태 메시지 라벨 생성"""
        try:
            self.empty_label = QLabel("작업이 없습니다. '새 작업' 버튼을 클릭하여 작업을 추가하세요.")
            self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.empty_label.setStyleSheet("color: #9E9E9E; font-size: 14px; padding: 20px;")
            self.layout.addWidget(self.empty_label)
        except Exception as e:
            print(f"빈 라벨 생성 중 오류 발생: {e}")

    def save_scroll_position(self):
        """현재 스크롤 위치 저장"""
        self.saved_scroll_position = self.verticalScrollBar().value()

    def restore_scroll_position(self):
        """저장된 스크롤 위치 복원"""
        self.verticalScrollBar().setValue(self.saved_scroll_position)

    def get_task_index(self, task_widget):
        """작업 위젯의 인덱스 반환 (해당 날짜 작업만 기준)"""
        try:
            date_only_tasks = [t for t in self.tasks if t.created_date == self.current_date]
            widget_task_id = task_widget.task.id

            for i, task in enumerate(date_only_tasks):
                if task.id == widget_task_id:
                    return i

        except Exception as e:
            print(f"작업 인덱스 찾기 중 오류: {e}")
        return -1

    def load_tasks(self, tasks, current_date):
        """작업 목록 로드"""
        try:
            # 스크롤 위치 저장
            self.save_scroll_position()

            # 기존 작업 위젯 제거
            self.clear_tasks()

            self.tasks = tasks
            self.current_date = current_date

            # 빈 라벨이 없으면 새로 생성
            if not hasattr(self, 'empty_label') or self.empty_label is None:
                self.create_empty_label()

            if tasks:
                try:
                    # 작업이 있으면 빈 라벨 숨기기
                    if self.empty_label is not None:
                        self.empty_label.hide()
                except (RuntimeError, AttributeError) as e:
                    print(f"빈 라벨 숨기기 중 오류: {e}")
                    self.create_empty_label()
                    self.empty_label.hide()

                # 작업 위젯 추가
                for task in tasks:
                    try:
                        task_widget = TaskItemWidget(task, current_date, self.storage_manager)

                        # 시그널 연결
                        task_widget.task_toggled.connect(self.on_task_toggled)
                        task_widget.edit_task.connect(self.on_edit_task)
                        task_widget.delete_task.connect(self.on_delete_task)

                        self.layout.addWidget(task_widget)
                    except Exception as e:
                        print(f"작업 위젯 추가 중 오류: {e}")
            else:
                try:
                    # 작업이 없으면 빈 라벨 표시
                    if self.empty_label is not None:
                        self.empty_label.show()
                except (RuntimeError, AttributeError) as e:
                    print(f"빈 라벨 표시 중 오류: {e}")
                    self.create_empty_label()
                    self.empty_label.show()

            # 스크롤 위치 복원
            self.restore_scroll_position()

        except Exception as e:
            print(f"작업 목록 로드 중 오류 발생: {e}")

    def clear_tasks(self):
        """작업 위젯 모두 제거"""
        try:
            # 빈 라벨을 제외한 모든 위젯 제거
            while self.layout.count() > 0:
                item = self.layout.takeAt(0)
                if item is None:
                    continue

                widget = item.widget()
                if widget is None:
                    continue

                if hasattr(self, 'empty_label') and widget == self.empty_label:
                    continue

                try:
                    widget.setParent(None)
                    widget.deleteLater()
                except RuntimeError:
                    pass

            # 빈 라벨이 제거되었을 수 있으므로 재확인
            if not hasattr(self, 'empty_label') or self.empty_label is None:
                self.create_empty_label()

            # 빈 라벨을 레이아웃에 다시 추가
            self.layout.addWidget(self.empty_label)

        except Exception as e:
            print(f"작업 위젯 제거 중 오류 발생: {e}")

    def on_task_toggled(self, task_id, completed):
        """작업 완료 상태 변경 처리"""
        try:
            # 스크롤 위치 저장
            self.save_scroll_position()

            # 작업 찾기
            for task in self.tasks:
                if task.id == task_id:
                    # 작업 상태 업데이트
                    task.completed = completed
                    self.storage_manager.update_task(task_id, task)

                    # 작업 순서 재정렬 (완료/미완료 및 중요도 고려)
                    self.reorder_tasks_by_priority(task)

                    self.task_edited.emit()
                    break

            # 스크롤 위치 복원
            self.restore_scroll_position()

        except Exception as e:
            print(f"작업 완료 상태 변경 중 오류 발생: {e}")

    def reorder_tasks_by_priority(self, changed_task):
        """작업 순서를 우선순위에 따라 재정렬 (완료 상태 변경 시 호출)"""
        try:
            # 해당 날짜의 작업들만 필터링
            date_tasks = [t for t in self.tasks if t.created_date == changed_task.created_date]

            if len(date_tasks) <= 1:
                return

            # 작업을 4개 그룹으로 분리
            important_incomplete = [t for t in date_tasks if t.important and not t.completed]
            normal_incomplete = [t for t in date_tasks if not t.important and not t.completed]
            important_completed = [t for t in date_tasks if t.important and t.completed]
            normal_completed = [t for t in date_tasks if not t.important and t.completed]

            # 각 그룹 내에서 기존 순서 유지 (order 기준 정렬)
            important_incomplete.sort(key=lambda x: getattr(x, 'order', 999))
            normal_incomplete.sort(key=lambda x: getattr(x, 'order', 999))
            important_completed.sort(key=lambda x: getattr(x, 'order', 999))
            normal_completed.sort(key=lambda x: getattr(x, 'order', 999))

            # 새로운 순서 할당
            order_counter = 1

            # 1. 중요 미완료 작업들 (최우선)
            for task in important_incomplete:
                task.order = order_counter
                order_counter += 1

            # 2. 일반 미완료 작업들
            for task in normal_incomplete:
                task.order = order_counter
                order_counter += 1

            # 3. 중요 완료 작업들
            for task in important_completed:
                task.order = order_counter
                order_counter += 1

            # 4. 일반 완료 작업들 (최하위)
            for task in normal_completed:
                task.order = order_counter
                order_counter += 1

            # 저장소에 변경사항 반영
            for task in date_tasks:
                self.storage_manager.update_task(task.id, task)

            # 즉시 저장
            self.storage_manager.save_data()

            status = "완료" if changed_task.completed else "미완료"
            importance = "중요" if changed_task.important else "일반"
            print(f"{importance} 작업 '{changed_task.title}'이 {status} 상태로 변경되어 우선순위에 따라 재정렬됨")

        except Exception as e:
            print(f"작업 우선순위 재정렬 중 오류: {e}")
            import traceback
            traceback.print_exc()

    def move_task_to_bottom(self, completed_task):
        """완료된 작업을 해당 날짜 작업 목록의 맨 아래로 이동 (중요도 고려)"""
        try:
            # 해당 날짜의 작업들만 필터링
            date_tasks = [t for t in self.tasks if t.created_date == completed_task.created_date]

            if len(date_tasks) <= 1:
                return  # 작업이 1개 이하면 이동할 필요 없음

            # 작업을 4개 그룹으로 분리
            important_incomplete = [t for t in date_tasks if t.important and not t.completed]
            normal_incomplete = [t for t in date_tasks if not t.important and not t.completed]
            important_completed = [t for t in date_tasks if t.important and t.completed]
            normal_completed = [t for t in date_tasks if not t.important and t.completed]

            # 각 그룹 내에서 기존 순서 유지 (order 기준 정렬)
            important_incomplete.sort(key=lambda x: getattr(x, 'order', 999))
            normal_incomplete.sort(key=lambda x: getattr(x, 'order', 999))
            important_completed.sort(key=lambda x: getattr(x, 'order', 999))
            normal_completed.sort(key=lambda x: getattr(x, 'order', 999))

            # 새로운 순서 할당
            # 1. 중요 미완료 작업들 (맨 위)
            order_counter = 1
            for task in important_incomplete:
                task.order = order_counter
                order_counter += 1

            # 2. 일반 미완료 작업들
            for task in normal_incomplete:
                task.order = order_counter
                order_counter += 1

            # 3. 중요 완료 작업들
            for task in important_completed:
                task.order = order_counter
                order_counter += 1

            # 4. 일반 완료 작업들 (맨 아래)
            for task in normal_completed:
                task.order = order_counter
                order_counter += 1

            # 저장소에 변경사항 반영
            for task in date_tasks:
                self.storage_manager.update_task(task.id, task)

            # 즉시 저장
            self.storage_manager.save_data()

            status = "완료" if completed_task.completed else "미완료"
            importance = "중요" if completed_task.important else "일반"
            print(f"{importance} 작업 '{completed_task.title}'이 {status} 상태로 변경되어 적절한 위치로 이동")

        except Exception as e:
            print(f"작업 이동 중 오류: {e}")
            import traceback
            traceback.print_exc()

    def on_edit_task(self, task_id):
        """작업 편집 대화상자 표시"""
        try:
            # 스크롤 위치 저장
            self.save_scroll_position()

            # 작업 찾기
            for task in self.tasks:
                if task.id == task_id:
                    # 편집 대화상자 표시
                    dialog = TaskForm(self.storage_manager, self.current_date, task)
                    if dialog.exec():
                        self.task_edited.emit()
                    break

            # 스크롤 위치 복원
            self.restore_scroll_position()

        except Exception as e:
            print(f"작업 편집 중 오류 발생: {e}")

    def on_delete_task(self, task_id):
        """작업 삭제 확인 및 처리"""
        try:
            # 스크롤 위치 저장
            self.save_scroll_position()

            # 확인 메시지 표시
            reply = QMessageBox.question(
                self,
                "작업 삭제",
                "이 작업을 삭제하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 작업 삭제
                if self.storage_manager.delete_task(task_id):
                    self.task_edited.emit()

            # 스크롤 위치 복원
            self.restore_scroll_position()

        except Exception as e:
            print(f"작업 삭제 중 오류 발생: {e}")

    def reorder_tasks(self, source_index, target_index):
        """작업 순서 변경"""
        try:
            # 스크롤 위치 저장
            self.save_scroll_position()

            # 해당 날짜의 작업만 필터링
            date_only_tasks = [t for t in self.tasks if t.created_date == self.current_date]

            # 인덱스 범위 검사
            if source_index < 0 or source_index >= len(date_only_tasks):
                print(f"잘못된 소스 인덱스: {source_index}, 날짜별 작업 수: {len(date_only_tasks)}")
                return
            if target_index < 0 or target_index >= len(date_only_tasks):
                print(f"잘못된 타겟 인덱스: {target_index}, 날짜별 작업 수: {len(date_only_tasks)}")
                return
            if source_index == target_index:
                return

            print(f"UI에서 순서 변경 요청: {source_index} -> {target_index}")

            # 저장소에서 순서 변경 처리
            success = self.storage_manager.reorder_tasks(self.current_date, source_index, target_index)

            if success:
                # 즉시 저장
                self.storage_manager.save_data()
                print("데이터 즉시 저장 완료")

                # UI 업데이트 - 저장소에서 다시 데이터 가져오기
                updated_tasks = self.storage_manager.get_tasks_by_date(self.current_date)
                self.load_tasks(updated_tasks, self.current_date)

                # 변경 알림
                self.task_edited.emit()

                print(f"UI 작업 순서 변경 완료: {source_index} -> {target_index}")
            else:
                print("작업 순서 변경 실패")

            # 스크롤 위치 복원
            self.restore_scroll_position()

        except Exception as e:
            print(f"UI 작업 순서 변경 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def get_task_widget_at_position(self, pos):
        """주어진 위치의 작업 위젯과 인덱스 반환"""
        try:
            # 컨테이너 위젯 내부 위치로 변환
            container_pos = self.container.mapFromParent(pos)

            # 해당 날짜의 작업만 필터링
            date_only_tasks = [t for t in self.tasks if t.created_date == self.current_date]

            # 위치에 있는 위젯 찾기
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                if item is None:
                    continue

                widget = item.widget()
                if widget is None or (hasattr(self, 'empty_label') and widget == self.empty_label):
                    continue

                # 위젯의 영역 확인
                rect = widget.geometry()
                if rect.contains(container_pos):
                    # 실제 작업 인덱스 계산
                    widget_task_id = widget.task.id
                    for task_idx, task in enumerate(date_only_tasks):
                        if task.id == widget_task_id:
                            return (widget, task_idx)

        except Exception as e:
            print(f"작업 위젯 찾기 중 오류 발생: {e}")

        return (None, -1)

    # 드래그 앤 드롭 이벤트 처리
    def dragEnterEvent(self, event):
        """드래그 시작 이벤트 처리"""
        try:
            if event.mimeData().hasText() and event.mimeData().text().startswith("task-"):
                source_index_str = event.mimeData().text().replace("task-", "")
                self.drag_source_index = int(source_index_str)

                date_only_tasks = [t for t in self.tasks if t.created_date == self.current_date]

                if 0 <= self.drag_source_index < len(date_only_tasks):
                    event.accept()
                    print(f"드래그 시작: 인덱스 {self.drag_source_index}")
                else:
                    print(f"드래그 인덱스 범위 오류: {self.drag_source_index}")
                    event.ignore()
            else:
                event.ignore()
        except Exception as e:
            print(f"드래그 시작 이벤트 처리 중 오류: {e}")
            event.ignore()

    def dragMoveEvent(self, event):
        """드래그 이동 이벤트 처리"""
        try:
            if self.drag_source_index < 0:
                event.ignore()
                return

            widget, target_index = self.get_task_widget_at_position(event.position().toPoint())

            if widget is not None and target_index >= 0:
                self.drag_target_index = target_index

                # 모든 위젯의 스타일 초기화
                for i in range(self.layout.count()):
                    item = self.layout.itemAt(i)
                    if item and item.widget() and hasattr(item.widget(), 'apply_task_style'):
                        item.widget().apply_task_style()

                # 대상 위젯 강조
                if hasattr(widget, 'apply_task_style'):
                    widget.setStyleSheet(widget.styleSheet() + " border: 2px dashed #4285F4;")

                event.accept()
            else:
                self.drag_target_index = -1
                event.ignore()
        except Exception as e:
            print(f"드래그 이동 이벤트 처리 중 오류: {e}")
            event.ignore()

    def dropEvent(self, event):
        """드롭 이벤트 처리"""
        try:
            print(f"드롭 이벤트: 소스={self.drag_source_index}, 타겟={self.drag_target_index}")

            if (self.drag_source_index >= 0 and self.drag_target_index >= 0 and
                    self.drag_source_index != self.drag_target_index):

                # 작업 순서 변경
                self.reorder_tasks(self.drag_source_index, self.drag_target_index)
                event.accept()
            else:
                event.ignore()

            # 상태 초기화
            self.drag_source_index = -1
            self.drag_target_index = -1

            # 모든 위젯 스타일 복원
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                if item and item.widget() and hasattr(item.widget(), 'apply_task_style'):
                    item.widget().apply_task_style()

        except Exception as e:
            print(f"드롭 이벤트 처리 중 오류: {e}")
            event.ignore()

    def dragLeaveEvent(self, event):
        """드래그 떠남 이벤트 처리"""
        try:
            # 모든 위젯 스타일 복원
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                if item and item.widget() and hasattr(item.widget(), 'apply_task_style'):
                    item.widget().apply_task_style()
        except Exception as e:
            print(f"드래그 떠남 이벤트 처리 중 오류: {e}")