@echo off
chcp 65001 > nul
echo ===============================================
echo Todolist PM - 메일 기능 의존성 설치
echo ===============================================
echo.

echo 메일 발송 기능을 사용하기 위해 필요한 라이브러리를 설치합니다.
echo.

pause

echo pywin32 설치 중...
pip install pywin32

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===============================================
    echo 설치 완료!
    echo ===============================================
    echo.
    echo 이제 Todolist PM에서 메일 기능을 사용할 수 있습니다.
    echo 프로그램을 다시 시작해주세요.
    echo.
) else (
    echo.
    echo ===============================================
    echo 설치 실패!
    echo ===============================================
    echo.
    echo 다음 방법으로 수동 설치를 시도해보세요:
    echo 1. 명령 프롬프트를 관리자 권한으로 실행
    echo 2. 'pip install pywin32' 입력
    echo 3. 설치 완료 후 프로그램 재시작
    echo.
)

pause