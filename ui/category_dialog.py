#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QColorDialog,
    QMessageBox, QDialogButtonBox, QFrame, QButtonGroup, QRadioButton, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon

from models.category import Category


class CategoryItem(QListWidgetItem):
    """카테고리 항목"""

    def __init__(self, category):
        """카테고리 항목 초기화

        Args:
            category (Category): 카테고리 객체
        """
        super().__init__()

        self.category = category
        self.setText(category.name)

        # 색상 표시
        self.setForeground(QColor("white"))
        self.setBackground(QColor(category.color))

        # 기본 카테고리는 삭제 불가 표시
        if category.name in ["LB", "Tester", "Handler", "ETC"]:
            self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.setToolTip("기본 카테고리는 삭제할 수 없습니다")


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
        self.setMinimumSize(500, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # UI 초기화
        self.init_ui()

        # 카테고리 목록 로드
        self.load_categories()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        # 카테고리 목록
        list_label = QLabel("카테고리 목록:")
        list_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(list_label)

        self.category_list = QListWidget()
        self.category_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
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

        # 닫기 버튼
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)

    def load_categories(self):
        """카테고리 목록 로드"""
        self.category_list.clear()

        for category in self.storage_manager.categories:
            item = CategoryItem(category)
            self.category_list.addItem(item)

    def get_selected_color(self):
        """선택된 색상 코드 반환"""
        for color_hex, radio in self.color_radios.items():
            if radio.isChecked():
                return color_hex
        # 기본값 반환
        return list(self.COLOR_SAMPLES.values())[0]

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

            # 새 카테고리 추가
            new_category = Category(name, color)

            self.storage_manager.add_category(new_category)
            self.storage_manager.categories_changed = True

            # 목록 새로고침
            self.load_categories()

            # 입력 필드 초기화
            self.name_edit.clear()
            self.name_edit.setFocus()
        except Exception as e:
            print(f"카테고리 추가 중 오류 발생: {e}")
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

            # 기본 카테고리는 삭제 불가
            if category.name in ["LB", "Tester", "Handler", "ETC"]:
                QMessageBox.warning(self, "삭제 불가", "기본 카테고리는 삭제할 수 없습니다.")
                return

            # 삭제 확인
            reply = QMessageBox.question(
                self,
                "카테고리 삭제",
                f"'{category.name}' 카테고리를 삭제하시겠습니까?\n\n"
                f"이 카테고리를 사용하는 모든 작업은 'ETC' 카테고리로 변경됩니다.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 카테고리 삭제
                if self.storage_manager.delete_category(category.name):
                    self.load_categories()
        except Exception as e:
            print(f"카테고리 삭제 중 오류 발생: {e}")
            QMessageBox.warning(self, "오류", f"카테고리 삭제 중 오류가 발생했습니다: {e}")