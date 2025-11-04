from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox, QSizePolicy
from PyQt6.QtGui import QFontDatabase, QFont, QFontMetrics
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

    # 左側のコントロール群
    left_controls = QVBoxLayout()
    # 変換モード切替チェックボックス(上寄せ)
    convert_checkbox_on = QCheckBox("変換あり")
    convert_checkbox_off = QCheckBox("変換なし")
    convert_checkbox_on.setChecked(False)
    convert_checkbox_off.setChecked(True)
    left_controls.addWidget(convert_checkbox_on)
    left_controls.addWidget(convert_checkbox_off)

    # 中央の伸縮領域でスペースを確保
    left_controls.addStretch()

    # prompt_widgetを参照するため先にNoneを置いておく
    prompt_widget = None

    # 相互排他かつ「すでにONのものをクリックしてもOFFにしない」ハンドラ
    def on_convert(checked: bool):
        print(f"on_convert called with checked = {checked}")
        # 択一で常にどちらかがONにしたいので、OFFにしようとしたら元に戻す
        if not checked:
            convert_checkbox_on.blockSignals(True)
            convert_checkbox_on.setChecked(True)
            convert_checkbox_on.blockSignals(False)
            return
        # checked == True: もう一方をオフにして状態適用
        convert_checkbox_off.blockSignals(True)
        convert_checkbox_off.setChecked(False)
        convert_checkbox_off.blockSignals(False)
        # prompt_widgetが作成済みならプロパティ経由で反映
        if prompt_widget is not None:
            prompt_widget.conversion_enabled = True

    def off_convert(checked: bool):
        print(f"off_convert called with checked = {checked}")
        # 択一で常にどちらかがONにしたいので、OFFにしようとしたら元に戻す
        if not checked:
            convert_checkbox_off.blockSignals(True)
            convert_checkbox_off.setChecked(True)
            convert_checkbox_off.blockSignals(False)
            return
        # checked == True: もう一方をオフにして状態適用
        convert_checkbox_on.blockSignals(True)
        convert_checkbox_on.setChecked(False)
        convert_checkbox_on.blockSignals(False)
        # prompt_widgetが作成済みならプロパティ経由で反映
        if prompt_widget is not None:
            prompt_widget.conversion_enabled = False

    convert_checkbox_on.toggled.connect(on_convert)
    convert_checkbox_off.toggled.connect(off_convert)

    # 設定ウィンドウ表示ボタン
    settings_button = QPushButton("設定")
    left_controls.addWidget(settings_button)

    # プログラム終了ボタン
    exit_button = QPushButton("終了")
    exit_button.clicked.connect(app.quit)
    left_controls.addWidget(exit_button)

    # 設定ウィンドウ表示ボタンの動作
    loaded_family = app.font().family()
    settings_window = SettingsWindow(app, loaded_family)
    def open_settings():
        settings_window.show()
        settings_window.raise_()
        settings_window.activateWindow()
    settings_button.clicked.connect(open_settings)

    # 右側のお題表示エリア
    right_area = QVBoxLayout()

    # お題ウィジェット
    prompt_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "prompt.json"))
    prompt_widget = PromptWidget(prompt_path)
    # 初期状態をprompt_widgetに反映
    prompt_widget._conversion_enabled = False
    right_area.addWidget(prompt_widget)

    # レイアウト設定
    root_layout = QHBoxLayout()
    root_layout.addLayout(left_controls)
    root_layout.addLayout(right_area)
    window.setLayout(root_layout)

    # 表示
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