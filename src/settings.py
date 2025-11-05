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
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 255)
        self.font_size_spin.setValue(self._current_font_size())
        layout.addWidget(self.font_size_spin)
        # フォントサイズを変更するのを決定するボタン
        font_size_apply_button = QPushButton("適用")
        font_size_apply_button.clicked.connect(self.on_font_size_apply)
        layout.addWidget(font_size_apply_button)

        # 改行の閾値設定
        # タイトル
        self.label = QLabel("1行当たりの文字数")
        layout.addWidget(self.label)
        # 現在の1行当たりの文字数表示
        self.current_line_length = QLabel(str(self._current_line_length()))
        layout.addWidget(self.current_line_length)
        # スピンボックス
        self.line_length_spin = QSpinBox()
        self.line_length_spin.setRange(8, 255)
        self.line_length_spin.setValue(self._current_line_length())
        layout.addWidget(self.line_length_spin)
        # 1行当たりの文字数を変更するのを決定するボタン
        line_length_apply_button = QPushButton("適用")
        line_length_apply_button.clicked.connect(self.on_line_length_apply)
        layout.addWidget(line_length_apply_button)

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

    def _current_line_length(self) -> int:
        # トップレベルウィジェットからPromptWidgetを探して現在のline_lengthを返す
        try:
            from prompt_widget import PromptWidget
        except Exception:
            return 20
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, PromptWidget):
                # PromptWidget自体ではなくその内部のウィジェットかもしれないので再帰的に探索
                # 直接PromptWidgetのインスタンスを見つけたら値を取得
                try:
                    return max(8, int(getattr(widget, 'line_length', 20)))
                except Exception:
                    return 20
        return 20
    
    def on_font_size_apply(self):
        new_size = int(self.font_size_spin.value())
        # 現在のフォントサイズのラベル更新
        self.current_size.setText(str(new_size))
        # アプリ全体のフォントを更新
        if self.loaded_family:
            font = QFont(self.loaded_family, new_size)
        else:
            font = QFont("", new_size)
        self.app.setFont(font)

    def on_line_length_apply(self):
        new_length = int(self.line_length_spin.value())
        # ラベル更新
        self.current_line_length.setText(str(new_length))
        # トップレベルのPromptWidgetに反映
        try:
            from prompt_widget import PromptWidget
        except Exception:
            return
        for widget in QApplication.topLevelWidgets():
            # もしトップレベルがPromptWidgetの親ウィンドウなら、その中を探索
            if isinstance(widget, PromptWidget):
                try:
                    widget.line_length = new_length
                except Exception:
                    pass
            else:
                # ウィンドウ内の子を探索してPromptWidgetを探す
                def recurse_and_set(widget):
                    try:
                        for child in widget.findChildren(PromptWidget):
                            try:
                                child.line_length = new_length
                            except Exception:
                                pass
                    except Exception:
                        pass
                recurse_and_set(widget)

        # ジオメトリ/レイアウトを再計算してウィンドウが縮むようにする
        QApplication.processEvents()
        for widget in QApplication.topLevelWidgets():
            widget.updateGeometry()
            widget.adjustSize()
            widget.repaint()