#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import QCalendarWidget, QToolTip
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QRect, QPoint  # QRect와 QPoint 추가
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont


class CalendarWidget(QCalendarWidget):
    """작업 관리 달력 위젯"""

    # 커스텀 시그널
    date_selected = pyqtSignal(QDate)

    def __init__(self, storage_manager):
        """달력 위젯 초기화

        Args:
            storage_manager (StorageManager): 데이터 저장소 관리자
        """
        super().__init__()

        self.storage_manager = storage_manager
        self.calendar_view_mode = False  # 달력 뷰 모드 플래그

        # 달력 설정
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)

        # 오늘 날짜 선택
        self.setSelectedDate(QDate.currentDate())

        # 시그널 연결
        self.clicked.connect(self.on_date_clicked)

        # 달력 업데이트
        self.update_calendar()

    def on_date_clicked(self, date):
        """날짜 클릭 이벤트 처리

        Args:
            date (QDate): 클릭된 날짜
        """
        self.date_selected.emit(date)

    def update_calendar(self):
        """달력 데이터 업데이트"""
        # 달력 UI 갱신
        self.updateCells()

    def setCalendarViewMode(self, enabled):
        """달력 뷰 모드 설정

        Args:
            enabled (bool): 달력 뷰 모드 활성화 여부
        """
        self.calendar_view_mode = enabled
        self.updateCells()  # 달력 셀 다시 그리기

    def paintCell(self, painter, rect, date):
        """달력 셀 그리기 재정의

        Args:
            painter (QPainter): 페인터 객체
            rect (QRect): 그릴 영역
            date (QDate): 날짜
        """
        # 기본 셀 그리기
        super().paintCell(painter, rect, date)

        # 날짜 문자열 변환 (YYYY-MM-DD)
        date_str = date.toString("yyyy-MM-dd")

        # 날짜 통계 가져오기
        stats = self.storage_manager.get_task_stats(date_str)
        total_count = stats["total"]

        if total_count > 0:
            # 작업이 있는 날짜 표시
            completion_rate = stats["completion_rate"]

            # 배경색 설정 (완료율에 따라 색상 변화)
            if completion_rate == 100:
                # 모두 완료: 녹색
                bg_color = QColor(200, 255, 200, 100)
            elif completion_rate > 0:
                # 일부 완료: 연한 파란색
                bg_color = QColor(200, 200, 255, 100)
            else:
                # 미완료: 연한 빨간색
                bg_color = QColor(255, 200, 200, 100)

            # 배경 그리기
            painter.save()
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)
            painter.restore()

            # 작업 수 표시
            painter.save()
            painter.setPen(QPen(QColor(80, 80, 80)))
            painter.setFont(QFont(self.font().family(), 7))
            text = f"{stats['completed']}/{total_count}"
            painter.drawText(
                rect.adjusted(0, rect.height() - 15, 0, -2),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                text
            )
            painter.restore()

            # 달력 뷰 모드인 경우 작업 제목 표시
            if self.calendar_view_mode:
                try:
                    # 해당 날짜의 작업 목록 가져오기
                    tasks = self.storage_manager.get_tasks_by_date(date_str)

                    # 작업 표시 영역 계산
                    task_rect = rect.adjusted(2, 18, -2, -15)
                    max_items = 3  # 최대 표시 항목 수
                    item_height = min(15, task_rect.height() / max_items)

                    # 작업 목록 표시
                    for i, task in enumerate(tasks[:max_items]):
                        if i >= max_items:
                            break

                        # 작업 항목 배경 설정
                        item_rect = QRect(
                            task_rect.left(),
                            task_rect.top() + int(i * item_height),
                            task_rect.width(),
                            int(item_height - 1)
                        )

                        # 작업 배경색 설정
                        if task.important and not task.completed:
                            item_bg_color = QColor("#FFF8E1")  # 중요 작업: 연한 노랑
                        elif hasattr(task, 'bg_color') and task.bg_color != "none":
                            # 사용자 지정 배경색
                            item_bg_color = QColor(task.get_bg_color_hex())
                        else:
                            item_bg_color = QColor("#FFFFFF")  # 기본: 흰색

                        # 완료된 작업은 회색으로 표시
                        if task.completed:
                            item_bg_color = QColor("#F5F5F5")  # 완료: 연한 회색

                        # 배경 그리기
                        painter.save()
                        painter.setBrush(QBrush(item_bg_color))
                        painter.setPen(QPen(QColor("#DDDDDD")))
                        painter.drawRoundedRect(item_rect, 2, 2)

                        # 제목 텍스트 표시
                        text_color = QColor("#757575") if task.completed else QColor("#212121")
                        painter.setPen(QPen(text_color))
                        painter.setFont(QFont(self.font().family(), 7))

                        # 제목 축약
                        title = task.title
                        if len(title) > 10:
                            title = title[:8] + "..."

                        # 제목 그리기
                        painter.drawText(
                            item_rect.adjusted(2, 0, -2, 0),
                            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                            title
                        )
                        painter.restore()

                    # 추가 항목이 있음을 표시
                    if len(tasks) > max_items:
                        painter.save()
                        painter.setPen(QPen(QColor("#9E9E9E")))
                        painter.setFont(QFont(self.font().family(), 7))
                        painter.drawText(
                            rect.adjusted(0, rect.height() - 28, 0, -15),
                            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                            f"+{len(tasks) - max_items}"
                        )
                        painter.restore()
                except Exception as e:
                    print(f"달력 뷰 작업 표시 중 오류: {e}")

    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리 (툴팁 표시)

        Args:
            event: 마우스 이벤트
        """
        # 마우스 위치의 날짜 가져오기
        pos = event.position()
        date = self.dateAt(pos.toPoint())

        if date.isValid():
            # 날짜 문자열 변환 (YYYY-MM-DD)
            date_str = date.toString("yyyy-MM-dd")

            # 날짜 통계 가져오기
            stats = self.storage_manager.get_task_stats(date_str)

            if stats["total"] > 0:
                # 툴팁 내용 구성
                tooltip = f"작업: {stats['total']}개\n"
                tooltip += f"완료: {stats['completed']}개\n"
                tooltip += f"완료율: {stats['completion_rate']:.1f}%"

                # 툴팁 표시
                QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
            else:
                QToolTip.hideText()
        else:
            QToolTip.hideText()

        super().mouseMoveEvent(event)

    def dateAt(self, pos):
        """주어진 위치의 날짜 반환

        Args:
            pos (QPoint): 마우스 위치

        Returns:
            QDate: 해당 위치의 날짜
        """
        # 현재 표시 중인 월
        current_month = self.monthShown()
        current_year = self.yearShown()

        # 한 셀의 크기 계산
        width = self.width() / 7
        height = (self.height() - self.horizontalHeader().height()) / 6

        # 셀 인덱스 계산
        x = int(pos.x() / width)
        y = int((pos.y() - self.horizontalHeader().height()) / height)

        if 0 <= x < 7 and 0 <= y < 6:
            # 현재 달력 데이터 가져오기
            first_day = QDate(current_year, current_month, 1)
            day_of_week = first_day.dayOfWeek() - 1  # 월요일이 0

            # 셀에 해당하는 날짜 계산
            day = y * 7 + x + 1 - day_of_week

            if day > 0:
                date = QDate(current_year, current_month, day)
                if date.month() == current_month:
                    return date

        return QDate()  # 유효하지 않은 날짜