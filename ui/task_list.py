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

    def __init__(self, task, current_date):
        """작업 항목 위젯 초기화

        Args:
            task (Task): 표시할 작업 객체
            current_date (str): 현재 선택된 날짜
        """
        super().__init__()

        self.task = task
        self.current_date = current_date

        # 스타일 설정 - PyQt6 호환성 수정
        self.setFrameShape(QFrame.Shape.StyledPanel)
        # QFrame.Shadow.Raised 대신 정수 값 사용
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

        # 카테고리 라벨
        category_label = QLabel(self.task.category)
        category_label.setStyleSheet(
            f"color: white; background-color: {self.get_category_color()}; "
            f"padding: 2px 5px; border-radius: 3px; font-size: 10px;"
        )
        category_label.setMaximumHeight(20)
        title_layout.addWidget(category_label)

        # 제목 라벨
        title_label = QLabel(self.task.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        if self.task.completed:
            title_label.setStyleSheet("text-decoration: line-through; color: #9E9E9E; font-size: 14px;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 다른 날짜의 작업인 경우 날짜 표시
        if self.task.created_date != self.current_date:
            date_label = QLabel(self.task.created_date)
            date_label.setStyleSheet("color: #9E9E9E; font-size: 10px;")
            title_layout.addWidget(date_label)

        info_layout.addLayout(title_layout)

        # 내용 라벨 (있는 경우에만)
        if self.task.content:
            content_label = QLabel(self.task.content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #616161; font-size: 12px;")
            if self.task.completed:
                content_label.setStyleSheet("color: #9E9E9E; font-size: 12px;")
            info_layout.addWidget(content_label)

        layout.addLayout(info_layout, stretch=1)

        # 중요 버튼
        self.important_button = QPushButton("★" if self.task.important else "☆")
        self.important_button.setCheckable(True)
        self.important_button.setChecked(self.task.important)
        self.important_button.setStyleSheet(
            "background: transparent; border: none; font-size: 16px; color: #FFB300;"
        )
        self.important_button.setToolTip("중요 표시")
        self.important_button.setMaximumWidth(30)
        self.important_button.toggled.connect(self.on_important_toggled)
        layout.addWidget(self.important_button)

        # 편집 버튼
        edit_button = QPushButton("편집")
        edit_button.setStyleSheet(
            "background: transparent; border: 1px solid #CCCCCC; border-radius: 3px; "
            "padding: 2px; font-size: 11px;"
        )
        edit_button.setToolTip("편집")
        edit_button.setMaximumWidth(40)
        edit_button.clicked.connect(self.on_edit_clicked)
        layout.addWidget(edit_button)

        # 삭제 버튼
        delete_button = QPushButton("삭제")
        delete_button.setStyleSheet(
            "background: transparent; border: 1px solid #CCCCCC; border-radius: 3px; "
            "padding: 2px; font-size: 11px; color: #E53935;"
        )
        delete_button.setToolTip("삭제")
        delete_button.setMaximumWidth(40)
        delete_button.clicked.connect(self.on_delete_clicked)
        layout.addWidget(delete_button)

        # 작업 배경색 설정
        self.apply_task_style()
    def get_category_color(self):
        """작업 카테고리에 해당하는 색상 반환"""
        category_colors = {
            "LB": "#4285F4",  # 파란색
            "Tester": "#FBBC05",  # 노란색
            "Handler": "#34A853",  # 녹색
            "ETC": "#EA4335"  # 빨간색
        }
        return category_colors.get(self.task.category, "#9E9E9E")  # 기본값은 회색

    def on_complete_toggled(self, checked):
        """완료 상태 변경 처리"""
        self.task_toggled.emit(self.task.id, checked)

    def on_important_toggled(self, checked):
        """중요 상태 변경 처리"""
        self.important_button.setText("★" if checked else "☆")
        self.task_important_toggled.emit(self.task.id, checked)

    def on_edit_clicked(self):
        """편집 버튼 클릭 처리"""
        self.edit_task.emit(self.task.id)

    def on_delete_clicked(self):
        """삭제 버튼 클릭 처리"""
        self.delete_task.emit(self.task.id)


    def apply_task_style(self):
        """작업 스타일 적용 (배경색, 중요 표시 등)"""
        style = ""

        # 배경색 설정
        bg_color = "#FFFFFF"  # 기본 흰색

        # 중요 작업인 경우 노란색 배경 (날짜 상관없이)
        if self.task.important and not self.task.completed:
            bg_color = "#FFF8E1"  # 연한 노란색
            border_color = "#FFE082"  # 노란색 테두리
        else:
            border_color = "#E0E0E0"  # 기본 테두리

        # 사용자 지정 배경색이 있는 경우
        if hasattr(self.task, 'bg_color') and self.task.bg_color != "none":
            try:
                # 배경색 가져오기
                bg_color = self.task.get_bg_color_hex()
                # 테두리색은 배경색과 비슷하게 설정
                border_color = bg_color
            except Exception as e:
                print(f"배경색 설정 중 오류: {e}")

        # 스타일 문자열 구성
        style = f"""
            background-color: {bg_color}; 
            border: 1px solid {border_color}; 
            border-radius: 5px; 
            margin: 2px;
        """

        self.setStyleSheet(style)

    # TaskItemWidget 클래스에 추가
    def mousePressEvent(self, event):
        """마우스 누름 이벤트 처리"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 드래그 시작 위치 저장
            self.drag_start_position = event.position().toPoint()

            # 인덱스 저장
            self.index = self.property("index")

            # 부모 위젯에 알리기
            if hasattr(self.parent(), 'drag_source_index'):
                self.parent().drag_source_index = self.index

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # 최소 드래그 거리 확인
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # 드래그 시작
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"task-{self.index}")
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
                        task_widget = TaskItemWidget(task, current_date)

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

                if widget == self.empty_label:
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
        """작업 완료 상태 변경 처리

        Args:
            task_id (str): 작업 ID
            completed (bool): 완료 상태
        """
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
        """작업 중요 상태 변경 처리

        Args:
            task_id (str): 작업 ID
            important (bool): 중요 상태
        """
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
        """작업 편집 대화상자 표시

        Args:
            task_id (str): 편집할 작업 ID
        """
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
        """작업 삭제 확인 및 처리

        Args:
            task_id (str): 삭제할 작업 ID
        """
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
        """작업 순서 변경

        Args:
            source_index (int): 원본 인덱스
            target_index (int): 대상 인덱스
        """
        try:
            # 인덱스 범위 검사
            if source_index < 0 or source_index >= len(self.tasks):
                return
            if target_index < 0 or target_index >= len(self.tasks):
                return
            if source_index == target_index:
                return

            # 작업 순서 변경
            task = self.tasks.pop(source_index)
            self.tasks.insert(target_index, task)

            # 저장소에 순서 업데이트
            # 중요: 이 부분은 작업 순서 저장 기능을 구현해야 함
            # 현재는 실제 저장소에는 반영되지 않고 UI에만 반영됨

            # UI 업데이트
            self.reload_tasks()

            # 변경 알림
            self.task_edited.emit()
        except Exception as e:
            print(f"작업 순서 변경 중 오류 발생: {e}")

    def reload_tasks(self):
        """현재 작업 목록 다시 로드"""
        try:
            # 기존 작업 위젯 제거
            self.clear_tasks()

            if self.tasks:
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
                for i, task in enumerate(self.tasks):
                    try:
                        task_widget = TaskItemWidget(task, self.current_date)
                        task_widget.setProperty("index", i)  # 인덱스 저장

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
            print(f"작업 목록 다시 로드 중 오류 발생: {e}")

    def get_task_widget_at(self, pos):
        """주어진 위치의 작업 위젯 반환

        Args:
            pos (QPoint): 마우스 위치

        Returns:
            tuple: (작업 위젯, 인덱스) 또는 (None, -1)
        """
        try:
            # 컨테이너 위젯 내부 위치로 변환
            container_pos = self.container.mapFromParent(pos)

            # 위치에 있는 위젯 찾기
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i)
                if item is None:
                    continue

                widget = item.widget()
                if widget is None or widget == self.empty_label:
                    continue

                # 위젯의 영역 확인
                rect = widget.geometry()
                if rect.contains(container_pos):
                    # 인덱스 반환
                    index = widget.property("index")
                    if index is None:
                        index = i - 1  # empty_label이 있을 경우 조정

                    return (widget, index)
        except Exception as e:
            print(f"작업 위젯 찾기 중 오류 발생: {e}")

        return (None, -1)

    # 드래그 앤 드롭 이벤트 처리
    def dragEnterEvent(self, event):
        """드래그 시작 이벤트 처리"""
        # 내부 드래그만 허용
        if event.source() == self:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """드래그 이동 이벤트 처리"""
        try:
            widget, index = self.get_task_widget_at(event.position().toPoint())

            if widget is not None and index >= 0:
                # 대상 인덱스 저장
                self.drag_target_index = index

                # 위젯 상태 표시
                for i in range(self.layout.count()):
                    item = self.layout.itemAt(i)
                    if item is None:
                        continue

                    w = item.widget()
                    if w is None or w == self.empty_label:
                        continue

                    if w == widget:
                        # 대상 위젯 강조
                        w.setStyleSheet(w.styleSheet() + "border: 2px dashed #4285F4;")
                    else:
                        # 스타일 복원
                        if hasattr(w, 'apply_task_style'):
                            w.apply_task_style()

                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(f"드래그 이동 이벤트 처리 중 오류 발생: {e}")
            event.ignore()

    def dropEvent(self, event):
        """드롭 이벤트 처리"""
        try:
            if self.drag_source_index >= 0 and self.drag_target_index >= 0:
                # 작업 순서 변경
                self.reorder_tasks(self.drag_source_index, self.drag_target_index)

                # 상태 초기화
                self.drag_source_index = -1
                self.drag_target_index = -1

                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(f"드롭 이벤트 처리 중 오류 발생: {e}")
            event.ignore()