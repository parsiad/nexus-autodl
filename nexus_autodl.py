#!/usr/bin/env python

import logging
import random
import re
import sys
import time
from pathlib import Path
from typing import Iterator

import click
import pyautogui
from PIL import UnidentifiedImageError
from PIL.Image import Image, open as open_image
from pyautogui import ImageNotFoundException
from pyscreeze import Box

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def human_sorted(paths: Iterator[Path]) -> list[Path]:
    pattern = re.compile("([0-9]+)")

    def key(key: Path) -> tuple[int | str, ...]:
        return tuple(int(c) if c.isdigit() else c for c in pattern.split(str(key)))

    return sorted(paths, key=key)


@click.command()
@click.option("--confidence", default=0.7, show_default=True, help="Specifies the accuracy with which the script should find the screenshot button")
@click.option("--grayscale/--color", default=True, show_default=True, help="Try to locate button using only desaturated images, can speed up the locating action")
@click.option("--min-sleep-interval", default=1, show_default=True, help="Minumal amount of time to wait between every click attempt")
@click.option("--max-sleep-interval", default=5, show_default=True, help="Minumal amount of time to wait between every click attempt")
@click.option("--retries-before-scroll", default=3, show_default=True, help="Amount of failed attemps before trying to scroll down")
@click.option("--disable-transparent-ads-fix", default=False, show_default=True, help="Disable the functionality that can potentially locate transparent ads which prevent clicking")
@click.option("--templates-path", default=Path.cwd() / "templates", show_default=True, help="Set a path to the folder with button screenshots")
def main(
    confidence: float,
    grayscale: bool,
    min_sleep_interval: int,
    max_sleep_interval: int,
    templates_path: str,
    retries_before_scroll: int,
    disable_transparent_ads_fix: bool,
    ) -> None:
    transparent_ads_fix = 5
    matched = False
    templates_path_ = Path(templates_path)
    retries_before_scroll_ = retries_before_scroll
    templates: dict[Path, Image] = {}
    try:
        for template_path in human_sorted(templates_path_.iterdir()):
                templates[template_path] = open_image(template_path)
                logging.info(f"Loaded {template_path}")
    except UnidentifiedImageError:
                logging.info(f"{template_path} is not a valid image; skipping")
    except FileNotFoundError:
        
        logging.error(
            f"No images found in {templates_path_.absolute()}. "
            f"If this is your first time running, take a screenshot and crop "
            f"(WIN+S on Windows) the item on the screen you want to click on, "
            f"placing the result in the {templates_path_.absolute()} directory."
        )
        input("Press ENTER to exit.")
        sys.exit(1)

    while True:
        screenshot = pyautogui.screenshot()

        for template_path, template_image in templates.items():
            logging.info(f"Attempting to match {template_path}.")
            box: Box | None = None
            try:
                box = pyautogui.locate(
                    template_image,
                    screenshot,
                    grayscale=grayscale,
                    confidence=confidence,
                )
            except ImageNotFoundException:
                pass
            if not isinstance(box, Box):
                if not retries_before_scroll_:
                    logging.info(f"Picture matching failed, attempting to scroll.")
                    pyautogui.scroll(-40)
                else:
                    retries_before_scroll_ -= 1
                    matched = False
                continue
            if matched:
                transparent_ads_fix -= 1
            else:
                transparent_ads_fix = 5
            if not transparent_ads_fix and not disable_transparent_ads_fix:
                logging.info(f"Potential transparent ad encountered, attempting to scroll.")
                pyautogui.scroll(-40)
                transparent_ads_fix = 5
            matched = True
            retries_before_scroll_ = retries_before_scroll
            match_x, match_y = pyautogui.center(box)
            pyautogui.click(match_x, match_y)
            logging.info(f"Matched at ({match_x}, {match_y}).")
            pyautogui.moveTo(400, 400)
            break

        sleep_interval = random.uniform(min_sleep_interval, max_sleep_interval)
        logging.info(f"Waiting for {sleep_interval:.2f} seconds.")
        time.sleep(sleep_interval)


if __name__ == "__main__":
    main()
