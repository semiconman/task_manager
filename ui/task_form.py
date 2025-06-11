#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QCheckBox, QPushButton, QDialogButtonBox,
    QDateEdit, QGroupBox, QRadioButton, QButtonGroup, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QColor

from models.task import Task


class TaskForm(QDialog):
    """작업 추가/편집 대화상자"""

    def __init__(self, storage_manager, current_date, task=None):
        """작업 폼 초기화

        Args:
            storage_manager (StorageManager): 데이터 저장소 관리자
            current_date (str): 현재 선택된 날짜
            task (Task, optional): 편집할 작업 객체. 없으면 새 작업 추가 모드
        """
        super().__init__()

        self.storage_manager = storage_manager
        self.current_date = current_date
        self.task = task
        self.edit_mode = task is not None

        # 대화상자 설정
        self.setWindowTitle("작업 편집" if self.edit_mode else "새 작업")
        self.setMinimumWidth(600)  # 가로 크기 증가
        self.setMinimumHeight(500)  # 세로 크기 제한
        self.setMaximumHeight(600)  # 최대 높이 제한
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # UI 초기화
        self.init_ui()

        # 편집 모드인 경우 기존 데이터 표시
        if self.edit_mode:
            self.populate_form()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 상단 영역: 기본 정보
        top_layout = QHBoxLayout()

        # 좌측: 기본 입력 필드들
        left_layout = QVBoxLayout()

        # 제목 입력
        title_layout = QVBoxLayout()
        title_label = QLabel("제목:")
        title_label.setStyleSheet("font-weight: bold;")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("작업 제목을 입력하세요")

        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_edit)
        left_layout.addLayout(title_layout)

        # 내용 입력
        content_layout = QVBoxLayout()
        content_label = QLabel("내용:")
        content_label.setStyleSheet("font-weight: bold;")
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("작업 내용을 입력하세요 (선택사항)")
        self.content_edit.setMinimumHeight(80)  # 높이 줄임
        self.content_edit.setMaximumHeight(100)

        content_layout.addWidget(content_label)
        content_layout.addWidget(self.content_edit)
        left_layout.addLayout(content_layout)

        # 날짜 선택 필드
        date_layout = QVBoxLayout()
        date_label = QLabel("날짜:")
        date_label.setStyleSheet("font-weight: bold;")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)

        # 현재 선택된 날짜로 설정
        try:
            self.date_edit.setDate(QDate.fromString(self.current_date, "yyyy-MM-dd"))
        except Exception as e:
            print(f"날짜 설정 중 오류: {e}")
            self.date_edit.setDate(QDate.currentDate())

        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        left_layout.addLayout(date_layout)

        # 카테고리 선택
        category_layout = QVBoxLayout()
        category_label = QLabel("카테고리:")
        category_label.setStyleSheet("font-weight: bold;")
        self.category_combo = QComboBox()

        # 카테고리 목록 로드
        if hasattr(self.storage_manager, 'categories') and self.storage_manager.categories:
            for category in self.storage_manager.categories:
                self.category_combo.addItem(category.name)
        else:
            default_categories = ["LB", "Tester", "Handler", "ETC"]
            for cat_name in default_categories:
                self.category_combo.addItem(cat_name)

        if self.category_combo.count() == 0:
            self.category_combo.addItem("ETC")

        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        left_layout.addLayout(category_layout)

        # 중요 여부
        self.important_check = QCheckBox("중요 작업으로 표시")
        left_layout.addWidget(self.important_check)

        top_layout.addLayout(left_layout)

        # 우측: 배경색 선택
        right_layout = QVBoxLayout()

        # 배경색 선택 그룹박스
        color_group = QGroupBox("배경색")
        color_layout = QVBoxLayout(color_group)

        # 색상 선택 라디오 버튼
        self.color_radio_group = QButtonGroup(self)
        self.color_radios = {}

        # 색상 정보 (더 컴팩트하게)
        colors = {
            "none": "없음",
            "red": "빨강",
            "orange": "주황",
            "yellow": "노랑",
            "green": "초록",
            "blue": "파랑",
            "purple": "보라"
        }

        # 라디오 버튼 생성 (더 작게)
        for color_code, color_name in colors.items():
            radio = QRadioButton(color_name)

            if color_code != "none":
                bg_color = Task.BG_COLORS.get(color_code, "#FFFFFF")
                radio.setStyleSheet(f"""
                    QRadioButton {{
                        background-color: {bg_color};
                        padding: 3px;
                        border-radius: 3px;
                        font-size: 11px;
                    }}
                """)

            self.color_radio_group.addButton(radio)
            self.color_radios[color_code] = radio
            color_layout.addWidget(radio)

        # 기본값은 '없음'
        self.color_radios["none"].setChecked(True)

        right_layout.addWidget(color_group)
        right_layout.addStretch()  # 남은 공간 채우기

        top_layout.addLayout(right_layout)

        layout.addLayout(top_layout)

        # 템플릿 선택 영역
        self.template_group = QGroupBox("템플릿 사용 (선택사항)")
        template_layout = QVBoxLayout(self.template_group)

        template_info_label = QLabel("해당 카테고리의 템플릿을 선택하면 제목과 내용이 자동으로 입력됩니다.")
        template_info_label.setStyleSheet("color: #666666; font-size: 11px;")
        template_layout.addWidget(template_info_label)

        self.template_list = QListWidget()
        self.template_list.setMaximumHeight(100)  # 높이 줄임
        self.template_list.itemClicked.connect(self.on_template_selected)
        template_layout.addWidget(self.template_list)

        # 템플릿 버튼들
        template_button_layout = QHBoxLayout()
        self.apply_template_btn = QPushButton("선택한 템플릿 적용")
        self.apply_template_btn.clicked.connect(self.apply_selected_template)
        self.apply_template_btn.setEnabled(False)

        self.clear_form_btn = QPushButton("양식 초기화")
        self.clear_form_btn.clicked.connect(self.clear_form_fields)

        template_button_layout.addWidget(self.apply_template_btn)
        template_button_layout.addWidget(self.clear_form_btn)
        template_layout.addLayout(template_button_layout)

        layout.addWidget(self.template_group)

        # 버튼
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("저장")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("취소")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 카테고리 변경 시 템플릿 업데이트 - 모든 UI 요소가 생성된 후에 연결
        self.category_combo.currentTextChanged.connect(self.on_category_changed)

        # 초기 템플릿 로드
        self.load_templates()

    def on_category_changed(self, category_name):
        """카테고리 변경 시 템플릿 목록 업데이트"""
        self.load_templates()

    def load_templates(self):
        """현재 선택된 카테고리의 템플릿 목록 로드"""
        self.template_list.clear()
        self.apply_template_btn.setEnabled(False)

        current_category_name = self.category_combo.currentText()
        if not current_category_name:
            return

        # 해당 카테고리 찾기
        current_category = None
        for category in self.storage_manager.categories:
            if category.name == current_category_name:
                current_category = category
                break

        if not current_category or not hasattr(current_category, 'templates'):
            return

        # 템플릿이 있는 경우에만 표시
        if len(current_category.templates) > 0:
            for i, template in enumerate(current_category.templates):
                title = template.get('title', f'템플릿 {i + 1}')
                content_preview = template.get('content', '')

                # 내용 미리보기 (20자 제한)
                if content_preview:
                    if len(content_preview) > 20:
                        content_preview = content_preview[:20] + "..."
                    display_text = f"{title} - {content_preview}"
                else:
                    display_text = title

                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, i)  # 템플릿 인덱스 저장
                item.setToolTip(f"제목: {title}\n내용: {template.get('content', '(내용 없음)')}")
                self.template_list.addItem(item)

            # 템플릿 그룹 표시
            self.template_group.setVisible(True)
        else:
            # 템플릿이 없으면 그룹 숨기기
            self.template_group.setVisible(False)

    def on_template_selected(self, item):
        """템플릿 선택 시 적용 버튼 활성화"""
        self.apply_template_btn.setEnabled(True)

    def apply_selected_template(self):
        """선택한 템플릿 적용"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return

        # 템플릿 인덱스 가져오기
        template_index = current_item.data(Qt.ItemDataRole.UserRole)

        # 현재 카테고리의 템플릿 가져오기
        current_category_name = self.category_combo.currentText()
        current_category = None

        for category in self.storage_manager.categories:
            if category.name == current_category_name:
                current_category = category
                break

        if (current_category and hasattr(current_category, 'templates') and
                0 <= template_index < len(current_category.templates)):
            template = current_category.templates[template_index]

            # 제목과 내용 적용
            self.title_edit.setText(template.get('title', ''))
            self.content_edit.setText(template.get('content', ''))

            # 적용 완료 메시지
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "템플릿 적용", f"템플릿 '{template.get('title', '')}'이 적용되었습니다.")

    def clear_form_fields(self):
        """양식 필드 초기화"""
        self.title_edit.clear()
        self.content_edit.clear()
        self.important_check.setChecked(False)
        self.color_radios["none"].setChecked(True)

    def populate_form(self):
        """기존 작업 데이터 폼에 표시"""
        if not self.task:
            return

        self.title_edit.setText(self.task.title)
        self.content_edit.setText(self.task.content)

        # 날짜 설정
        try:
            self.date_edit.setDate(QDate.fromString(self.task.created_date, "yyyy-MM-dd"))
        except Exception as e:
            print(f"날짜 설정 중 오류: {e}")

        # 카테고리 선택 - 보호 코드 추가
        index = self.category_combo.findText(self.task.category)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

        # 배경색 설정
        if hasattr(self.task, 'bg_color') and self.task.bg_color in self.color_radios:
            self.color_radios[self.task.bg_color].setChecked(True)

        self.important_check.setChecked(self.task.important)

        # 편집 모드에서는 템플릿 그룹 숨기기 (기존 작업 편집 시에는 템플릿 불필요)
        self.template_group.setVisible(False)

    def get_selected_color(self):
        """선택된 배경색 코드 반환"""
        for color_code, radio in self.color_radios.items():
            if radio.isChecked():
                return color_code
        return "none"  # 기본값

    def accept(self):
        """확인 버튼 클릭 처리"""
        try:
            # 입력 데이터 유효성 검사
            title = self.title_edit.text().strip()
            if not title:
                self.title_edit.setFocus()
                return

            content = self.content_edit.toPlainText().strip()

            # 카테고리 선택 안전하게 가져오기
            if self.category_combo.currentText():
                category = self.category_combo.currentText()
            else:
                category = "ETC"  # 기본값

            important = self.important_check.isChecked()

            # 선택한 날짜 가져오기
            selected_date = self.date_edit.date().toString("yyyy-MM-dd")

            # 선택한 배경색 가져오기
            bg_color = self.get_selected_color()

            if self.edit_mode and self.task:
                # 기존 작업 업데이트
                self.task.title = title
                self.task.content = content
                self.task.category = category
                self.task.important = important
                self.task.created_date = selected_date
                self.task.bg_color = bg_color

                if hasattr(self.storage_manager, 'update_task'):
                    self.storage_manager.update_task(self.task.id, self.task)
            else:
                # 새 작업 추가
                new_task = Task(
                    title=title,
                    content=content,
                    category=category,
                    important=important,
                    created_date=selected_date,
                    bg_color=bg_color
                )

                if hasattr(self.storage_manager, 'add_task'):
                    self.storage_manager.add_task(new_task)

            super().accept()
        except Exception as e:
            print(f"작업 저장 중 오류 발생: {e}")
            # 오류가 발생해도 프로그램이 중단되지 않도록 처리
            super().reject()