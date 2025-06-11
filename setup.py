import sys
from cx_Freeze import setup, Executable

# 프로그램 정보 설정
APP_NAME = "Todolist_PM_Ver1.41"
VERSION = "1.41"
DESCRIPTION = "Todolist_PM_Ver1.41"
AUTHOR = "YoungJun_Ahn"

# 콘솔창 숨김 설정 (Windows)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

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
    "build_exe": f"build/{APP_NAME}"
}

# 실행 파일 설정
executables = [
    Executable(
        script="main.py",  # 메인 파이썬 파일
        base=base,  # GUI 모드 (콘솔창 숨김)
        target_name=f"{APP_NAME}.exe",  # 실행 파일 이름
        icon="resources/icons/app_icon.ico" if sys.platform == "win32" else None  # 아이콘 (있는 경우)
    )
]

# cx_Freeze 설정
setup(
    name=APP_NAME,
    version=VERSION,
    description=DESCRIPTION,
    options={"build_exe": build_options},
    executables=executables
)