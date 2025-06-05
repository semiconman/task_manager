from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton, QCheckBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QColor, QDrag, QPixmap, QPainter
from PyQt6.QtCore import QMimeData

from ui.task_form import TaskForm


class TaskItemWidget(QFrame):
    """작업 항목 위젯"""

    # 커스텀 시그널
    task_toggled = pyqtSignal(str, bool)  # 작업 완료 상태 변경 (id, completed)
    task_important_toggled = pyqtSignal(str, bool)  # 작업 중요 상태 변경 (id, important)
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
        self.storage_manager = storage_manager  # 추가
        self.drag_start_position = QPoint()  # 드래그 시작 위치 초기화

        # 스타일 설정 - PyQt6 호환성 수정
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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 완료 체크박스
        self.complete_checkbox = QCheckBox()
        self.complete_checkbox.setChecked(self.task.completed)
        self.complete_checkbox.toggled.connect(self.on_complete_toggled)
        layout.addWidget(self.complete_checkbox)

        # 작업 정보 영역
        info_layout = QVBoxLayout()

        # 제목 행
        title_layout = QHBoxLayout()

        # 중요 표시 아이콘 (맨 앞에 추가)
        if self.task.important and not self.task.completed:
            important_icon = QLabel("🔥")  # 불꽃 이모지
            important_icon.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                margin-right: 5px;
                border: none;
            """)
            important_icon.setToolTip("중요 작업")
            title_layout.addWidget(important_icon)

        # 카테고리 라벨 - 중요 일정일 때 테두리 제거
        category_label = QLabel(self.task.category)
        if self.task.important and not self.task.completed:
            # 중요 일정: 테두리 없는 스타일
            category_label.setStyleSheet(
                f"color: white; background-color: {self.get_category_color()}; "
                f"padding: 2px 5px; border: none; border-radius: 3px; font-size: 10px;"
            )
        else:
            # 일반 일정: 기본 스타일
            category_label.setStyleSheet(
                f"color: white; background-color: {self.get_category_color()}; "
                f"padding: 2px 5px; border-radius: 3px; font-size: 10px;"
            )
        category_label.setMaximumHeight(20)
        title_layout.addWidget(category_label)

        # 제목 라벨
        title_text = self.task.title
        if self.task.important and not self.task.completed:
            title_text = f"【중요】{self.task.title}"  # 중요 표시 텍스트 추가

        title_label = QLabel(title_text)

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

        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 다른 날짜의 작업인 경우 날짜 표시
        if self.task.created_date != self.current_date:
            date_label = QLabel(self.task.created_date)
            date_label.setStyleSheet("color: #9E9E9E; font-size: 10px; border: none;")
            title_layout.addWidget(date_label)

        info_layout.addLayout(title_layout)

        # 내용 라벨 (있는 경우에만)
        if self.task.content:
            content_label = QLabel(self.task.content)
            content_label.setWordWrap(True)

            if self.task.completed:
                content_label.setStyleSheet("color: #9E9E9E; font-size: 12px; border: none;")
            elif self.task.important:
                content_label.setStyleSheet("""
                    color: #D32F2F; 
                    font-size: 12px; 
                    font-weight: 500;
                    border: none;
                """)
            else:
                content_label.setStyleSheet("color: #616161; font-size: 12px; border: none;")
            info_layout.addWidget(content_label)

        layout.addLayout(info_layout, stretch=1)

        # 중요 버튼 - 중요 일정일 때 테두리 완전 제거
        self.important_button = QPushButton("★" if self.task.important else "☆")
        self.important_button.setCheckable(True)
        self.important_button.setChecked(self.task.important)

        # 중요 버튼 스타일 - 테두리 완전 제거
        if self.task.important:
            self.important_button.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none;
                    outline: none;
                    font-size: 18px; 
                    color: #FFD700;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #FFC107;
                    border: none;
                    outline: none;
                }
                QPushButton:focus {
                    border: none;
                    outline: none;
                }
            """)
        else:
            self.important_button.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none;
                    outline: none;
                    font-size: 16px; 
                    color: #CCCCCC;
                }
                QPushButton:hover {
                    color: #FFD700;
                    border: none;
                    outline: none;
                }
                QPushButton:focus {
                    border: none;
                    outline: none;
                }
            """)

        self.important_button.setToolTip("중요 표시")
        self.important_button.setMaximumWidth(30)
        self.important_button.toggled.connect(self.on_important_toggled)
        layout.addWidget(self.important_button)

        # 편집 버튼 - 중요 일정일 때 테두리 제거
        edit_button = QPushButton("편집")
        if self.task.important and not self.task.completed:
            edit_button.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none;
                    outline: none;
                    border-radius: 3px; 
                    padding: 2px; 
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: rgba(0,0,0,0.1);
                    border: none;
                    outline: none;
                }
                QPushButton:focus {
                    border: none;
                    outline: none;
                }
            """)
        else:
            edit_button.setStyleSheet("""
                background: transparent; 
                border: 1px solid #CCCCCC; 
                border-radius: 3px; 
                padding: 2px; 
                font-size: 11px;
            """)
        edit_button.setToolTip("편집")
        edit_button.setMaximumWidth(40)
        edit_button.clicked.connect(self.on_edit_clicked)
        layout.addWidget(edit_button)

        # 삭제 버튼 - 중요 일정일 때 테두리 제거
        delete_button = QPushButton("삭제")
        if self.task.important and not self.task.completed:
            delete_button.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none;
                    outline: none;
                    border-radius: 3px; 
                    padding: 2px; 
                    font-size: 11px; 
                    color: #E53935;
                }
                QPushButton:hover {
                    background-color: rgba(229,57,53,0.1);
                    border: none;
                    outline: none;
                }
                QPushButton:focus {
                    border: none;
                    outline: none;
                }
            """)
        else:
            delete_button.setStyleSheet("""
                background: transparent; 
                border: 1px solid #CCCCCC; 
                border-radius: 3px; 
                padding: 2px; 
                font-size: 11px; 
                color: #E53935;
            """)
        delete_button.setToolTip("삭제")
        delete_button.setMaximumWidth(40)
        delete_button.clicked.connect(self.on_delete_clicked)
        layout.addWidget(delete_button)

        # 작업 배경색 설정
        self.apply_task_style()

    def get_category_color(self):
        """작업 카테고리에 해당하는 색상 반환"""
        # StorageManager에서 카테고리 정보 가져오기
        if self.storage_manager:
            for category in self.storage_manager.categories:
                if category.name == self.task.category:
                    print(f"카테고리 '{self.task.category}' 색상 찾음: {category.color}")
                    return category.color

        # StorageManager가 없거나 카테고리를 찾지 못한 경우 기본 색상 사용
        default_colors = {
            "LB": "#4285F4",  # 파란색
            "Tester": "#FBBC05",  # 노란색
            "Handler": "#34A853",  # 녹색
            "ETC": "#EA4335"  # 빨간색
        }

        color = default_colors.get(self.task.category, "#9E9E9E")  # 기본값은 회색
        print(f"카테고리 '{self.task.category}' 기본 색상 사용: {color}")
        return color

    def on_complete_toggled(self, checked):
        """완료 상태 변경 처리"""
        self.task_toggled.emit(self.task.id, checked)

    def on_important_toggled(self, checked):
        """중요 상태 변경 처리"""
        # 버튼 텍스트 및 스타일 업데이트
        self.important_button.setText("★" if checked else "☆")

        if checked:
            self.important_button.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none;
                    outline: none;
                    font-size: 18px; 
                    color: #FFD700;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #FFC107;
                    border: none;
                    outline: none;
                }
                QPushButton:focus {
                    border: none;
                    outline: none;
                }
            """)
        else:
            self.important_button.setStyleSheet("""
                QPushButton {
                    background: transparent; 
                    border: none;
                    outline: none;
                    font-size: 16px; 
                    color: #CCCCCC;
                }
                QPushButton:hover {
                    color: #FFD700;
                    border: none;
                    outline: none;
                }
                QPushButton:focus {
                    border: none;
                    outline: none;
                }
            """)

        # 작업 객체 업데이트
        self.task.important = checked

        # UI 전체 스타일 즉시 업데이트
        self.apply_task_style()

        # 제목과 내용 스타일도 업데이트 (전체 UI 다시 그리기)
        self.setParent(None)
        self.setParent(self.parent())

        # 신호 방출
        self.task_important_toggled.emit(self.task.id, checked)

    def on_edit_clicked(self):
        """편집 버튼 클릭 처리"""
        self.edit_task.emit(self.task.id)

    def on_delete_clicked(self):
        """삭제 버튼 클릭 처리"""
        self.delete_task.emit(self.task.id)

    def apply_task_style(self):
        """작업 스타일 적용 (배경색, 중요 표시 등)"""
        # 배경색 설정
        bg_color = "#FFFFFF"  # 기본 흰색
        border_color = "#E0E0E0"  # 기본 테두리
        shadow = ""  # 그림자 효과

        # 완료된 작업
        if self.task.completed:
            bg_color = "#F5F5F5"  # 회색 배경
            border_color = "#CCCCCC"
        # 중요 작업 (미완료) - 주황색 테두리만 유지
        elif self.task.important:
            bg_color = "#FFF3E0"  # 연한 주황 배경
            border_color = "#FF6B00"  # 주황 테두리 (이것만 유지)

            # 다른 날짜의 중요 작업은 더 강조
            if self.task.created_date != self.current_date:
                bg_color = "#FFE0B2"  # 더 진한 주황 배경
                border_color = "#FF5722"  # 더 진한 주황 테두리
        # 사용자 지정 배경색이 있는 경우 (중요하지 않은 작업만)
        elif hasattr(self.task, 'bg_color') and self.task.bg_color != "none":
            try:
                bg_color = self.task.get_bg_color_hex()
                border_color = bg_color
            except Exception as e:
                print(f"배경색 설정 중 오류: {e}")

        # 중요 작업에 대한 특별한 테두리 설정
        border_width = "3px" if (self.task.important and not self.task.completed) else "1px"

        # 스타일 문자열 구성 - 그림자 효과 제거
        style = f"""
            QFrame {{
                background-color: {bg_color}; 
                border: {border_width} solid {border_color}; 
                border-radius: 8px; 
                margin: 2px;
            }}
        """

        # 중요 작업에 호버 효과 - 그림자 제거, 색상만 변경
        if self.task.important and not self.task.completed:
            style += f"""
            QFrame:hover {{
                background-color: #FFCC80;
                border: 3px solid #FF5722;
            }}
            """

        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        """마우스 누름 이벤트 처리"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 드래그 시작 위치 저장
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # 최소 드래그 거리 확인
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # 부모 위젯에서 현재 인덱스 가져오기
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, 'get_task_index'):
            parent_widget = parent_widget.parent()

        if parent_widget:
            index = parent_widget.get_task_index(self)
            if index >= 0:
                # 드래그 시작
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(f"task-{index}")
                drag.setMimeData(mime_data)

                # 반투명 드래그 효과
                pixmap = self.grab()
                painter = QPainter(pixmap)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
                painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
                painter.end()
                drag.setPixmap(pixmap)

                # 드래그 실행
                drag.exec(Qt.DropAction.MoveAction)


class TaskListWidget(QScrollArea):
    """작업 목록 위젯"""

    # 커스텀 시그널
    task_edited = pyqtSignal()  # 작업 편집됨

    def __init__(self, storage_manager):
        """작업 목록 위젯 초기화

        Args:
            storage_manager (StorageManager): 데이터 저장소 관리자
        """
        super().__init__()

        self.storage_manager = storage_manager
        self.tasks = []
        self.current_date = ""
        self.drag_source_index = -1
        self.drag_target_index = -1

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

    def get_task_index(self, task_widget):
        """작업 위젯의 인덱스 반환 (해당 날짜 작업만 기준)"""
        try:
            # 해당 날짜의 작업만 필터링
            date_only_tasks = [t for t in self.tasks if t.created_date == self.current_date]

            # 위젯에서 작업 ID 가져오기
            widget_task_id = task_widget.task.id

            # 해당 날짜 작업에서 인덱스 찾기
            for i, task in enumerate(date_only_tasks):
                if task.id == widget_task_id:
                    return i

        except Exception as e:
            print(f"작업 인덱스 찾기 중 오류: {e}")
        return -1

    def load_tasks(self, tasks, current_date):
        """작업 목록 로드

        Args:
            tasks (list): 표시할 작업 목록
            current_date (str): 현재 선택된 날짜
        """
        try:
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
                    # 오류 발생 시 빈 라벨 재생성
                    self.create_empty_label()
                    self.empty_label.hide()

                # 작업 위젯 추가
                for task in tasks:
                    try:
                        # storage_manager를 TaskItemWidget에 전달
                        task_widget = TaskItemWidget(task, current_date, self.storage_manager)

                        # 시그널 연결
                        task_widget.task_toggled.connect(self.on_task_toggled)
                        task_widget.task_important_toggled.connect(self.on_task_important_toggled)
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
                    # 오류 발생 시 빈 라벨 재생성
                    self.create_empty_label()
                    self.empty_label.show()
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
            # 작업 찾기
            for task in self.tasks:
                if task.id == task_id:
                    # 작업 상태 업데이트
                    task.completed = completed
                    self.storage_manager.update_task(task_id, task)
                    self.task_edited.emit()
                    break
        except Exception as e:
            print(f"작업 완료 상태 변경 중 오류 발생: {e}")

    def on_task_important_toggled(self, task_id, important):
        """작업 중요 상태 변경 처리"""
        try:
            # 작업 찾기
            for task in self.tasks:
                if task.id == task_id:
                    # 작업 상태 업데이트
                    task.important = important
                    self.storage_manager.update_task(task_id, task)
                    self.task_edited.emit()
                    break
        except Exception as e:
            print(f"작업 중요 상태 변경 중 오류 발생: {e}")

    def on_edit_task(self, task_id):
        """작업 편집 대화상자 표시"""
        try:
            # 작업 찾기
            for task in self.tasks:
                if task.id == task_id:
                    # 편집 대화상자 표시
                    dialog = TaskForm(self.storage_manager, self.current_date, task)
                    if dialog.exec():
                        self.task_edited.emit()
                    break
        except Exception as e:
            print(f"작업 편집 중 오류 발생: {e}")

    def on_delete_task(self, task_id):
        """작업 삭제 확인 및 처리"""
        try:
            # 확인 메시지 표시
            reply = QMessageBox.question(
                self,
                "작업 삭제",
                "이 작업을 삭제하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 작업 삭제
                if self.storage_manager.delete_task(task_id):
                    self.task_edited.emit()
        except Exception as e:
            print(f"작업 삭제 중 오류 발생: {e}")

    def reorder_tasks(self, source_index, target_index):
        """작업 순서 변경"""
        try:
            # 해당 날짜의 작업만 필터링 (중요한 다른 날짜 작업 제외)
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
            print(f"변경 전 UI 작업 목록:")
            for i, task in enumerate(date_only_tasks):
                print(f"  UI {i}: {task.title}")

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
                    # 실제 작업 인덱스 계산 (해당 날짜 기준)
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
            # 마임 데이터 확인
            if event.mimeData().hasText() and event.mimeData().text().startswith("task-"):
                # 소스 인덱스 추출
                source_index_str = event.mimeData().text().replace("task-", "")
                self.drag_source_index = int(source_index_str)

                # 해당 날짜 작업 수 확인
                date_only_tasks = [t for t in self.tasks if t.created_date == self.current_date]

                if 0 <= self.drag_source_index < len(date_only_tasks):
                    event.accept()
                    print(f"드래그 시작: 인덱스 {self.drag_source_index} (해당 날짜 작업 수: {len(date_only_tasks)})")
                else:
                    print(f"드래그 인덱스 범위 오류: {self.drag_source_index}, 작업 수: {len(date_only_tasks)}")
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

            # 현재 위치의 작업 위젯 찾기
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