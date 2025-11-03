from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSpinBox, QLabel
from PyQt6.QtGui import QFont

class SettingsWindow(QWidget):
    def __init__(self, app: QApplication, loaded_family: str | None, parent=None):
        super().__init__(parent)
        self.app = app
        self.loaded_family = loaded_family

        self.setWindowTitle("設定")
        layout = QVBoxLayout()

        # フォントサイズ設定
        # タイトル
        self.label = QLabel("現在のフォントサイズ")
        layout.addWidget(self.label)
        # 現在のフォントサイズ表示
        self.current_size = QLabel(str(self._current_font_size()))
        layout.addWidget(self.current_size)

        # スピンボックス
        self.spin = QSpinBox()
        self.spin.setRange(8, 255)
        self.spin.setValue(self._current_font_size())
        layout.addWidget(self.spin)
        
        # フォントサイズを変更するのを決定するボタン
        apply_button = QPushButton("適用")
        apply_button.clicked.connect(self.on_apply)
        layout.addWidget(apply_button)

        # 設定ウィンドウを閉じるボタン
        close_button = QPushButton("閉じる")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        self.setLayout(layout)

    def _current_font_size(self) -> int:
        pointSize = self.app.font().pointSize()
        if pointSize == -1:
            pointSize = 20
        return pointSize
    
    def on_apply(self):
        new_size = int(self.spin.value())
        # 現在のフォントサイズのラベル更新
        self.current_size.setText(str(new_size))
        # アプリ全体のフォントを更新
        if self.loaded_family:
            font = QFont(self.loaded_family, new_size)
        else:
            font = QFont("", new_size)
        self.app.setFont(font)

        # ジオメトリ/レイアウトを再計算してウィンドウが縮むようにする
        QApplication.processEvents()
        for widget in QApplication.topLevelWidgets():
            widget.updateGeometry()
            widget.adjustSize()
            widget.repaint()