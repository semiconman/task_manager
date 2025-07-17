import sys
from cx_Freeze import setup, Executable

# 프로그램 정보 설정
APP_NAME = "Todolist_PM_Ver1.6"
VERSION = "1.6"
DESCRIPTION = "Todolist PM - 일정 관리"
AUTHOR = "YoungJun_Ahn"

# 콘솔창 숨김 설정 (Windows)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# 빌드 옵션 설정
build_options = {
    # 필요한 패키지 포함
    "packages": [
        "PyQt6",
        "PyQt6.QtWidgets",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "win32com.client",  # Outlook 연동용
        "win32com",
        "pythoncom",
        "pywintypes",
        "uuid",
        "json",
        "datetime",
        "csv",
        "subprocess",
        "os",
        "sys",
        "traceback",
        "math",
        "calendar"
    ],

    # 필요한 파일/폴더 포함
    "include_files": [
        ("resources", "resources"),
        ("data", "data"),
        ("ui", "ui"),
        ("utils", "utils"),
        ("models", "models"),
        # Windows 시스템 DLL (필요한 경우)
        # ("C:/Windows/System32/msvcp140.dll", "msvcp140.dll"),
        # ("C:/Windows/System32/vcruntime140.dll", "vcruntime140.dll"),
    ],

    # 제외할 모듈들 (빌드 크기 최적화)
    "excludes": [
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "PIL",
        "pygame",
        "unittest",
        "pydoc",
        "email",
        "xml"
    ],

    # 빌드 폴더 지정
    "build_exe": f"build/{APP_NAME}",

    # 최적화 옵션 (지원되는 옵션만 사용)
    "optimize": 2,

    # ZIP 파일 포함 (더 빠른 로딩)
    "zip_include_packages": ["*"],
    "zip_exclude_packages": []
}

# 실행 파일 설정
executables = [
    Executable(
        script="main.py",  # 메인 파이썬 파일
        base=base,  # GUI 모드 (콘솔창 숨김)
        target_name=f"{APP_NAME}.exe",  # 실행 파일 이름
        icon="resources/icons/app_icon.ico",  # ICO 파일 사용 (권장)
        shortcut_name="Todolist PM",  # 바로가기 이름
        shortcut_dir="DesktopFolder"  # 바탕화면에 바로가기 생성
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