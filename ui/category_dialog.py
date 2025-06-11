#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QColorDialog,
    QMessageBox, QDialogButtonBox, QFrame, QButtonGroup, QRadioButton, QGroupBox,
    QTextEdit, QTabWidget, QWidget, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon

from models.category import Category


class CategoryListItem(QListWidgetItem):
    """카테고리 리스트 아이템"""

    def __init__(self, category):
        """카테고리 아이템 초기화

        Args:
            category (Category): 카테고리 객체
        """
        super().__init__()

        self.category = category

        # 템플릿 개수 표시
        template_count = len(category.templates) if hasattr(category, 'templates') else 0
        display_text = f"{category.name}"
        if template_count > 0:
            display_text += f" (템플릿 {template_count}개)"

        self.setText(display_text)

        # 색상 표시
        self.setForeground(QColor("white"))
        self.setBackground(QColor(category.color))

        # ETC 카테고리는 삭제 불가 표시
        if category.name == "ETC":
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.setToolTip("ETC 카테고리는 삭제할 수 없습니다 (기본 카테고리)")
        else:
            self.setToolTip(f"카테고리: {category.name}")


class CategoryListWidget(QListWidget):
    """드래그 앤 드롭을 지원하는 카테고리 리스트 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage_manager = None
        self.parent_dialog = None

        # 드래그 앤 드롭 설정
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def setup_references(self, storage_manager, parent_dialog):
        """참조 객체들 설정"""
        self.storage_manager = storage_manager
        self.parent_dialog = parent_dialog

    def dropEvent(self, event):
        """드롭 이벤트 처리"""
        if not self.storage_manager or not self.parent_dialog:
            event.ignore()
            return

        if event.source() == self:
            # 드롭된 아이템들 가져오기
            items = self.selectedItems()
            if not items:
                event.ignore()
                return

            # 드롭 위치 계산
            drop_row = self.indexAt(event.position().toPoint()).row()
            if drop_row == -1:
                drop_row = self.count()

            # 현재 아이템 위치
            current_row = self.row(items[0])

            # 순서 변경
            if current_row != drop_row and current_row != -1:
                # 실제 드롭 위치 조정
                target_row = drop_row
                if current_row < drop_row:
                    target_row -= 1

                print(f"카테고리 드래그 앤 드롭: {current_row} -> {target_row}")

                try:
                    # StorageManager에서 순서 변경
                    if self.storage_manager.reorder_categories(current_row, target_row):
                        # 부모 다이얼로그의 카테고리 목록 새로고침
                        self.parent_dialog.load_categories()
                        # 즉시 저장
                        self.storage_manager.save_data()
                        print("카테고리 순서 변경 완료 및 저장됨")
                        event.accept()
                    else:
                        print("카테고리 순서 변경 실패")
                        event.ignore()
                except Exception as e:
                    print(f"카테고리 순서 변경 중 오류: {e}")
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()


class TemplateWidget(QWidget):
    """템플릿 관리 위젯"""

    def __init__(self, category, storage_manager):
        super().__init__()
        self.category = category
        self.storage_manager = storage_manager  # StorageManager 직접 참조
        self.init_ui()
        self.load_templates()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 상단: 템플릿 목록
        template_label = QLabel(f"'{self.category.name}' 카테고리 템플릿:")
        template_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(template_label)

        # 템플릿 리스트
        self.template_list = QListWidget()
        self.template_list.setMaximumHeight(150)
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)

        # 템플릿 삭제 버튼
        delete_template_btn = QPushButton("선택한 템플릿 삭제")
        delete_template_btn.clicked.connect(self.delete_template)
        layout.addWidget(delete_template_btn)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 하단: 새 템플릿 추가
        add_template_label = QLabel("새 템플릿 추가:")
        add_template_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(add_template_label)

        # 템플릿 제목
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("제목:"))
        self.template_title_edit = QLineEdit()
        self.template_title_edit.setPlaceholderText("템플릿 제목")
        title_layout.addWidget(self.template_title_edit)
        layout.addLayout(title_layout)

        # 템플릿 내용
        content_label = QLabel("내용:")
        layout.addWidget(content_label)
        self.template_content_edit = QTextEdit()
        self.template_content_edit.setPlaceholderText("템플릿 내용 (선택사항)")
        self.template_content_edit.setMaximumHeight(80)
        layout.addWidget(self.template_content_edit)

        # 추가 버튼
        add_template_btn = QPushButton("템플릿 추가")
        add_template_btn.clicked.connect(self.add_template)
        layout.addWidget(add_template_btn)

    def load_templates(self):
        """템플릿 목록 로드"""
        self.template_list.clear()

        if hasattr(self.category, 'templates'):
            for i, template in enumerate(self.category.templates):
                item_text = template.get('title', f'템플릿 {i + 1}')
                if template.get('content'):
                    item_text += f" - {template['content'][:20]}..."

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, i)  # 인덱스 저장
                self.template_list.addItem(item)

    def on_template_selected(self, item):
        """템플릿 선택 시 미리보기"""
        index = item.data(Qt.ItemDataRole.UserRole)
        if hasattr(self.category, 'templates') and 0 <= index < len(self.category.templates):
            template = self.category.templates[index]
            self.template_title_edit.setText(template.get('title', ''))
            self.template_content_edit.setText(template.get('content', ''))

    def add_template(self):
        """템플릿 추가"""
        title = self.template_title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "입력 오류", "템플릿 제목을 입력하세요.")
            return

        content = self.template_content_edit.toPlainText().strip()

        print(f"템플릿 추가 시작: 제목='{title}', 내용='{content}'")

        # templates 속성이 없으면 초기화
        if not hasattr(self.category, 'templates'):
            self.category.templates = []
            print(f"카테고리 '{self.category.name}'에 빈 templates 리스트 생성")

        # 템플릿 추가
        self.category.add_template(title, content)

        print(f"템플릿 추가 후 '{self.category.name}' 카테고리 템플릿 수: {len(self.category.templates)}")
        print(f"추가된 템플릿: {self.category.templates[-1]}")

        # StorageManager에서 강제 저장
        print("StorageManager를 통한 강제 저장 시작...")
        self.storage_manager.categories_changed = True

        # _save_categories 직접 호출로 강제 저장
        try:
            self.storage_manager._save_categories()
            print("강제 저장 완료!")
        except Exception as e:
            print(f"강제 저장 실패: {e}")
            import traceback
            traceback.print_exc()

        # UI 업데이트
        self.load_templates()
        self.template_title_edit.clear()
        self.template_content_edit.clear()

        QMessageBox.information(self, "성공", f"템플릿 '{title}'이 추가되었습니다.")

    def delete_template(self):
        """선택한 템플릿 삭제"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "선택 없음", "삭제할 템플릿을 선택하세요.")
            return

        index = current_item.data(Qt.ItemDataRole.UserRole)
        template_title = self.category.templates[index].get('title', f'템플릿 {index + 1}')

        reply = QMessageBox.question(
            self, "템플릿 삭제",
            f"'{template_title}' 템플릿을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes  # 기본값을 Yes로 설정
        )

        if reply == QMessageBox.StandardButton.Yes:
            print(f"템플릿 삭제 시작: '{template_title}'")

            if self.category.remove_template(index):
                print(f"템플릿 삭제 후 '{self.category.name}' 카테고리 템플릿 수: {len(self.category.templates)}")

                # StorageManager에서 강제 저장
                print("StorageManager를 통한 강제 저장 시작...")
                self.storage_manager.categories_changed = True

                # _save_categories 직접 호출로 강제 저장
                try:
                    self.storage_manager._save_categories()
                    print("강제 저장 완료!")
                except Exception as e:
                    print(f"강제 저장 실패: {e}")
                    import traceback
                    traceback.print_exc()

                self.load_templates()
                self.template_title_edit.clear()
                self.template_content_edit.clear()

                QMessageBox.information(self, "성공", f"템플릿 '{template_title}'이 삭제되었습니다.")


class CategoryDialog(QDialog):
    """카테고리 관리 대화상자"""

    # 미리 정의된 색상 샘플
    COLOR_SAMPLES = {
        "red": "#F44336",  # 빨강
        "pink": "#E91E63",  # 분홍
        "purple": "#9C27B0",  # 보라
        "deep_purple": "#673AB7",  # 진한 보라
        "indigo": "#3F51B5",  # 남색
        "blue": "#2196F3",  # 파랑
        "light_blue": "#03A9F4",  # 연한 파랑
        "cyan": "#00BCD4",  # 청록
        "teal": "#009688",  # 청록색
        "green": "#4CAF50",  # 녹색
        "light_green": "#8BC34A",  # 연한 녹색
        "lime": "#CDDC39",  # 라임
        "yellow": "#FFEB3B",  # 노랑
        "amber": "#FFC107",  # 황색
        "orange": "#FF9800",  # 주황
        "deep_orange": "#FF5722",  # 진한 주황
        "brown": "#795548",  # 갈색
        "grey": "#9E9E9E",  # 회색
        "blue_grey": "#607D8B"  # 청회색
    }

    def __init__(self, storage_manager):
        """카테고리 관리 대화상자 초기화

        Args:
            storage_manager (StorageManager): 데이터 저장소 관리자
        """
        super().__init__()

        self.storage_manager = storage_manager

        # 대화상자 설정
        self.setWindowTitle("카테고리 관리")
        self.setMinimumSize(700, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # UI 초기화
        self.init_ui()

        # 카테고리 목록 로드
        self.load_categories()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 첫 번째 탭: 카테고리 기본 관리
        self.create_category_tab()

        # 두 번째 탭: 템플릿 관리 (동적으로 생성)
        self.update_template_tabs()

        # 닫기 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def create_category_tab(self):
        """카테고리 기본 관리 탭 생성"""
        category_tab = QWidget()
        layout = QVBoxLayout(category_tab)

        # 카테고리 목록
        list_label = QLabel("카테고리 목록:")
        list_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(list_label)

        # 순서 변경 안내
        order_info = QLabel("💡 드래그 앤 드롭으로 카테고리 순서를 변경할 수 있습니다")
        order_info.setStyleSheet("color: #666666; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(order_info)

        # 카테고리 리스트 (드래그 앤 드롭 지원)
        self.category_list = CategoryListWidget()
        self.category_list.setup_references(self.storage_manager, self)
        self.category_list.itemClicked.connect(self.on_category_selected)
        layout.addWidget(self.category_list)

        # 새 카테고리 추가 영역
        add_frame = QFrame()
        add_frame.setFrameShape(QFrame.Shape.StyledPanel)
        add_frame.setFrameShadow(QFrame.Shadow.Sunken)
        add_frame.setStyleSheet("background-color: #F5F5F5; padding: 10px;")

        add_layout = QVBoxLayout(add_frame)

        add_label = QLabel("새 카테고리 추가:")
        add_label.setStyleSheet("font-weight: bold;")
        add_layout.addWidget(add_label)

        # 이름 입력
        name_layout = QHBoxLayout()
        name_label = QLabel("이름:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("카테고리 이름")

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        add_layout.addLayout(name_layout)

        # 색상 선택 그룹
        color_group = QGroupBox("색상 선택")
        color_layout = QVBoxLayout(color_group)

        # 색상 라디오 버튼 그룹
        self.color_radio_group = QButtonGroup(self)
        self.color_radios = {}

        # 색상 그리드 레이아웃 (4열)
        grid_layout = QHBoxLayout()
        col_count = 0
        col_max = 4
        current_col_layout = QVBoxLayout()

        # 색상 샘플 버튼 생성
        for color_code, color_hex in self.COLOR_SAMPLES.items():
            # 새 열 시작
            if col_count >= col_max:
                grid_layout.addLayout(current_col_layout)
                current_col_layout = QVBoxLayout()
                col_count = 0

            # 라디오 버튼 생성
            radio = QRadioButton("")
            radio.setToolTip(color_code.replace("_", " ").title())

            # 색상 미리보기 스타일 설정
            radio.setStyleSheet(f"""
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: {color_hex};
                    border: 1px solid #CCCCCC;
                }}
                QRadioButton::indicator:checked {{
                    border: 2px solid #000000;
                }}
            """)

            self.color_radio_group.addButton(radio)
            self.color_radios[color_hex] = radio
            current_col_layout.addWidget(radio)
            col_count += 1

        # 마지막 열 추가
        if current_col_layout.count() > 0:
            grid_layout.addLayout(current_col_layout)

        color_layout.addLayout(grid_layout)
        add_layout.addWidget(color_group)

        # 첫 번째 색상 선택
        if self.color_radios:
            first_radio = next(iter(self.color_radios.values()))
            first_radio.setChecked(True)

        # 추가 버튼
        add_button = QPushButton("추가")
        add_button.clicked.connect(self.add_category)
        add_layout.addWidget(add_button)

        layout.addWidget(add_frame)

        # 삭제 버튼
        delete_button = QPushButton("선택한 카테고리 삭제")
        delete_button.clicked.connect(self.delete_category)
        layout.addWidget(delete_button)

        # 첫 번째 탭에 추가
        self.tab_widget.addTab(category_tab, "카테고리 관리")

    def on_category_selected(self, item):
        """카테고리 선택 시 템플릿 탭 업데이트"""
        self.update_template_tabs()

    def update_template_tabs(self):
        """템플릿 관리 탭들 업데이트"""
        # 기존 템플릿 탭들 제거 (첫 번째 탭 제외)
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(1)

        # 선택된 카테고리가 있으면 해당 카테고리의 템플릿 탭 추가
        selected_items = self.category_list.selectedItems()
        if selected_items:
            selected_category = selected_items[0].category
            # StorageManager를 TemplateWidget에 전달
            template_widget = TemplateWidget(selected_category, self.storage_manager)
            self.tab_widget.addTab(template_widget, f"'{selected_category.name}' 템플릿")

    def load_categories(self):
        """카테고리 목록 로드"""
        self.category_list.clear()

        for category in self.storage_manager.categories:
            # templates 속성이 없는 기존 카테고리를 위한 보완
            if not hasattr(category, 'templates'):
                category.templates = []

            item = CategoryListItem(category)
            self.category_list.addItem(item)

    def get_selected_color(self):
        """선택된 색상 코드 반환"""
        for color_hex, radio in self.color_radios.items():
            if radio.isChecked():
                print(f"선택된 색상: {color_hex}")
                return color_hex
        # 기본값 반환
        default_color = list(self.COLOR_SAMPLES.values())[0]
        print(f"기본 색상 사용: {default_color}")
        return default_color

    def add_category(self):
        """새 카테고리 추가"""
        try:
            name = self.name_edit.text().strip()

            if not name:
                QMessageBox.warning(self, "입력 오류", "카테고리 이름을 입력하세요.")
                self.name_edit.setFocus()
                return

            # 중복 확인
            for category in self.storage_manager.categories:
                if category.name == name:
                    QMessageBox.warning(self, "중복 오류", f"'{name}' 카테고리가 이미 존재합니다.")
                    return

            # 선택한 색상 가져오기
            color = self.get_selected_color()
            print(f"새 카테고리 추가: 이름={name}, 색상={color}")

            # 새 카테고리 추가 (빈 템플릿 리스트와 함께)
            new_category = Category(name, color, templates=[])

            self.storage_manager.add_category(new_category)
            self.storage_manager.categories_changed = True

            # 즉시 저장
            self.storage_manager.save_data()
            print("카테고리 데이터 즉시 저장 완료")

            # 목록 새로고침
            self.load_categories()

            # 입력 필드 초기화
            self.name_edit.clear()
            self.name_edit.setFocus()

            QMessageBox.information(self, "성공", f"카테고리 '{name}'이 추가되었습니다.")

        except Exception as e:
            print(f"카테고리 추가 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"카테고리 추가 중 오류가 발생했습니다: {e}")

    def delete_category(self):
        """선택한 카테고리 삭제"""
        try:
            selected_items = self.category_list.selectedItems()

            if not selected_items:
                QMessageBox.information(self, "선택 없음", "삭제할 카테고리를 선택하세요.")
                return

            item = selected_items[0]
            category = item.category

            # ETC 카테고리는 삭제 불가
            if category.name == "ETC":
                QMessageBox.warning(self, "삭제 불가", "ETC 카테고리는 삭제할 수 없습니다.\n\n모든 작업의 기본 카테고리로 사용됩니다.")
                return

            # 삭제 확인
            template_info = ""
            if hasattr(category, 'templates') and len(category.templates) > 0:
                template_info = f"\n\n템플릿 {len(category.templates)}개도 함께 삭제됩니다."

            reply = QMessageBox.question(
                self,
                "카테고리 삭제",
                f"'{category.name}' 카테고리를 삭제하시겠습니까?\n\n"
                f"이 카테고리를 사용하는 모든 작업은 'ETC' 카테고리로 변경됩니다.{template_info}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes  # 기본값을 Yes로 설정
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 카테고리 삭제
                if self.storage_manager.delete_category(category.name):
                    # 즉시 저장
                    self.storage_manager.save_data()
                    self.load_categories()
                    self.update_template_tabs()  # 템플릿 탭도 업데이트
                    QMessageBox.information(self, "성공", f"카테고리 '{category.name}'이 삭제되었습니다.")
        except Exception as e:
            print(f"카테고리 삭제 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"카테고리 삭제 중 오류가 발생했습니다: {e}")

    def accept(self):
        """대화상자 닫기 전 저장"""
        # 모든 변경사항 저장
        self.storage_manager.save_data()
        super().accept()