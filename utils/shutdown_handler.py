import asyncio
import signal

class GracefulShutdown:
    def __init__(self):
        self.triggered = False

    def register_signals(self, loop):
        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(s, self._shutdown)
            except (NotImplementedError, RuntimeError):
                # Windows/active loop fallback
                signal.signal(s, lambda *_: self._shutdown())

    def _shutdown(self):
        self.triggered = True

