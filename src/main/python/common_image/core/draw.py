from typing import Tuple, Iterable

import cv2
import numpy as np

ituple = Tuple[int, int]


def draw_ellipse(ndarray: np.ndarray, p1: ituple, p2: ituple, color=255) -> None:
    ax = int(abs(p2[0] - p1[0]) / 2)
    ay = int(abs(p2[1] - p1[1]) / 2)
    cx = int(abs(p2[0] + p1[0]) / 2)
    cy = int(abs(p2[1] + p1[1]) / 2)
    cv2.ellipse(ndarray, (cx, cy), (ax, ay), 0, 0, 360, color, cv2.FILLED)


def draw_rect(ndarray: np.ndarray, p1: ituple, p2: ituple, color=255) -> None:
    cv2.rectangle(ndarray, p1, p2, color, cv2.FILLED)


def draw_polygon(ndarray: np.ndarray, points: Iterable[ituple], color: int = 255) -> None:
    points_ = np.array(points).reshape((1, -1, 2), order='C')
    cv2.fillPoly(ndarray, points_, color)


def draw_line(ndarray: np.ndarray, p1: ituple, p2: ituple, color: int = 255, thickness: int = 1) -> None:
    cv2.line(ndarray, p1, p2, color, thickness)