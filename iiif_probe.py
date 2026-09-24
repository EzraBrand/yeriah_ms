import json, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-scraper/0.1",
      "Referer": "https://www.nli.org.il/"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

# 1. manifest
for url in ["https://iiif.nli.org.il/IIIFv21/DOCID/IE27540503/manifest",
            "https://iiif.nli.org.il/IIIFv21/DOCID/IE27540503/manifest.json"]:
    try:
        data = get(url)
        m = json.loads(data)
        open("manifest_IE27540503.json", "wb").write(data)
        canvases = m["sequences"][0]["canvases"]
        print("manifest ok, canvases:", len(canvases))
        with open("canvases.tsv", "w", encoding="utf-8") as f:
            for i, c in enumerate(canvases):
                svc = c["images"][0]["resource"]["service"]["@id"]
                f.write(f"{i}\t{c.get('label','')}\t{svc}\t{c.get('width')}x{c.get('height')}\n")
        for i, c in enumerate(canvases[145:160], 145):
            print(i, c.get("label"), c["images"][0]["resource"]["service"]["@id"], c.get("width"), c.get("height"))
        break
    except Exception as e:
        print("manifest fail", url, e)

# 2. info.json for 76b
try:
    info = json.loads(get("https://iiif.nli.org.il/IIIFv21/FL27544706/info.json"))
    print("info", info["width"], info["height"], info.get("profile"))
except Exception as e:
    print("info fail", e)
