#!/usr/bin/env python

# pylint: disable=missing-module-docstring

import os
import logging
import random
import sys
import time

import click
import cv2 as cv  # type: ignore
import numpy as np
import PIL
import PIL.ImageOps
import pyautogui  # type: ignore


@click.command()
@click.option('--sleep_max', default=5.)
@click.option('--sleep_min', default=0.)
def run(sleep_max: float, sleep_min: float) -> None:  # pylint: disable=missing-function-docstring
    logging.basicConfig(
        datefmt='%m/%d/%Y %I:%M:%S %p',
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.INFO,
    )
    templates = _get_templates()
    while True:
        sleep_seconds = random.uniform(sleep_min, sleep_max)
        logging.info('Sleeping for %f seconds', sleep_seconds)
        time.sleep(sleep_seconds)
        _find_and_click(templates)


def _find_and_click(templates: dict[str, np.ndarray]) -> None:
    screenshot_image = pyautogui.screenshot()
    screenshot = _image_to_grayscale_array(screenshot_image)
    for name, template in templates.items():
        sift = cv.SIFT_create()  # pylint: disable=no-member
        _, template_descriptors = sift.detectAndCompute(template, mask=None)
        screenshot_keypoints, screenshot_descriptors = sift.detectAndCompute(screenshot, mask=None)
        matcher = cv.BFMatcher()  # pylint: disable=no-member
        matches = matcher.knnMatch(template_descriptors, screenshot_descriptors, k=2)
        points = np.array([screenshot_keypoints[m.trainIdx].pt for m, n in matches if m.distance < 0.5 * n.distance])
        if points.shape[0] == 0:
            continue
        point = np.median(points, axis=0)
        pyautogui.click(*point)
        logging.info('Clicking on %s at coordinates x=%f y=%f', name, *point)
        break
    logging.info('No matches found')


def _get_templates() -> dict[str, np.ndarray]:
    arrays = {}
    try:
        # pylint: disable=no-member,protected-access
        root_dir = sys._MEIPASS  # type: ignore
    except NameError:
        root_dir = '.'
    templates_dir = os.path.join(root_dir, 'templates')
    basenames = os.listdir(templates_dir)
    for basename in basenames:
        name, _ = os.path.splitext(basename)
        path = os.path.join(templates_dir, basename)
        image = PIL.Image.open(path)  # pylint: disable=no-member
        array = _image_to_grayscale_array(image)
        arrays[name] = array
    return arrays


def _image_to_grayscale_array(image: PIL.Image.Image) -> np.ndarray:
    image = PIL.ImageOps.grayscale(image)
    array = np.array(image)
    return array


if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
