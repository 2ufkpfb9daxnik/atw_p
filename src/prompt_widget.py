import json
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class PromptWidget(QWidget):
    def __init__(self, prompt_path: str | None = None, parent=None):
        super().__init__(parent)
        self.kanji_label = QLabel("漢字仮名交じり文")
        self.kana_label = QLabel("かな文")
        self.preedit_label = QLabel("打鍵列")

        self.kanji_label.setWordWrap(True)
        self.kanji_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.kana_label.setWordWrap(True)
        self.kana_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.preedit_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.kanji_label)
        layout.addWidget(self.kana_label)
        layout.addWidget(self.preedit_label)
        self.setLayout(layout)

        if prompt_path:
            self.load_and_show_first(prompt_path)

    def set_prompt(self, text: str, kana: str = ""):
        self.kanji_label.setText(text)
        self.kana_label.setText(kana)
        self.preedit_label.setText("")
        
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
