import pathlib
import urllib.request
from io import BytesIO
from shutil import copyfileobj
from typing import Union


def copy_file_obj(source: BytesIO, target: Union[str, BytesIO]) -> None:
    if isinstance(target, str):
        with open(target, 'wb') as f:
            copyfileobj(source, f)
    elif isinstance(target, BytesIO):
        copyfileobj(source, target)


def load_gdrive_file(file_id: str, file: Union[str, BytesIO], force=False) -> None:
    if isinstance(file, str) and pathlib.Path(file).exists() and not force:
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


