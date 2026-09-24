import json, sys, urllib.request, concurrent.futures as cf
UA = {"User-Agent": "Mozilla/5.0 research-scraper/0.1", "Referer": "https://www.nli.org.il/"}
def dims(n):
    fl = f"FL{n}"
    try:
        req = urllib.request.Request(f"https://iiif.nli.org.il/IIIFv21/{fl}/info.json", headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.loads(r.read())
        return n, j["width"], j["height"]
    except Exception as e:
        return n, None, str(e)[:40]
lo, hi = int(sys.argv[1]), int(sys.argv[2])
with cf.ThreadPoolExecutor(8) as ex:
    for n, w, h in sorted(ex.map(dims, range(lo, hi + 1))):
        print(n, w, h)
