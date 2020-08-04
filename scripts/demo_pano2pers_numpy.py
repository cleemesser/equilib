#!/usr/bin/env python3

from typing import Union

import argparse
import os.path as osp
import time

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from panolib.pano2pers import NumpyPano2Pers

matplotlib.use('Agg')


def preprocess(
    img: Union[np.ndarray, Image.Image],
    is_cv2: bool = False,
) -> np.ndarray:
    r"""Preprocesses image
    """
    if isinstance(img, np.ndarray) and is_cv2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if isinstance(img, Image.Image):
        # Sometimes images are RGBA
        img = img.convert('RGB')
        img = np.asarray(img)
    assert len(img.shape) == 3, "input must be dim=3"
    assert img.shape[-1] == 3, "input must be HWC"
    img = np.transpose(img, (2, 0, 1))
    return img


def test_video(
    path: str,
    h_pers: int = 480,
    w_pers: int = 640,
    fov_x: float = 90.,
) -> None:
    r"""Test video
    """
    # Rotation:
    pi = np.pi
    inc = pi / 180
    roll = 0  # -pi/2 < a < pi/2
    pitch = 0  # -pi < b < pi
    yaw = 0

    # Initialize pano2pers
    pano2pers = NumpyPano2Pers(
        w_pers=w_pers,
        h_pers=h_pers,
        fov_x=fov_x
    )

    times = []
    cap = cv2.VideoCapture(path)

    while(cap.isOpened()):
        ret, frame = cap.read()

        rot = {
            'roll': roll,
            'pitch': pitch,
            'yaw': yaw,
        }

        if not ret:
            break

        s = time.time()
        pano_img = preprocess(frame, is_cv2=True)
        pers_img = pano2pers(
            pano=pano_img,
            rot=rot,
            sampling_method="faster",
            mode="bilinear",
        )
        pers_img = np.transpose(pers_img, (1, 2, 0))
        pers_img = cv2.cvtColor(pers_img, cv2.COLOR_RGB2BGR)
        e = time.time()
        times.append(e - s)

        # cv2.imshow("video", pers)

        # change direction `wsad` or exit with `q`
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
        if k == ord('w'):
            roll -= inc
        if k == ord('s'):
            roll += inc
        if k == ord('a'):
            pitch += inc
        if k == ord('d'):
            pitch -= inc

    cap.release()
    cv2.destroyAllWindows()

    print(sum(times)/len(times))
    x_axis = [i for i in range(len(times))]
    plt.plot(x_axis, times)
    save_path = osp.join('./results', 'times_pano2pers_numpy_video.png')
    plt.savefig(save_path)


def test_image(
    path: str,
    h_pers: int = 480,
    w_pers: int = 640,
    fov_x: float = 90.,
) -> None:
    r"""Test single image
    """
    # Rotation:
    rot = {
        'roll': 0,
        'pitch': 0,
        'yaw': 0,
    }

    # Initialize pano2pers
    pano2pers = NumpyPano2Pers(
        w_pers=w_pers,
        h_pers=h_pers,
        fov_x=fov_x
    )

    # Open Image
    pano_img = Image.open(path)
    pano_img = preprocess(pano_img)

    pers_img = pano2pers(
        pano_img,
        rot=rot,
        sampling_method="faster",
        mode="bilinear",
    )

    pers_img = np.transpose(pers_img, (1, 2, 0))
    pers_img = Image.fromarray(pers_img)

    pers_path = osp.join('./results', 'output_pano2pers_numpy_image.jpg')
    pers_img.save(pers_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', action='store_true')
    parser.add_argument('--data', nargs='?', default=None, type=str)
    args = parser.parse_args()

    # Variables:
    h_pers = 480
    w_pers = 640
    fov_x = 90

    data_path = args.data
    if args.video:
        if data_path is None:
            data_path = "./data/R0010028_er_30.MP4"
        assert osp.exists(data_path)
        test_video(data_path, h_pers, w_pers, fov_x)
    else:
        if data_path is None:
            data_path = "./data/pano.jpg"
        assert osp.exists(data_path)
        test_image(data_path, h_pers, w_pers, fov_x)


if __name__ == "__main__":
    main()
