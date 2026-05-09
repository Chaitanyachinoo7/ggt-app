import os

import requests


def _modal_app_name():
    return os.getenv("MODAL_APP_NAME") or "ggt-compute"


def _modal_web_base_url():
    return os.getenv("MODAL_WEB_BASE_URL") or ""


def modal_remote(function_name, *args, **kwargs):
    import modal

    fn = modal.Function.lookup(_modal_app_name(), function_name)
    return fn.remote(*args, **kwargs)


def modal_web_post(path, payload=None):
    base = _modal_web_base_url().rstrip("/")
    if not base:
        raise RuntimeError("MODAL_WEB_BASE_URL is not set")
    url = f"{base}{path}"
    r = requests.post(url, json=payload or {}, timeout=60 * 60)
    r.raise_for_status()
    return r.json()


def modal_web_get(path):
    base = _modal_web_base_url().rstrip("/")
    if not base:
        raise RuntimeError("MODAL_WEB_BASE_URL is not set")
    url = f"{base}{path}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.json()
