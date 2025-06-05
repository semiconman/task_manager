#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
필요한 아이콘 파일 생성 스크립트
애플리케이션에 필요한 기본 아이콘들을 생성합니다.
"""

import os
import math
import sys
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont, QImage, QLinearGradient
from PyQt6.QtCore import Qt, QSize, QRect, QPoint
from PyQt6.QtWidgets import QApplication

# 현재 작업 디렉토리 확인
current_dir = os.getcwd()
print(f"현재 작업 디렉토리: {current_dir}")


def create_directory(path):
    """디렉토리 생성"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"디렉토리 생성: {path}")
    else:
        print(f"디렉토리 이미 존재함: {path}")


def create_add_icon(path, size=32):
    """추가 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 녹색 원
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#34A853")))
    painter.drawEllipse(0, 0, size, size)

    # 흰색 '+' 기호
    painter.setPen(QPen(QColor("#FFFFFF"), size / 8))
    center = size / 2
    line_length = size / 3

    # 가로선
    painter.drawLine(
        QPoint(int(center - line_length), int(center)),
        QPoint(int(center + line_length), int(center))
    )

    # 세로선
    painter.drawLine(
        QPoint(int(center), int(center - line_length)),
        QPoint(int(center), int(center + line_length))
    )

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_options_icon(path, size=32):
    """옵션 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 회색 톱니바퀴
    painter.setPen(QPen(QColor("#757575"), size / 16))
    painter.setBrush(QBrush(QColor("#9E9E9E")))

    # 톱니바퀴 외곽 원
    outer_radius = size * 0.4
    painter.drawEllipse(QPoint(int(size / 2), int(size / 2)), int(outer_radius), int(outer_radius))

    # 톱니바퀴 내부 원
    inner_radius = size * 0.2
    painter.drawEllipse(QPoint(int(size / 2), int(size / 2)), int(inner_radius), int(inner_radius))

    # 톱니 그리기
    painter.setPen(QPen(QColor("#757575"), size / 8))
    teeth_count = 8
    for i in range(teeth_count):
        angle = i * (360 / teeth_count)
        rad_angle = angle * (math.pi / 180)

        # 삼각함수 계산
        x_factor = math.cos(rad_angle)
        y_factor = math.sin(rad_angle)

        x1 = size / 2 + outer_radius * 0.9 * x_factor
        y1 = size / 2 + outer_radius * 0.9 * y_factor

        x2 = size / 2 + outer_radius * 1.3 * x_factor
        y2 = size / 2 + outer_radius * 1.3 * y_factor

        painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_star_icon(path, filled=True, size=32):
    """별 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 별 모양 그리기
    painter.setPen(QPen(QColor("#FFB300"), size / 16))
    if filled:
        painter.setBrush(QBrush(QColor("#FFCA28")))

    # 별 꼭지점 좌표 계산
    points = []
    center = size / 2
    outer_radius = size * 0.4
    inner_radius = size * 0.2

    for i in range(10):
        angle = i * 36  # 360 / 10 = 36
        rad_angle = angle * (math.pi / 180)
        radius = outer_radius if i % 2 == 0 else inner_radius

        x = center + radius * math.cos(rad_angle)
        y = center + radius * math.sin(rad_angle)

        points.append(QPoint(int(x), int(y)))

    painter.drawPolygon(points)

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_edit_icon(path, size=32):
    """편집 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 연필 모양 그리기
    painter.setPen(QPen(QColor("#616161"), size / 16))
    painter.setBrush(QBrush(QColor("#9E9E9E")))

    # 연필 몸통
    points = [
        QPoint(int(size * 0.2), int(size * 0.8)),
        QPoint(int(size * 0.7), int(size * 0.3)),
        QPoint(int(size * 0.8), int(size * 0.4)),
        QPoint(int(size * 0.3), int(size * 0.9))
    ]
    painter.drawPolygon(points)

    # 연필 끝
    points = [
        QPoint(int(size * 0.7), int(size * 0.3)),
        QPoint(int(size * 0.8), int(size * 0.2)),
        QPoint(int(size * 0.9), int(size * 0.3)),
        QPoint(int(size * 0.8), int(size * 0.4))
    ]
    painter.setBrush(QBrush(QColor("#FF9800")))
    painter.drawPolygon(points)

    # 지우개
    points = [
        QPoint(int(size * 0.2), int(size * 0.8)),
        QPoint(int(size * 0.3), int(size * 0.9)),
        QPoint(int(size * 0.2), int(size * 0.9)),
        QPoint(int(size * 0.1), int(size * 0.8))
    ]
    painter.setBrush(QBrush(QColor("#F5F5F5")))
    painter.drawPolygon(points)

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_delete_icon(path, size=32):
    """삭제 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 쓰레기통 그리기
    painter.setPen(QPen(QColor("#E53935"), size / 16))
    painter.setBrush(QBrush(QColor("#EF5350")))

    # 쓰레기통 몸통
    painter.drawRect(int(size * 0.2), int(size * 0.3), int(size * 0.6), int(size * 0.6))

    # 쓰레기통 뚜껑
    painter.drawRect(int(size * 0.15), int(size * 0.2), int(size * 0.7), int(size * 0.1))

    # 손잡이
    painter.drawRect(int(size * 0.35), int(size * 0.1), int(size * 0.3), int(size * 0.1))

    # 쓰레기통 선
    painter.setPen(QPen(QColor("#FFFFFF"), size / 16))
    painter.drawLine(int(size * 0.3), int(size * 0.4), int(size * 0.3), int(size * 0.8))
    painter.drawLine(int(size * 0.5), int(size * 0.4), int(size * 0.5), int(size * 0.8))
    painter.drawLine(int(size * 0.7), int(size * 0.4), int(size * 0.7), int(size * 0.8))

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_check_icon(path, size=16):
    """체크 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 흰색 체크 그리기
    painter.setPen(QPen(QColor("#FFFFFF"), size / 4))

    # 체크 모양
    points = [
        QPoint(int(size * 0.2), int(size * 0.5)),
        QPoint(int(size * 0.4), int(size * 0.7)),
        QPoint(int(size * 0.8), int(size * 0.3))
    ]

    painter.drawLine(points[0], points[1])
    painter.drawLine(points[1], points[2])

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_radio_check_icon(path, size=16):
    """라디오 버튼 체크 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 흰색 원 그리기
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#FFFFFF")))

    # 작은 원 그리기
    painter.drawEllipse(int(size * 0.3), int(size * 0.3), int(size * 0.4), int(size * 0.4))

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_dropdown_icon(path, size=16):
    """드롭다운 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 화살표 그리기
    painter.setPen(QPen(QColor("#616161"), size / 8))

    # 화살표 모양
    points = [
        QPoint(int(size * 0.2), int(size * 0.4)),
        QPoint(int(size * 0.5), int(size * 0.7)),
        QPoint(int(size * 0.8), int(size * 0.4))
    ]

    painter.drawLine(points[0], points[1])
    painter.drawLine(points[1], points[2])

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_color_dot_icon(path, size=16):
    """색상 점 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 색상 점 그리기
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#616161")))

    # 원 그리기
    painter.drawEllipse(2, 2, size - 4, size - 4)

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def create_app_icon(path, size=512):
    """애플리케이션 아이콘 생성"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 배경 그리기
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#4285F4"))
    gradient.setColorAt(1, QColor("#34A853"))

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(0, 0, size, size, size / 10, size / 10)

    # 체크리스트 모양 그리기
    padding = size / 5
    rect_width = size - 2 * padding
    rect_height = size / 14

    painter.setBrush(QBrush(QColor("#FFFFFF")))

    for i in range(5):
        y_pos = padding + i * (rect_height * 1.5)

        # 체크 박스
        painter.drawRoundedRect(
            int(padding), int(y_pos), int(rect_height), int(rect_height),
            rect_height / 5, rect_height / 5
        )

        # 체크 표시 (첫 3개 항목)
        if i < 3:
            painter.setPen(QPen(QColor("#4285F4"), rect_height / 5))

            # 체크 모양
            painter.drawLine(
                int(padding + rect_height * 0.2), int(y_pos + rect_height * 0.5),
                int(padding + rect_height * 0.4), int(y_pos + rect_height * 0.7)
            )
            painter.drawLine(
                int(padding + rect_height * 0.4), int(y_pos + rect_height * 0.7),
                int(padding + rect_height * 0.8), int(y_pos + rect_height * 0.3)
            )

            painter.setPen(Qt.PenStyle.NoPen)

        # 항목 텍스트 라인
        painter.drawRoundedRect(
            int(padding + rect_height * 1.5), int(y_pos + rect_height * 0.25),
            int(rect_width - rect_height * 1.5), int(rect_height * 0.5),
            rect_height / 5, rect_height / 5
        )

    painter.end()

    success = pixmap.save(path)
    print(f"아이콘 저장 {'성공' if success else '실패'}: {path}")


def find_png_files(start_path):
    """PNG 파일 찾기"""
    found_files = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.endswith('.png'):
                found_files.append(os.path.join(root, file))
    return found_files


if __name__ == "__main__":
    # QApplication 인스턴스 필요
    app = QApplication(sys.argv)

    # 현재 스크립트 파일의 디렉토리 가져오기
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not current_dir:  # 빈 문자열이면 현재 디렉토리 사용
        current_dir = os.getcwd()

    # 아이콘 저장 디렉토리 (절대 경로)
    icons_dir = os.path.join(current_dir, "resources", "icons")
    create_directory(icons_dir)

    print(f"아이콘을 저장할 디렉토리: {icons_dir}")

    # 아이콘 생성
    create_add_icon(os.path.join(icons_dir, "add.png"))
    create_options_icon(os.path.join(icons_dir, "options.png"))
    create_star_icon(os.path.join(icons_dir, "star.png"), filled=True)
    create_star_icon(os.path.join(icons_dir, "star_empty.png"), filled=False)
    create_edit_icon(os.path.join(icons_dir, "edit.png"))
    create_delete_icon(os.path.join(icons_dir, "delete.png"))
    create_check_icon(os.path.join(icons_dir, "check.png"))
    create_radio_check_icon(os.path.join(icons_dir, "radio_check.png"))
    create_dropdown_icon(os.path.join(icons_dir, "dropdown.png"))
    create_color_dot_icon(os.path.join(icons_dir, "color_dot.png"))
    create_app_icon(os.path.join(icons_dir, "app_icon.png"))

    print("모든 아이콘이 생성되었습니다.")

    # 생성된 PNG 파일 찾기
    png_files = find_png_files(current_dir)
    print(f"\n찾은 PNG 파일 개수: {len(png_files)}")
    for file in png_files:
        print(f" - {file}")