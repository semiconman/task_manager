#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QGroupBox, QRadioButton,
    QDateEdit, QFileDialog, QMessageBox, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon

from datetime import datetime
from utils.date_utils import get_month_start_end, get_week_start_end, get_current_date_str
from utils.csv_exporter import CsvExporter


class ExportDialog(QDialog):
    """CSV 내보내기 대화상자"""

    def __init__(self, storage_manager):
        """CSV 내보내기 대화상자 초기화

        Args:
            storage_manager (StorageManager): 데이터 저장소 관리자
        """
        super().__init__()

        self.storage_manager = storage_manager

        # 대화상자 설정
        self.setWindowTitle("CSV 내보내기")
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # UI 초기화
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 날짜 범위 선택
        date_group = QGroupBox("날짜 범위")
        date_layout = QVBoxLayout(date_group)

        # 라디오 버튼 그룹
        self.date_radio_group = QButtonGroup(self)

        # 모든 날짜
        self.all_radio = QRadioButton("모든 날짜")
        self.all_radio.setChecked(True)
        date_layout.addWidget(self.all_radio)
        self.date_radio_group.addButton(self.all_radio)

        # 오늘
        self.today_radio = QRadioButton("오늘")
        date_layout.addWidget(self.today_radio)
        self.date_radio_group.addButton(self.today_radio)

        # 이번 주
        self.week_radio = QRadioButton("이번 주")
        date_layout.addWidget(self.week_radio)
        self.date_radio_group.addButton(self.week_radio)

        # 이번 달
        self.month_radio = QRadioButton("이번 달")
        date_layout.addWidget(self.month_radio)
        self.date_radio_group.addButton(self.month_radio)

        # 사용자 지정 기간
        self.custom_radio = QRadioButton("사용자 지정 기간")
        date_layout.addWidget(self.custom_radio)
        self.date_radio_group.addButton(self.custom_radio)

        # 사용자 지정 날짜 선택
        custom_date_layout = QHBoxLayout()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setEnabled(False)
        custom_date_layout.addWidget(self.start_date)

        custom_date_layout.addWidget(QLabel("~"))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setEnabled(False)
        custom_date_layout.addWidget(self.end_date)

        date_layout.addLayout(custom_date_layout)

        # 라디오 버튼 선택 이벤트 연결
        self.custom_radio.toggled.connect(lambda checked: self.start_date.setEnabled(checked))
        self.custom_radio.toggled.connect(lambda checked: self.end_date.setEnabled(checked))

        layout.addWidget(date_group)

        # 카테고리 필터
        category_group = QGroupBox("카테고리 필터")
        category_layout = QVBoxLayout(category_group)

        # 카테고리 체크박스 목록
        self.category_checks = {}

        # 모든 카테고리 체크박스
        self.all_categories_check = QCheckBox("모든 카테고리")
        self.all_categories_check.setChecked(True)
        self.all_categories_check.stateChanged.connect(self.toggle_all_categories)
        category_layout.addWidget(self.all_categories_check)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        category_layout.addWidget(line)

        # 개별 카테고리 체크박스
        for category in self.storage_manager.categories:
            check = QCheckBox(category.name)
            check.setChecked(True)
            category_layout.addWidget(check)
            self.category_checks[category.name] = check

        layout.addWidget(category_group)

        # 완료 상태 필터
        completion_group = QGroupBox("완료 상태 필터")
        completion_layout = QVBoxLayout(completion_group)

        # 라디오 버튼 그룹
        self.completion_radio_group = QButtonGroup(self)

        # 모든 작업
        self.all_tasks_radio = QRadioButton("모든 작업")
        self.all_tasks_radio.setChecked(True)
        completion_layout.addWidget(self.all_tasks_radio)
        self.completion_radio_group.addButton(self.all_tasks_radio)

        # 완료된 작업만
        self.completed_radio = QRadioButton("완료된 작업만")
        completion_layout.addWidget(self.completed_radio)
        self.completion_radio_group.addButton(self.completed_radio)

        # 미완료 작업만
        self.incomplete_radio = QRadioButton("미완료 작업만")
        completion_layout.addWidget(self.incomplete_radio)
        self.completion_radio_group.addButton(self.incomplete_radio)

        layout.addWidget(completion_group)

        # 내보내기 옵션
        options_group = QGroupBox("내보내기 옵션")
        options_layout = QVBoxLayout(options_group)

        # 헤더 포함 여부
        self.header_check = QCheckBox("헤더 포함")
        self.header_check.setChecked(True)
        options_layout.addWidget(self.header_check)

        # 포함할 필드
        field_layout = QVBoxLayout()
        field_label = QLabel("포함할 필드:")
        field_layout.addWidget(field_label)

        # 필드 체크박스
        self.field_checks = {}
        field_names = {
            "id": "ID",
            "title": "제목",
            "content": "내용",
            "category": "카테고리",
            "created_date": "생성일",
            "important": "중요",
            "completed": "완료"
        }

        for field_key, field_name in field_names.items():
            check = QCheckBox(field_name)
            check.setChecked(True)
            field_layout.addWidget(check)
            self.field_checks[field_key] = check

        options_layout.addLayout(field_layout)

        layout.addWidget(options_group)

        # 버튼 영역
        button_layout = QHBoxLayout()

        # 내보내기 버튼
        export_button = QPushButton("내보내기")
        export_button.clicked.connect(self.export_csv)
        button_layout.addWidget(export_button)

        # 취소 버튼
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    # 여기에 누락된 메서드 추가
    def toggle_all_categories(self, state):
        """모든 카테고리 체크박스 토글 처리"""
        try:
            checked = state == Qt.CheckState.Checked
            for check in self.category_checks.values():
                check.setChecked(checked)
        except Exception as e:
            print(f"카테고리 토글 중 오류 발생: {e}")

    def get_date_range(self):
        """선택된 날짜 범위 반환"""
        today = get_current_date_str()

        if self.all_radio.isChecked():
            # 모든 날짜
            return None
        elif self.today_radio.isChecked():
            # 오늘
            return (today, today)
        elif self.week_radio.isChecked():
            # 이번 주
            return get_week_start_end(today)
        elif self.month_radio.isChecked():
            # 이번 달
            return get_month_start_end(today)
        elif self.custom_radio.isChecked():
            # 사용자 지정 기간
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            return (start, end)

        return None

    def get_selected_categories(self):
        """선택된 카테고리 목록 반환"""
        if self.all_categories_check.isChecked():
            return None

        selected = []
        for name, check in self.category_checks.items():
            if check.isChecked():
                selected.append(name)

        return selected if selected else None

    def get_completion_filter(self):
        """선택된 완료 상태 필터 반환"""
        if self.all_tasks_radio.isChecked():
            return None
        elif self.completed_radio.isChecked():
            return True
        elif self.incomplete_radio.isChecked():
            return False

        return None

    def get_selected_fields(self):
        """선택된 필드 목록 반환"""
        selected = []
        for field, check in self.field_checks.items():
            if check.isChecked():
                selected.append(field)

        return selected if selected else None

    def export_csv(self):
        """CSV 내보내기 실행"""
        try:
            # 저장 경로 선택
            file_path, _ = QFileDialog.getSaveFileName(
                self, "CSV 파일 저장", "", "CSV 파일 (*.csv);;모든 파일 (*.*)"
            )

            if not file_path:
                return

            # 파일 확장자 확인
            if not file_path.lower().endswith(".csv"):
                file_path += ".csv"

            # 필터 옵션 가져오기
            date_range = self.get_date_range()
            categories = self.get_selected_categories()
            completed = self.get_completion_filter()
            include_header = self.header_check.isChecked()
            fields = self.get_selected_fields()

            # 작업 필터링
            filtered_tasks = CsvExporter.filter_tasks(
                self.storage_manager.tasks,
                date_range=date_range,
                categories=categories,
                completed=completed
            )

            # CSV 내보내기
            success = CsvExporter.export_tasks(
                filtered_tasks,
                file_path,
                include_header=include_header,
                fields=fields
            )

            if success:
                QMessageBox.information(
                    self, "내보내기 성공",
                    f"작업이 성공적으로 CSV 파일로 내보내졌습니다.\n\n파일 경로: {file_path}"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self, "내보내기 오류",
                    "CSV 파일 내보내기 중 오류가 발생했습니다."
                )
        except Exception as e:
            print(f"CSV 내보내기 중 오류 발생: {e}")
            QMessageBox.critical(
                self, "내보내기 오류",
                f"CSV 파일 내보내기 중 오류가 발생했습니다: {e}"
            )