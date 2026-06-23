"""Shared constants + tiny wikitext helpers for the Ronaldo UCL project."""
import os, re, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "outputs")
for d in (RAW, PROC, OUT):
    os.makedirs(d, exist_ok=True)

# The three Real Madrid Champions League title campaigns ("La Decima" era three-peat).
# season label -> (openfootball folder, statsbomb season_id for comp 16, wikipedia season page, final match_id)
SEASONS = {
    "2015-16": dict(of="2015-16", sb_season=27, wiki="2015–16 Real Madrid CF season", final_mid=18243),
    "2016-17": dict(of="2016-17", sb_season=2,  wiki="2016–17 Real Madrid CF season", final_mid=18244),
    "2017-18": dict(of="2017-18", sb_season=1,  wiki="2017–18 Real Madrid CF season", final_mid=18245),
}
# Ronaldo's official Champions League goal tally per campaign (top scorer all three) — used as a correctness gate.
KNOWN_UCL_GOALS = {"2015-16": 16, "2016-17": 12, "2017-18": 15}

UA = {"User-Agent": "Mozilla/5.0 (compatible; ronaldo-ucl-portfolio/1.0)"}


def http_get(url, cache_name=None):
    """GET with optional on-disk cache under data/raw so re-runs are offline + fast."""
    if cache_name:
        path = os.path.join(RAW, cache_name)
        if os.path.exists(path):
            return open(path, encoding="utf-8").read()
    req = urllib.request.Request(url, headers=UA)
    txt = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    if cache_name:
        open(os.path.join(RAW, cache_name), "w", encoding="utf-8").write(txt)
    return txt


def wiki_raw(title, cache_name):
    url = f"https://en.wikipedia.org/w/index.php?title={urllib.parse.quote(title)}&action=raw"
    return http_get(url, cache_name)


def extract_templates(text, name):
    """Return all top-level {{name ...}} templates with balanced braces (case-insensitive).

    Positions are found on the ORIGINAL text (not a lowercased copy) because str.lower()
    can change length for some characters (e.g. Turkish 'İ', German 'ß'), which would
    desync indices and corrupt the slices.
    """
    out = []
    starts = [m.start() for m in re.finditer(re.escape("{{" + name), text, re.IGNORECASE)]
    for i in starts:
        depth, j = 0, i
        while j < len(text):
            if text[j:j + 2] == "{{":
                depth += 1; j += 2
            elif text[j:j + 2] == "}}":
                depth -= 1; j += 2
            else:
                j += 1
            if depth == 0:
                break
        out.append(text[i:j]); i = j
    return out


def split_params(t):
    """Split a {{template}} into a dict of named params, respecting nested {{}} and [[]]."""
    inner = t[2:-2]
    parts, depth, cur, k = [], 0, "", 0
    while k < len(inner):
        if inner[k:k + 2] in ("{{", "[["):
            depth += 1; cur += inner[k:k + 2]; k += 2
        elif inner[k:k + 2] in ("}}", "]]"):
            depth -= 1; cur += inner[k:k + 2]; k += 2
        elif inner[k] == "|" and depth == 0:
            parts.append(cur); cur = ""; k += 1
        else:
            cur += inner[k]; k += 1
    parts.append(cur)
    d = {}
    for p in parts[1:]:
        if "=" in p:
            key, _, val = p.partition("=")
            d[key.strip()] = val.strip()
    return d


def clean_name(s):
    """Turn '[[Borussia Dortmund|Dortmund]] {{flagicon|GER}}' into a plain comparable token."""
    s = re.sub(r"\{\{[^}]*\}\}", "", s)            # drop flagicons etc.
    s = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", s)  # [[A|B]] -> B
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def norm_token(s):
    """Lowercase alphanumeric key for fuzzy team matching across sources."""
    return re.sub(r"[^a-z0-9]", "", clean_name(s).lower())
