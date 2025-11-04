import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, 
    QPushButton, QComboBox, QTimeEdit
)
from PyQt6.QtCore import Qt, QSize, QTime
from timer import TimerController

class PromptWidget(QWidget):
    def __init__(self, prompt_path: str | None = None, parent=None):
        super().__init__(parent)
        # 計測開始ボタン
        self.start_button = QPushButton("開始")
        self.start_button.clicked.connect(self.on_start_clicked)

        # タイマー選択 (1分 / 1時間 /カスタム)
        self.duration_selector = QComboBox()
        self.duration_selector.addItems(["1分", "1時間", "カスタム"])
        # デフォルトは1分
        self.duration_selector.setCurrentIndex(0)

        # タイマー残り時間表示ラベル
        self.time_label = QLabel("00:01:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # カスタム入力用の時間エディット
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm:ss")
        self.time_edit.setTime(QTime(0, 1, 0))
        # time_editは最初は非表示
        self.time_edit.setVisible(False)

        # テキスト表示部
        self.text_label = QLabel("漢字仮名交じり文")
        self.kana_label = QLabel("かな文")
        self.preedit_label = QLabel("打鍵列")

        self.text_label.setWordWrap(False)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.kana_label.setWordWrap(False)
        self.kana_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.preedit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        # 計測開始ボタン、選択、残り時間を横並びで配置
        timer_top = QHBoxLayout()
        timer_top.addWidget(self.start_button)
        timer_top.addWidget(self.duration_selector)
        timer_top.addWidget(self.time_label)
        timer_top.addWidget(self.time_edit)
        timer_top.addStretch()
        layout.addLayout(timer_top)

        layout.addWidget(self.text_label)
        layout.addWidget(self.kana_label)
        layout.addWidget(self.preedit_label)
        self.setLayout(layout)

        self._conversion_enabled = False

        # 子が希望サイズを持つようにポリシーを設定
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # TimerControllerにコールバックを渡して分離
        self._timer = TimerController(self,
                                     tick_callback = self._on_timer_tick_callback,
                                     finished_callback = self._on_timer_finished)

        # 内部状態
        self._initial_seconds = 60 # デフォルト1分
        self._update_time_display_from_selection()

        # シグナル接続
        self.duration_selector.currentIndexChanged.connect(self._on_duration_changed)

        if prompt_path:
            self.load_and_show_first(prompt_path)

    def _on_duration_changed(self, index: int):
        # 0: 1分, 1: 1時間, 2: カスタム
        select = self.duration_selector.currentText()
        if select == "1分":
            self.time_edit.setVisible(False)
            self._initial_seconds = 60
            self._set_time_label_from_seconds(self._initial_seconds)
        elif select == "1時間":
            self.time_edit.setVisible(False)
            self._initial_seconds = 60 * 60
            self._set_time_label_from_seconds(self._initial_seconds)
        else: # カスタム
            # time_editを表示し、time_editの値を初期化
            self.time_edit.setVisible(True)
            time = self.time_edit.time()
            self._initial_seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
            # ラベルに反映
            self._set_time_label_from_seconds(self._initial_seconds)

    def on_start_clicked(self):
        # 押したら開始、実行中に押すと停止
        if not self._timer.is_running():
            # 開始秒数を決定する
            if self.duration_selector.currentText() == "カスタム":
                # time_editの値を使う
                time = self.time_edit.time()
                seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
                if seconds <= 0:
                    print("カスタム時間が0秒以下のため計測を開始できません")
                    return
            else:
                seconds = self._initial_seconds
            print(f"Start button clicked -> start {seconds}s timer")
            # 実行中はセレクタとtime_editを無効化
            self.duration_selector.setEnabled(False)
            self.time_edit.setEnabled(False)
            self._timer.start(seconds)
            self.start_button.setText("停止")
        else:
            print("Start button clicked -> stop timer")
            self._timer.stop()
            self._on_timer_finished()

    # TimeContollerから呼ばれるコールバック(残り秒数を受け取る)
    def _on_timer_tick_callback(self, remaining: int):
        print(f"timer tick: remaining={remaining}")
        self._set_time_label_from_seconds(remaining)

    # タイマー終了時コールバック
    def _on_timer_finished(self):
        print("timer finished or stopped")
        self.start_button.setText("開始")
        # セレクタとtime_editを有効化
        self.duration_selector.setEnabled(True)
        # カスタム選択時のみtime_editを有効化
        if self.duration_selector.currentText() == "カスタム":
            self.time_edit.setEnabled(True)
        else:
            self.time_edit.setEnabled(False)
        # 残り時間を初期値に戻す
        self._set_time_label_from_seconds(self._initial_seconds)

    def _set_time_label_from_seconds(self, seconds: int):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        self.time_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    def _update_time_display_from_selection(self):
        index = self.duration_selector.currentIndex()
        if index == 0:
            self._initial_seconds = 60
        elif index == 1:
            self._initial_seconds = 3600
        else:
            time = self.time_edit.time()
            self._initial_seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
            self.time_edit.setVisible(True)
        self._set_time_label_from_seconds(self._initial_seconds)

    @property
    def conversion_enabled(self) -> bool:
        return bool(self._conversion_enabled)
    
    @conversion_enabled.setter
    def conversion_enabled(self, v: bool):
        print(f"PromptWidget: set conversion_enabled to {v}")
        self._conversion_enabled = bool(v)
        # 変換ありなら、kana_labelを隠す
        self.kana_label.setVisible(not self._conversion_enabled)
        # レイアウト・親ウィンドウを更新してサイズを再計算させる
        self.updateGeometry()
        top = self.window()
        if top is not None:
            top.adjustSize()

    def set_prompt(self, text: str, kana: str = ""):
        self.text_label.setText(text)
        self.kana_label.setText(kana)
        self.preedit_label.setText("")
        # conversion_enabledの状態に応じて表示を更新
        self.kana_label.setVisible(not self._conversion_enabled)
        # 自分のジオメトリを更新してから親を再調整する
        self.updateGeometry()
        top = self.window()
        if top is not None:
            top.adjustSize()
        
    def set_preedit(self, preedit: str):
        self.preedit_label.setText(preedit)

    def load_and_show_first(self, prompt_path: str):
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                prompt = json.load(file)
            if isinstance(prompt, list) and prompt:
                first = prompt[0]
                
                text = first.get("text", "")
                kana = first.get("kana", "")
                self.set_prompt(text, kana)
        except Exception:
            self.set_prompt("お題読み込み失敗", "")

    def sizeHint(self) -> QSize:
        if self._conversion_enabled:
            fontMetrics = self.text_label.fontMetrics()
            text = self.text_label.text() or ""
        else:
            fontMetrics = self.kana_label.fontMetrics()
            text = self.kana_label.text() or ""
        width = fontMetrics.horizontalAdvance(text) + 20  # 余白分を追加
        # 高さは各ラベルの高さの合計
        height = (self.start_button.sizeHint().height()
                  + self.text_label.sizeHint().height()
                  + self.kana_label.sizeHint().height()
                  + self.preedit_label.sizeHint().height())
        return QSize(max(100, width), height)
    