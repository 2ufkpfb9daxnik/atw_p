from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSpinBox, QLabel
from PyQt6.QtGui import QFontDatabase, QFont
import os
from prompt_widget import PromptWidget
from settings import SettingsWindow

def main():
    app = QApplication([])

    # フォント読み込み
    font_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "NotoSansJP-Regular.ttf"))
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)
            if font_family:
                app.setFont(QFont(font_family[0], 20))

    # ウィンドウ初期化
    window = QWidget()
    window.setWindowTitle("atw")
    layout = QVBoxLayout()

    # お題ウィジェット
    prompt_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "prompt.json"))
    prompt_widget = PromptWidget(prompt_path)
    layout.addWidget(prompt_widget)

    # 設定ウィンドウ表示ボタン
    settings_button = QPushButton("設定")
    layout.addWidget(settings_button)

    # プログラム終了ボタン
    exit_button = QPushButton("終了")
    exit_button.clicked.connect(app.quit)
    layout.addWidget(exit_button)

    # 設定ウィンドウ表示ボタンの動作
    loaded_family = app.font().family()
    settings_window = SettingsWindow(app, loaded_family)
    def open_settings():
        settings_window.show()
        settings_window.raise_()
        settings_window.activateWindow()
    settings_button.clicked.connect(open_settings)

    # レイアウト設定と表示
    window.setLayout(layout)
    window.show()
    app.processEvents()
    try:
        prompt_widget.updateGeometry()
    except Exception:
        pass
    window.adjustSize()
    app.exec()

if __name__ == "__main__":
    main()