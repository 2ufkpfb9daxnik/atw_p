import os
import json
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class PromptWidget(QWidget):
    def __init__(self, prompt_path: str | None = None, parent=None):
        super().__init__(parent)
        self.kanji_label = QLabel("漢字仮名交じり文")
        self.kana_label = QLabel("かな文")
        self.romaji_label = QLabel("ローマ字文")

        self.kanji_label.setWordWrap(True)
        self.kanji_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.kana_label.setWordWrap(True)
        self.kana_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.romaji_label.setWordWrap(True)
        self.romaji_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.kanji_label)
        layout.addWidget(self.kana_label)
        layout.addWidget(self.romaji_label)
        self.setLayout(layout)

        if prompt_path:
            self.load_and_show_first(prompt_path)

    def set_prompt(self, text: str, kana: str = ""):
        self.kanji_label.setText(text)
        self.kana_label.setText(kana)
        self.romaji_label.setText(self.to_romaji(text))

    def load_and_show_first(self, prompt_path: str):
        try:
            with open(prompt_path, "r", encoding="utf-8") as file:
                arr = json.load(file)
            if isinstance(arr, list) and arr:
                first = arr[0]
                
                text = first.get("text", "")
                kana = first.get("kana", "")
                self.set_prompt(text, kana)
        except Exception:
            self.set_prompt("お題読み込み失敗", "")

    def to_romaji(self, text: str) -> str:
        return text# 後で作る