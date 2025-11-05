import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, 
    QPushButton, QComboBox, QTimeEdit
)
from PyQt6.QtCore import Qt, QSize, QTime
from PyQt6.QtGui import QKeySequence, QShortcut
from timer import TimerController

class PromptWidget(QWidget):
    def __init__(self, prompt_path: str | None = None, parent=None):
        super().__init__(parent)
        # 計測開始ボタン
        self.start_button = QPushButton("開始[s]")
        self.start_button.clicked.connect(self.on_start_clicked)

        # ショートカットキーの設定(sで計測開始)
        self._shortcut_s = QShortcut(QKeySequence("s"), self)
        self._shortcut_s.activated.connect(self.on_s_pressed)

        # ショートカットキーの設定(ESCで計測停止)
        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self.on_escape_pressed)

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
        self.text_label = QLabel("")
        self.kana_label = QLabel("")
        self.preedit_label = QLabel("")

        self.text_label.setWordWrap(False)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.kana_label.setWordWrap(False)
        self.kana_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.preedit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        # 計測開始ボタン、選択、残り時間を横並びで配置
        timer_top = QHBoxLayout()
        timer_top.addWidget(self.start_button)
        timer_top.addWidget(self.time_label)
        timer_top.addWidget(self.duration_selector)
        timer_top.addWidget(self.time_edit)
        timer_top.addStretch()
        layout.addLayout(timer_top)

        # 規定のテンプレートはレイアウトに追加しない
        # layout.addWidget(self.text_label)
        # layout.addWidget(self.kana_label)
        # layout.addWidget(self.preedit_label)

        # お題はここに行グループを追加していく(text, (kana,) preeditのグループを縦に積む)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        self.setLayout(layout)

        self._conversion_enabled = False

        # 行長のデフォルト
        self._line_length = 25

        # 最後に表示した元テキスト(再描画用)
        self._last_text = None
        self._last_kana = None

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
            self.start_button.setText("停止[Esc]")
        else:
            print("Start button clicked -> stop timer")
            self._timer.stop()
            self._on_timer_finished()

    def on_s_pressed(self):
        print(f"s key pressed -> start timer")
        if not hasattr(self, "_timer") or not self._timer.is_running():
            if self.duration_selector.currentText() == "カスタム":
                time = self.time_edit.time()
                seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
                if seconds <= 0:
                    print("カスタム時間が0秒以下のため計測を開始できません")
                    return
            else:
                seconds = self._initial_seconds
            print(f"Start (shortcut) -> start {seconds}s timer")
            self.duration_selector.setEnabled(False)
            self.time_edit.setEnabled(False)
            self._timer.start(seconds)
            self.start_button.setText("停止[Esc]")
        else:
            print("s pressed (no-op): timer already running")
    
    def on_escape_pressed(self):
        if hasattr(self, "_timer") and self._timer.is_running():
            print("Escape key pressed -> stop timer")
            self._timer.stop()
            self._on_timer_finished()
        else:
            print("Escape pressed (no-op): timer not running")

    # TimeContollerから呼ばれるコールバック(残り秒数を受け取る)
    def _on_timer_tick_callback(self, remaining: int):
        print(f"timer tick: remaining={remaining}")
        self._set_time_label_from_seconds(remaining)

    # タイマー終了時コールバック
    def _on_timer_finished(self):
        print("timer finished or stopped")
        self.start_button.setText("開始[s]")
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
        # kana_labelの表示/非表示はcontent_layoutの再描画で制御する
        if getattr(self, "_last_text", None) is not None:
            # 再描画してkanaの行を反映
            self.set_prompt(self._last_text or "", self._last_kana or "")
        else:
            # ウィジェット全体を再計算
            self.updateGeometry()
            top = self.window()
            if top is not None:
                top.adjustSize()

    def set_prompt(self, text: str, kana: str = ""):
        # 最後に表示した値を保存(line_length変更時に再描画するため)
        self._last_text = text
        self._last_kana = kana

        # 古い行グループを削除
        while self.content_layout.count():
            it = self.content_layout.takeAt(0)
            widget = it.widget()
            if widget:
                widget.deleteLater()
            else:
                # レイアウトが残っている場合は中身を削除
                sub = it.layout()
                if sub:
                    while sub.count():
                        it2 = sub.takeAt(0)
                        widget2 = it2.widget()
                        if widget2:
                            widget2.deleteLater()
            
        def chunks(s: str, n: int):
            return [s[i:i+n] for i in range(0, len(s), n)] if s else []

        n = max(1, int(self._line_length))
        text_chunks = chunks(text, n)
        kana_chunks = chunks(kana, n)
        max_chunks = max(1, len(text_chunks), len(kana_chunks))

        # 各チャンクについてグループ(QWidget)を作ってcontent_layoutに追加
        for i in range(max_chunks):
            row_widget = QWidget()
            row_layout = QVBoxLayout(row_widget)
            # text
            text = text_chunks[i] if i < len(text_chunks) else ""
            label_text = QLabel(text)
            label_text.setWordWrap(False)
            label_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(label_text)
            # kana(変換ありモードでは表示しない)
            if not self._conversion_enabled:
                kana = kana_chunks[i] if i < len(kana_chunks) else ""
                label_kana = QLabel(kana)
                label_kana.setWordWrap(False)
                label_kana.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                row_layout.addWidget(label_kana)
            # predit(今は空だが順序を保つため追加)
            label_predit = QLabel("")
            label_predit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(label_predit)
            
            # マージンを小さくして詰める
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(2)

            self.content_layout.addWidget(row_widget)
        
        self.updateGeometry()
        top = self.window()
        if top is not None:
            top.adjustSize()

    @property
    def line_length(self) -> int:
        return int(self._line_length)
    
    @line_length.setter
    def line_length(self, v: int):
        # 最低値を保障
        try:
            v = int(v)
        except Exception:
            return
        if v < 1:
            v = 1
        if self._line_length == v:
            return
        self._line_length = v
        # すでに描画しているお題があれば再描画して反映
        if getattr(self, "_last_text", None) is not None:
            self.set_prompt(self._last_text, self._last_kana)

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
        # content_layoutに行がある場合はその行のテキストを使って幅を計算
        sample_text = ""
        if self.content_layout.count() > 0:
            it = self.content_layout.itemAt(0)
            widget = it.widget()
            if widget:
                # その行の最初のQLabelを探す
                first_label = None
                for child in widget.findChildren(QLabel):
                    first_label = child
                    break
                if first_label is not None:
                    sample_text = first_label.text() or ""
        else:
            # fallback: テンプレートラベル(空)を利用
            sample_text = self.text_label.text() or ""
        
        fontMetrics = self.fontMetrics()
        width = fontMetrics.horizontalAdvance(sample_text) + 20  # 余白分を追加
        # 高さは各ラベルの高さの合計
        height = (self.start_button.sizeHint().height()
                  + self.text_label.sizeHint().height()
                  + self.kana_label.sizeHint().height()
                  + self.preedit_label.sizeHint().height())
        return QSize(max(100, width), height)
    