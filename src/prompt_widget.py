import json
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QSize

class PromptWidget(QWidget):
    def __init__(self, prompt_path: str | None = None, parent=None):
        super().__init__(parent)
        self.text_label = QLabel("漢字仮名交じり文")
        self.kana_label = QLabel("かな文")
        self.preedit_label = QLabel("打鍵列")

        self.text_label.setWordWrap(False)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.kana_label.setWordWrap(False)
        self.kana_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.preedit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.kana_label)
        layout.addWidget(self.preedit_label)
        self.setLayout(layout)

        # 子が希望サイズを持つようにポリシーを設定
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if prompt_path:
            self.load_and_show_first(prompt_path)

    def set_prompt(self, text: str, kana: str = ""):
        self.text_label.setText(text)
        self.kana_label.setText(kana)
        self.preedit_label.setText("")
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
        # 希望幅をテキストの長さとフォントから計算
        fontMetrics = self.kana_label.fontMetrics()
        text = self.kana_label.text() or ""
        width = fontMetrics.horizontalAdvance(text) + 20  # 余白分を追加
        # 高さはデフォルトのまま
        height = self.text_label.sizeHint().height() + self.kana_label.sizeHint().height() + self.preedit_label.sizeHint().height()
        return QSize(width, height)