import pathlib
import urllib.request
from contextlib import contextmanager
from io import BytesIO
from os import PathLike
from shutil import copyfileobj
from typing import Union

FileLike = Union[str, PathLike, BytesIO]


@contextmanager
def filelike_open(source: FileLike, mode):
    if isinstance(source, (str, PathLike)):
        with open(source, mode) as f:
            yield f
    else:
        return source


def copy_file_obj(source: FileLike, target: FileLike) -> None:
    with filelike_open(source, 'rb') as fs, filelike_open(target, 'wb') as ft:
        copyfileobj(fs, ft)


def load_file(url: str, file: FileLike, force=False) -> None:
    if isinstance(file, (str, PathLike)) and pathlib.Path(file).exists() and not force:
        return
    with urllib.request.urlopen(url) as resp:
        copy_file_obj(resp, file)


def load_gdrive_file(file_id: str, file: FileLike, force=False) -> None:
    if isinstance(file, (str, PathLike)) and pathlib.Path(file).exists() and not force:
        return
    url = f'https://drive.google.com/uc?export=downlod&id={file_id}'
    with urllib.request.urlopen(url) as resp:
        cookie = resp.info()['Set-Cookie']
        if cookie and 'download_warning' in cookie:
            confirm = cookie[cookie.find(file_id) + len(file_id) + 1:cookie.find(';')]
            url = url + f"&confirm={confirm}"
            req = urllib.request.Request(url)
            req.add_header('cookie', cookie)
            with urllib.request.urlopen(req) as resp:
                copy_file_obj(resp, file)
        else:
            copy_file_obj(resp, file)
