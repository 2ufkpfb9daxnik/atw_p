from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QFontDatabase, QFont
import os

def main():
    app = QApplication([])

    # フォント読み込み
    font_path = "../assets/NotoSansJP-Regular.ttf"
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)
            if font_family:
                app.setFont(QFont(font_family[0], 10))

    # ウィンドウ初期化
    window = QWidget()
    window.setWindowTitle("atw")
    layout = QVBoxLayout()

    # プログラム終了ボタン
    button = QPushButton("終了")
    button.clicked.connect(app.quit)
    layout.addWidget(button)

    # レイアウト設定と表示
    window.setLayout(layout)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()