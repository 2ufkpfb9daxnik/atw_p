from PyQt6.QtCore import QObject, QTimer
from typing import Optional, Callable

class TimerController(QObject):
    def __init__(self, parent=None,
                 tick_callback: Optional[Callable[[int], None]] = None,
                 finished_callback: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_timeout)
        self._remaining = 0
        self._running = False
        self._tick_callback = tick_callback
        self._finished_callback = finished_callback

    def start(self, seconds: int):
        self._remaining = int(seconds)
        self._running = True
        # 即時に現在残りを通知
        if self._tick_callback:
            self._tick_callback(self._remaining)
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self._running = False
        self._remaining = 0
    
    def _on_timeout(self):
        if self._remaining > 0:
            self._remaining -= 1
            if self._tick_callback:
                self._tick_callback(self._remaining)
            if self._remaining == 0:
                self._timer.stop()
                self._running = False
                if self._finished_callback:
                    self._finished_callback()
        else:
            self._timer.stop()
            self._running = False
            if self._finished_callback:
                self._finished_callback()
    
    def remainng(self) -> int:
        return int(self._remaining)
    
    def is_running(self) -> bool:
        return bool(self._running)