import sys
import os
import traceback
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.storage import StorageManager

# 로그 설정
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, f"debug_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# 예외 처리기
def exception_hook(exctype, value, tb):
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logging.error(f"예외 발생:\n{error_msg}")
    print(f"예외 발생:\n{error_msg}")
    sys.__excepthook__(exctype, value, tb)


sys.excepthook = exception_hook


def main():
    try:
        logging.info("애플리케이션 시작")
        app = QApplication(sys.argv)

        # 스타일시트 적용
        try:
            with open("resources/styles/macos_style.qss", "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            logging.error(f"스타일시트 로딩 오류: {e}")

        storage_manager = StorageManager()
        main_window = MainWindow(storage_manager)
        main_window.show()

        return app.exec()
    except Exception as e:
        logging.error(f"main 함수 오류: {e}")
        logging.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    print(f"로그 파일: {log_file}")
    sys.exit(main())