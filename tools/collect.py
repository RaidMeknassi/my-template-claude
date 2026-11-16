"""Downloads the Futurepedia style atlases (prompts + metadata) into data/*.json."""
import json, os, sys, time, urllib.request
from datetime import datetime, timezone

BASE = "https://www.futurepedia.io"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "application/json,text/html,*/*"}
THREE_D = ["low-poly","paper-pop-up","soft-clay","tiny-diorama","blueprint-build","spotlight-stage","neon-sign",
 "exploded-view","marble-run","x-ray","led-wall","inflated","painted","circuit-city","glass-light","factory-line",
 "white-model","voxel","data-skyline","ink-toon","pin-wall","toy-blocks","particle-swarm","museum-gallery",
 "pencil-sketch","domino-chain","node-network","shadow-box","layer-stack","dithered","floating-screens",
 "device-hero","studio-product","split-flap","hero-icon","embossed","monument-type"]

def get(url, tries=4):
    err = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    raise err

def prompt_data(atlas, sid):
    return json.loads(json.loads(get(f"{BASE}/api/resources/{atlas}/styles/{sid}/prompt-data"))["data"])

def save(name, obj):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{name}", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("saved", name, os.path.getsize(f"data/{name}"), "bytes")

now = datetime.now(timezone.utc).isoformat()
failed = []

# ---- Atlas 1: 3D Style Atlas
styles = []
for sid in THREE_D:
    try:
        styles.append(prompt_data("3d-style-atlas", sid))
    except Exception as e:
        failed.append(("3d-style-atlas", sid, str(e)))
save("3d-style-atlas.json", {"source": f"{BASE}/resources/3d-style-atlas/view", "fetched": now, "styles": styles})

# ---- Atlas 2: AI Style Atlas
lst, page = [], 1
while True:
    d = json.loads(get(f"{BASE}/api/resources/ai-style-atlas/styles?category=All&page={page}"))
    lst += d["styles"]
    if not d.get("hasMore"):
        break
    page += 1
details = {}
for s in lst:
    try:
        details[s["styleId"]] = prompt_data("ai-style-atlas", s["styleId"])
    except Exception as e:
        failed.append(("ai-style-atlas", s["styleId"], str(e)))
save("ai-style-atlas.json", {"source": f"{BASE}/resources/ai-style-atlas/view", "fetched": now, "list": lst, "styles": details})
try:
    save("ai-prompt-builder.json", json.loads(get(f"{BASE}/api/resources/ai-style-atlas/prompt-builder")))
except Exception as e:
    failed.append(("ai-style-atlas", "prompt-builder", str(e)))

print(f"3D: {len(styles)}/{len(THREE_D)}  AI: {len(details)}/{len(lst)}  failed: {len(failed)}")
for f in failed:
    print("FAILED", f)
if not styles and not details:
    sys.exit(1)
