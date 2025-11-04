import json
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt, QSize, QTimer

class PromptWidget(QWidget):
    def __init__(self, prompt_path: str | None = None, parent=None):
        super().__init__(parent)
        # 計測開始ボタン
        self.start_button = QPushButton("計測開始")
        self.start_button.clicked.connect(self.on_start_clicked)

        # タイマー残り時間表示ラベル
        self.time_label = QLabel("残り時間: 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.text_label = QLabel("漢字仮名交じり文")
        self.kana_label = QLabel("かな文")
        self.preedit_label = QLabel("打鍵列")

        self.text_label.setWordWrap(False)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.kana_label.setWordWrap(False)
        self.kana_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.preedit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        # 計測開始ボタンを左寄せにするために水平レイアウトに配置してから垂直レイアウトへ追加
        timer_layout = QHBoxLayout()
        timer_layout.addWidget(self.start_button)
        timer_layout.addWidget(self.time_label)
        timer_layout.addStretch()
        layout.addLayout(timer_layout)

        layout.addWidget(self.text_label)
        layout.addWidget(self.kana_label)
        layout.addWidget(self.preedit_label)
        self.setLayout(layout)

        self._conversion_enabled = False

        # 子が希望サイズを持つようにポリシーを設定
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_timer_tick)
        self._remaining_seconds = 0
        self._timer_running = False

        if prompt_path:
            self.load_and_show_first(prompt_path)

    def on_start_clicked(self):
        # 押したら開始、実行中に押すと停止
        if not self._timer_running:
            print("Start button clicked -> start 60s timer")
            self._start_timer(seconds=60)
        else:
            print("Start button clicked -> stop timer")
            self._stop_timer()

    def _start_timer(self, seconds: int):
        self._remaining_seconds = int(seconds)
        self._update_time_label()
        self._timer.start()
        self._timer_running = True
        self.start_button.setText("停止")

    def _stop_timer(self):
        self._timer.stop()
        self._timer_running = False
        self.start_button.setText("計測開始")
        self._remaining_seconds = 0
        self._update_time_label()

    def _on_timer_tick(self):
        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._update_time_label()
            print(f"timer tick: remaining={self._remaining_seconds}")
            if self._remaining_seconds == 0:
                print("timer finished")
                self._stop_timer()
        
        else:
            self._stop_timer()

    def _update_time_label(self):
        minutes = self._remaining_seconds // 60
        seconds = self._remaining_seconds % 60
        self.time_label.setText(f"{minutes:02}:{seconds:02}")

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
        height = self.text_label.sizeHint().height() + self.kana_label.sizeHint().height() + self.preedit_label.sizeHint().height()
        return QSize(max(100, width), height)
    