from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request


HOST = "https://cn.bing.com/Translator"


def main() -> None:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    headers = {"User-Agent": "Mozilla/5.0", "Referer": HOST}
    html = opener.open(urllib.request.Request(HOST, headers=headers), timeout=30).read().decode("utf-8", "ignore")
    print("html", len(html))
    token_match = re.search(r"var params_AbusePreventionHelper = (.*?);", html)
    ig_match = re.search(r'IG:"(.*?)"', html)
    iid_match = re.search(r'data-iid="(translator\.[0-9]+)"', html)
    print("token", bool(token_match), "ig", bool(ig_match), "iid", bool(iid_match))
    if not (token_match and ig_match and iid_match):
        return
    params = json.loads(token_match.group(1))
    payload = {
        "text": "World models learn representations of an environment for planning and control.",
        "fromLang": "en",
        "to": "zh-Hans",
        "tryFetchingGenderDebiasedTranslations": "true",
        "key": params[0],
        "token": params[1],
    }
    url = f"https://cn.bing.com/ttranslatev3?isVertical=1&&IG={ig_match.group(1)}&IID={iid_match.group(1)}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": HOST,
            "Origin": "https://cn.bing.com",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    print(opener.open(req, timeout=30).read().decode("utf-8", "ignore")[:500])


if __name__ == "__main__":
    main()
