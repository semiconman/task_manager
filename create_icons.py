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
    """애플리케이션 아이콘 생성 (개선된 버전)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 배경 그라디언트 (더 현대적인 색상)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#667eea"))  # 보라-파랑
    gradient.setColorAt(0.5, QColor("#764ba2"))  # 보라
    gradient.setColorAt(1, QColor("#f093fb"))  # 분홍

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(0, 0, size, size, size / 8, size / 8)

    # 그림자 효과
    shadow_gradient = QLinearGradient(0, size * 0.7, 0, size)
    shadow_gradient.setColorAt(0, QColor(0, 0, 0, 0))
    shadow_gradient.setColorAt(1, QColor(0, 0, 0, 50))
    painter.setBrush(QBrush(shadow_gradient))
    painter.drawRoundedRect(0, 0, size, size, size / 8, size / 8)

    # 메인 체크리스트 아이콘
    padding = size / 6
    item_height = size / 12

    # 흰색 반투명 배경
    painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
    painter.drawRoundedRect(
        int(padding), int(padding),
        int(size - 2 * padding), int(size - 2 * padding),
        int(size / 20), int(size / 20)
    )

    # 체크리스트 항목들
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.setPen(Qt.PenStyle.NoPen)

    for i in range(5):
        y_pos = padding + padding / 2 + i * (item_height * 1.8)

        # 체크박스
        checkbox_size = item_height * 0.8
        painter.drawRoundedRect(
            int(padding + padding / 3), int(y_pos),
            int(checkbox_size), int(checkbox_size),
            int(checkbox_size / 6), int(checkbox_size / 6)
        )

        # 체크 표시 (처음 3개 항목)
        if i < 3:
            painter.setPen(QPen(QColor("#4CAF50"), int(checkbox_size / 6)))

            # 체크 모양 그리기
            check_start_x = padding + padding / 3 + checkbox_size * 0.2
            check_start_y = y_pos + checkbox_size * 0.5
            check_mid_x = padding + padding / 3 + checkbox_size * 0.45
            check_mid_y = y_pos + checkbox_size * 0.7
            check_end_x = padding + padding / 3 + checkbox_size * 0.8
            check_end_y = y_pos + checkbox_size * 0.3

            painter.drawLine(
                QPoint(int(check_start_x), int(check_start_y)),
                QPoint(int(check_mid_x), int(check_mid_y))
            )
            painter.drawLine(
                QPoint(int(check_mid_x), int(check_mid_y)),
                QPoint(int(check_end_x), int(check_end_y))
            )
            painter.setPen(Qt.PenStyle.NoPen)

        # 텍스트 라인
        line_width = (size - 2 * padding) * 0.6
        line_y = y_pos + checkbox_size * 0.3
        line_height = checkbox_size * 0.4

        painter.drawRoundedRect(
            int(padding + padding / 3 + checkbox_size * 1.4), int(line_y),
            int(line_width), int(line_height),
            int(line_height / 4), int(line_height / 4)
        )

    # 텍스트 추가 (하단)
    painter.setPen(QPen(QColor("#FFFFFF")))
    font = QFont("Arial", int(size / 20), QFont.Weight.Bold)
    painter.setFont(font)

    text_rect = QRect(0, int(size * 0.8), size, int(size * 0.2))
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Todolist PM")

    painter.end()

    success = pixmap.save(path)
    print(f"앱 아이콘 저장 {'성공' if success else '실패'}: {path}")
    return pixmap


def create_ico_file(png_path, ico_path):
    """PNG 파일을 ICO 파일로 변환"""
    try:
        # PIL 라이브러리 사용 (없으면 설치 필요)
        try:
            from PIL import Image

            # PNG 이미지 열기
            img = Image.open(png_path)

            # ICO 파일로 저장 (여러 크기 포함)
            img.save(ico_path, format='ICO', sizes=[
                (16, 16), (32, 32), (48, 48), (64, 64),
                (128, 128), (256, 256)
            ])
            print(f"ICO 파일 생성 성공: {ico_path}")
            return True

        except ImportError:
            print("PIL 라이브러리가 없어서 ICO 파일을 생성할 수 없습니다.")
            print("설치 방법: pip install Pillow")

            # PyQt6로 간단한 ICO 생성 시도
            pixmap = QPixmap(png_path)
            if not pixmap.isNull():
                # 256x256 크기로 리사이즈
                scaled_pixmap = pixmap.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                success = scaled_pixmap.save(ico_path, "ICO")
                if success:
                    print(f"PyQt6로 ICO 파일 생성 성공: {ico_path}")
                    return True
                else:
                    print(f"PyQt6로 ICO 파일 생성 실패: {ico_path}")
                    return False
            return False

    except Exception as e:
        print(f"ICO 파일 생성 중 오류: {e}")
        return False


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

    # 기본 아이콘들 생성
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

    # 앱 아이콘 생성 (여러 크기)
    print("\n=== 앱 아이콘 생성 중 ===")

    # 고해상도 앱 아이콘 (512x512)
    app_icon_512 = os.path.join(icons_dir, "app_icon.png")
    create_app_icon(app_icon_512, 512)

    # 중간 해상도 (256x256)
    app_icon_256 = os.path.join(icons_dir, "app_icon_256.png")
    create_app_icon(app_icon_256, 256)

    # 작은 해상도 (128x128)
    app_icon_128 = os.path.join(icons_dir, "app_icon_128.png")
    create_app_icon(app_icon_128, 128)

    # 윈도우용 ICO 파일 생성
    print("\n=== ICO 파일 생성 중 ===")
    ico_path = os.path.join(icons_dir, "app_icon.ico")
    ico_success = create_ico_file(app_icon_512, ico_path)

    if not ico_success:
        print("\n⚠️  ICO 파일 생성을 위해 Pillow 라이브러리 설치를 권장합니다:")
        print("명령어: pip install Pillow")

    print("\n=== 생성 완료 ===")
    print("모든 아이콘이 생성되었습니다.")

    # 생성된 PNG 파일 찾기
    png_files = find_png_files(current_dir)
    print(f"\n찾은 PNG 파일 개수: {len(png_files)}")
    for file in png_files:
        print(f" - {file}")

    print(f"\n📁 아이콘 저장 위치: {icons_dir}")
    print("🎨 앱 아이콘 파일:")
    print(f" - app_icon.png (512x512) - 고해상도")
    print(f" - app_icon_256.png (256x256) - 중간해상도")
    print(f" - app_icon_128.png (128x128) - 작은해상도")
    if ico_success:
        print(f" - app_icon.ico - Windows 실행파일용")