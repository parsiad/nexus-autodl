#!/usr/bin/env python

# pylint: disable=missing-module-docstring

from typing import List, NamedTuple
import os
import logging
import random
import re
import sys
import time

from numpy import ndarray as NDArray
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
        try:
            _find_and_click(templates)
        except cv.error:
            logging.info('Ignoring OpenCV error')
            pass


class _Template(NamedTuple):
    array: NDArray
    name: str
    threshold: int


def _find_and_click(templates: List[_Template]) -> None:
    screenshot_image = pyautogui.screenshot()
    screenshot = _image_to_grayscale_array(screenshot_image)
    for template in templates:
        sift = cv.SIFT_create()  # pylint: disable=no-member
        _, template_descriptors = sift.detectAndCompute(template.array, mask=None)
        screenshot_keypoints, screenshot_descriptors = sift.detectAndCompute(screenshot, mask=None)
        matcher = cv.BFMatcher()  # pylint: disable=no-member
        matches = matcher.knnMatch(template_descriptors, screenshot_descriptors, k=2)
        points = np.array([screenshot_keypoints[m.trainIdx].pt for m, _ in matches if m.distance < template.threshold])
        if points.shape[0] == 0:
            continue
        point = np.median(points, axis=0)
        pyautogui.click(*point)
        logging.info('Clicking on %s at coordinates x=%f y=%f', template.name, *point)
        return
    logging.info('No matches found')


def _get_templates() -> List[_Template]:
    templates = []
    try:
        # pylint: disable=no-member,protected-access
        root_dir = sys._MEIPASS  # type: ignore
    except AttributeError:
        root_dir = '.'
    templates_dir = os.path.join(root_dir, 'templates')
    pattern = re.compile(r'^([1-9][0-9]*)_([1-9][0-9]*)_(.+)\.png$')
    basenames = os.listdir(templates_dir)
    matches = (pattern.match(basename) for basename in basenames)
    filtered_matches = (match for match in matches if match is not None)
    groups = (match.groups() for match in filtered_matches)
    sorted_groups = sorted(groups, key=lambda t: int(t[0]))
    for index, threshold, name in sorted_groups:
        path = os.path.join(templates_dir, f'{index}_{threshold}_{name}.png')
        image = PIL.Image.open(path)  # pylint: disable=no-member
        array = _image_to_grayscale_array(image)
        template = _Template(array=array, name=name, threshold=int(threshold))
        templates.append(template)
    return templates


def _image_to_grayscale_array(image: PIL.Image.Image) -> NDArray:
    image = PIL.ImageOps.grayscale(image)
    array = np.array(image)
    return array


if __name__ == '__main__':
    run()  # pylint: disable=no-value-for-parameter
