import random
import re
from datetime import datetime
from pathlib import Path
from tkinter import (
    BooleanVar,
    Button,
    Checkbutton,
    DoubleVar,
    Entry,
    Frame,
    IntVar,
    Label,
    StringVar,
    Tk,
    Text,
    Toplevel,
    Scrollbar,
    filedialog,
)

import pyautogui
from PIL import UnidentifiedImageError
from PIL.Image import open as open_image
from PIL.ImageFile import ImageFile

_INTEGER_PATTERN = re.compile("([0-9]+)")


def _human_sort(key):
    return tuple(int(c) if c.isdigit() else c for c in _INTEGER_PATTERN.split(str(key)))


class NexusAutoDL:
    def __init__(self, root) -> None:
        self._root = root
        self._root.title("Nexus AutoDL")
        self._root.resizable(False, False)

        self._confidence = DoubleVar(value=0.7)
        self._grayscale = BooleanVar(value=True)
        self._min_sleep_seconds = IntVar(value=1)
        self._max_sleep_seconds = IntVar(value=5)
        self._templates_path = StringVar(value="templates")

        Label(root, text="Confidence:").grid(row=0, column=0, sticky="w")
        Entry(root, textvariable=self._confidence).grid(row=0, column=1)

        Label(root, text="Min sleep seconds:").grid(row=1, column=0, sticky="w")
        Entry(root, textvariable=self._min_sleep_seconds).grid(row=1, column=1)

        Label(root, text="Max sleep seconds:").grid(row=2, column=0, sticky="w")
        Entry(root, textvariable=self._max_sleep_seconds).grid(row=2, column=1)

        Label(root, text="Templates directory:").grid(row=3, column=0, sticky="w")
        Entry(root, state="readonly", textvariable=self._templates_path).grid(row=3, column=1)
        Button(root, text="...", command=self._select).grid(row=3, column=2)

        Label(root, text="Grayscale:").grid(row=4, column=0, sticky="w")
        Checkbutton(root, variable=self._grayscale).grid(row=4, column=1)

        Button(root, text="Start", command=self._start).grid(row=5, column=0, columnspan=3)

        self._log_text = None
        self._templates: dict[str, ImageFile] = {}

    def _log(self, message: str, fatal: bool = False) -> None:
        assert self._log_text is not None
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if fatal:
            self._log_text.insert("end", "FATAL ", "fatal")
        else:
            self._log_text.insert("end", "INFO ", "info")
        self._log_text.insert("end", f"[{timestamp}] ", "timestamp")
        self._log_text.insert("end", f"{message}\n")
        self._log_text.tag_config("fatal", foreground="red")
        self._log_text.tag_config("info", foreground="orange")
        self._log_text.tag_config("timestamp", foreground="blue")
        self._log_text.yview_moveto(1)  # Scroll to the end

    def _match(self):
        try:
            self._match_impl()
        except Exception as e:
            self._log(str(e), fatal=True)

    def _match_impl(self):
        confidence = self._confidence.get()
        grayscale = self._grayscale.get()
        min_sleep_seconds = self._min_sleep_seconds.get()
        max_sleep_seconds = self._max_sleep_seconds.get()

        if len(self._templates) == 0:
            self._log(f"No valid images found in {self._templates_path.get()}", fatal=True)
            return

        screenshot = pyautogui.screenshot()

        for template_path, template_image in self._templates.items():
            self._log(f"Attempting to match {template_path}.")

            box = None
            try:
                box = pyautogui.locate(template_image, screenshot, confidence=confidence, grayscale=grayscale)
            except pyautogui.ImageNotFoundException:
                pass
            if not box:
                continue

            match_x, match_y = pyautogui.center(box)
            pyautogui.click(match_x, match_y)
            self._log(f"Matched at ({match_x}, {match_y}).")
            break

        sleep_interval = random.uniform(min_sleep_seconds, max_sleep_seconds)
        self._log(f"Waiting for {sleep_interval:.2f} seconds.")
        self._root.after(int(sleep_interval * 1000), self._match)

    def _select(self) -> None:
        abspath = filedialog.askdirectory()
        if not abspath:
            return
        relpath = str(Path(abspath).relative_to(Path.cwd()))
        self._templates_path.set(relpath)

    def _start(self):
        self._root.withdraw()  # Close the current window

        log_window = Toplevel(self._root)
        log_window.title("Logging Console")
        log_window.protocol("WM_DELETE_WINDOW", self._terminate)

        frame = Frame(log_window)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        self._log_text = Text(frame, height=20, width=80, wrap="char")
        self._log_text.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame, command=self._log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self._log_text.config(yscrollcommand=scrollbar.set)

        templates_path_ = Path(self._templates_path.get())
        templates_path_.mkdir(exist_ok=True)

        for template_path in sorted(
            (str(template_path) for template_path in templates_path_.iterdir()),
            key=_human_sort,
        ):
            try:
                self._templates[template_path] = open_image(template_path)
                self._log(f"Loaded {template_path}")
            except IsADirectoryError:
                self._log(f"Skipping directory {template_path}")
            except UnidentifiedImageError:
                self._log(f"Skipping non-image {template_path}")
            except Exception as e:
                self._log(str(e), fatal=True)

        self._match()

    def _terminate(self) -> None:
        self._root.quit()  # Stop the Tkinter event loop
        self._root.destroy()  # Close all windows and terminate the application


if __name__ == "__main__":
    root = Tk()
    NexusAutoDL(root)
    root.mainloop()
