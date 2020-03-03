import pathlib
import urllib.request
from shutil import copyfileobj


def load_gdrive_file(file_id: str, file_path: str, force=False) -> None:
    if pathlib.Path(file_path).exists() and not force:
        return
    url = f'https://drive.google.com/uc?export=downlod&id={file_id}'
    with urllib.request.urlopen(url) as resp, open(file_path, 'wb') as f:
        cookie = resp.info()['Set-Cookie']
        if cookie and 'download_warning' in cookie:
            confirm = cookie[cookie.find(file_id) + len(file_id) + 1:cookie.find(';')]
            url = url + f"&confirm={confirm}"
            req = urllib.request.Request(url)
            req.add_header('cookie', cookie)
            with urllib.request.urlopen(req) as resp:
                copyfileobj(resp, f)
        else:
            copyfileobj(resp, f)
