import urllib.request, json
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
      "Accept": "application/json,*/*", "Referer": "https://www.nli.org.il/", "Origin": "https://www.nli.org.il"}
urls = [
 "https://iiif.nli.org.il/IIIFv21/DOCID/IE27540503/manifest",
 "https://iiif.nli.org.il/IIIFv21/IE27540503/manifest",
 "https://iiif.nli.org.il/IIIFv21/DOCID/PNX_MANUSCRIPTS990001050100205171-1/manifest",
 "https://iiif.nli.org.il/IIIFv21/DOCID/NNL_ALEPH990001050100205171/manifest",
 "https://www.nli.org.il/api/iiif/manifest/IE27540503",
 "https://rosetta.nli.org.il/delivery/DeliveryManagerServlet?dps_pid=IE27540503&dps_func=stream",
 "https://iiif.nli.org.il/IIIFv3/DOCID/IE27540503/manifest",
 "https://www.nli.org.il/en/manuscripts/NNL_ALEPH990001050100205171/NLI",
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        print("OK", r.status, len(data), u)
        if b"canvases" in data or b"\"items\"" in data:
            open("manifest_found.json", "wb").write(data); print("  saved manifest")
        elif b"<html" in data[:500].lower():
            s = data.decode("utf-8", "ignore")
            for key in ("FL2754", "manifest", "IE27540503"):
                i = s.find(key)
                if i >= 0: print("  html has", key, "at", i, s[max(0,i-80):i+120].replace("\n"," "))
    except Exception as e:
        print("FAIL", u, str(e)[:60])
