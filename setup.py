import sys
from cx_Freeze import setup, Executable

# 프로그램 정보 설정
APP_NAME = "Todolist_PM_Ver1.31"
VERSION = "1.31"
DESCRIPTION = "Todolist_PM_Ver1.31"
AUTHOR = "YoungJun_Ahn"

# 콘솔창 완전 숨김 설정
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Windows에서 콘솔창 숨김

# 빌드 옵션 설정
build_options = {
    # 필요한 패키지 포함
    "packages": ["PyQt6", "uuid", "json", "datetime", "csv"],

    # 필요한 파일/폴더 포함
    "include_files": [
        ("resources", "resources"),
        ("data", "data")
    ],

    # 빌드 폴더 지정
    "build_exe": f"build/{APP_NAME}",

    # 콘솔 출력 완전 차단 옵션들
    "silent": True,
    "optimize": 2,

    # 불필요한 모듈 제외 (크기 줄이기 + 안정성)
    "excludes": [
        "tkinter", "unittest", "email", "html", "http", "urllib",
        "xml", "pydoc", "doctest", "argparse", "difflib"
    ]
}

# 실행 파일 설정
executables = [
    Executable(
        script="main.py",  # 메인 파이썬 파일
        base=base,  # GUI 모드 (콘솔창 완전 숨김)
        target_name=f"{APP_NAME}.exe",  # 실행 파일 이름
        icon="resources/icons/app_icon.ico" if sys.platform == "win32" else None,  # 아이콘

        # 추가 콘솔 숨김 옵션들
        copyright="Copyright (C) 2024 YoungJun_Ahn",
        trademarks="Todolist PM"
    )
]

# cx_Freeze 설정
setup(
    name=APP_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    options={"build_exe": build_options},
    executables=executables
)