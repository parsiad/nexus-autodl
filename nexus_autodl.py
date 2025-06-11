import logging
import random
import threading
import queue
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
    Toplevel,
    Text,
    Scrollbar,
    filedialog,
    messagebox,
)
from typing import Dict
from PIL import UnidentifiedImageError
from PIL.Image import open as open_image
import pyautogui

logger = logging.getLogger("NexusAutoDL")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

_INTEGER_PATTERN = re.compile(r"(\d+)")

def _human_sort(key: str):
    return tuple(int(token) if token.isdigit() else token for token in _INTEGER_PATTERN.split(str(key)))

def load_templates_from_dir(dir_path: Path) -> Dict[Path, "PIL.Image.Image"]:
    templates: Dict[Path, "PIL.Image.Image"] = {}
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)

    for file_path in sorted(dir_path.rglob("*"), key=lambda p: _human_sort(p.name)):
        if file_path.is_dir():
            continue
        if file_path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            logger.debug(f"Skipping invalid extension: {file_path.name}")
            continue
        try:
            img = open_image(file_path)
            templates[file_path] = img
            logger.debug(f"Loaded template: {file_path.name}")
        except UnidentifiedImageError:
            logger.debug(f"Skipping (not an image): {file_path.name}")
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")
    return templates

class MatcherThread(threading.Thread):
    def __init__(self, templates: Dict[Path, "PIL.Image.Image"], config: dict, event_queue: queue.Queue):
        super().__init__(daemon=True)
        self.templates = templates
        self.config = config
        self.event_queue = event_queue
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    def run(self):
        logger.info("MatcherThread started")
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                self._pause_event.wait(0.5)
                continue

            try:
                screenshot = pyautogui.screenshot()
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
                self.stop()
                return

            items = list(self.templates.items())
            random.shuffle(items)

            matched_any = False
            for path, img in items:
                try:
                    box = pyautogui.locate(
                        img,
                        screenshot,
                        grayscale=self.config["grayscale"],
                        confidence=self.config.get("confidence", 0.7),
                    )
                except AttributeError:
                    box = pyautogui.locate(img, screenshot, grayscale=self.config["grayscale"])
                except pyautogui.ImageNotFoundException:
                    box = None
                except pyautogui.FailSafeException:
                    logger.error("FailSafeException during locate; aborting thread.")
                    self.stop()
                    return
                except Exception as e:
                    logger.error(f"Unexpected error during locate: {e}")
                    continue

                if box:
                    matched_any = True

                    center_x, center_y = pyautogui.center(box)

                    tol = self.config.get("tol_pixels", 30)
                    offset_y = random.uniform(-tol, tol)
                    click_x = center_x
                    click_y = center_y + offset_y

                    try:
                        pyautogui.click(click_x, click_y)
                        logger.info(
                            f"Clicked on template '{path.name}' at (~{click_x:.0f}, {click_y:.0f}) "
                            f"(center = {center_x}, {center_y}; offset = {offset_y:.1f}px)"
                        )
                        self.event_queue.put((
                            "INFO",
                            f"Match: '{path.name}' with click at (~{click_x:.0f}, {click_y:.0f})"
                        ))
                    except pyautogui.FailSafeException:
                        logger.warning("FailSafeException during click; continuing.")
                    except Exception as e:
                        logger.error(f"Error clicking {path.name}: {e}")

                    break

            if not matched_any:
                self.event_queue.put(("DEBUG", "No template matched in this round."))

            sleep_time = random.uniform(self.config["min_sleep"], self.config["max_sleep"])
            self.event_queue.put(("INFO", f"Waiting {sleep_time:.2f} seconds"))
            self._stop_event.wait(sleep_time)

        logger.info("MatcherThread stopped")

    def stop(self):
        self._stop_event.set()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

class NexusAutoDL:
    def __init__(self, root: Tk) -> None:
        self._root = root
        self._root.title("Nexus AutoDL")
        self._root.resizable(False, False)

        self._confidence = DoubleVar(value=0.7)
        self._grayscale = BooleanVar(value=True)
        self._min_sleep_seconds = IntVar(value=1)
        self._max_sleep_seconds = IntVar(value=5)
        self._templates_path = StringVar(value="templates")
        self._tol_pixels = IntVar(value=30)

        Label(root, text="Confidence (0.0–1.0):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        Entry(root, textvariable=self._confidence, width=10).grid(row=0, column=1, padx=5, pady=5)

        Label(root, text="Min sleep (s):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        Entry(root, textvariable=self._min_sleep_seconds, width=10).grid(row=1, column=1, padx=5, pady=5)

        Label(root, text="Max sleep (s):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        Entry(root, textvariable=self._max_sleep_seconds, width=10).grid(row=2, column=1, padx=5, pady=5)

        Label(root, text="Templates dir:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        Entry(root, state="readonly", textvariable=self._templates_path, width=25).grid(row=3, column=1, padx=5, pady=5)
        Button(root, text="...", width=3, command=self._select).grid(row=3, column=2, padx=5, pady=5)

        Label(root, text="Grayscale:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        Checkbutton(root, variable=self._grayscale).grid(row=4, column=1, padx=5, pady=5)

        Label(root, text="Tolerance (px):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        Entry(root, textvariable=self._tol_pixels, width=10).grid(row=5, column=1, padx=5, pady=5)

        Button(root, text="Start", width=10, command=self._start).grid(row=6, column=0, columnspan=3, pady=10)

        self._log_text: Text | None = None
        self._thread: MatcherThread | None = None
        self._event_queue: queue.Queue = queue.Queue()
        self._templates: Dict[Path, "PIL.Image.Image"] = {}
        self._is_running = False

    def _log_to_widget(self, level: str, msg: str):
        if not self._log_text:
            return
        colors = {"DEBUG": "gray", "INFO": "orange", "WARNING": "purple", "ERROR": "red"}
        tag = level if level in colors else "INFO"
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log_text.insert("end", f"{timestamp} [{level}] {msg}\n", tag)
        self._log_text.tag_config(tag, foreground=colors.get(tag, "black"))
        self._log_text.yview_moveto(1)

    def _process_queue(self):
        while not self._event_queue.empty():
            level, msg = self._event_queue.get()
            self._log_to_widget(level, msg)
        if self._is_running:
            self._root.after(100, self._process_queue)

    def _select(self) -> None:
        abspath = filedialog.askdirectory(title="Select template directory")
        if not abspath:
            return
        try:
            path = str(Path(abspath).relative_to(Path.cwd()))
        except ValueError:
            path = abspath
        self._templates_path.set(path)

    def _start(self) -> None:
        try:
            conf = float(self._confidence.get())
        except Exception:
            messagebox.showerror("Error", "Invalid confidence value. Use decimal between 0 and 1.")
            return
        if not (0.0 <= conf <= 1.0):
            messagebox.showerror("Error", "Confidence must be between 0.0 and 1.0.")
            return

        ms = self._min_sleep_seconds.get()
        mx = self._max_sleep_seconds.get()
        if ms < 0 or mx < 0:
            messagebox.showerror("Error", "Sleep time cannot be negative.")
            return
        if ms > mx:
            messagebox.showerror("Error", "Min sleep cannot be greater than Max sleep.")
            return

        tol = self._tol_pixels.get()
        if tol < 0:
            messagebox.showerror("Error", "Pixel tolerance cannot be negative.")
            return

        self._root.withdraw()

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

        templates_dir = Path(self._templates_path.get())
        self._templates = load_templates_from_dir(templates_dir)
        total = len(self._templates)
        self._log_to_widget("INFO", f"{total} template(s) loaded from '{templates_dir}'.")
        if total == 0:
            self._log_to_widget("ERROR", "No valid templates found. Aborting.")
            return

        config = {
            "confidence": conf,
            "grayscale": self._grayscale.get(),
            "min_sleep": ms,
            "max_sleep": mx,
            "tol_pixels": tol,
        }

        self._thread = MatcherThread(self._templates, config, self._event_queue)
        self._thread.start()
        self._is_running = True

        self._process_queue()

        btn_frame = Frame(log_window)
        btn_frame.pack(pady=5)
        self._btn_pause = Button(btn_frame, text="Pause", width=10, command=self._toggle_pause)
        self._btn_pause.pack(side="left", padx=5)
        Button(btn_frame, text="Stop", width=10, command=self._terminate).pack(side="left", padx=5)

    def _toggle_pause(self):
        if not self._thread:
            return
        if self._thread._pause_event.is_set():
            self._thread.resume()
            self._btn_pause.config(text="Pause")
            self._log_to_widget("INFO", "Resuming matching.")
        else:
            self._thread.pause()
            self._btn_pause.config(text="Resume")
            self._log_to_widget("INFO", "Matching paused.")

    def _terminate(self):
        self._log_to_widget("INFO", "Shutting down application...")
        self._is_running = False
        if self._thread:
            self._thread.stop()
        self._root.quit()
        self._root.destroy()

if __name__ == "__main__":
    root = Tk()
    NexusAutoDL(root)
    root.mainloop()
