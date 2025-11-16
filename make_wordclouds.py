#!/usr/bin/env python3
# make_wordclouds.py
# Run in the same folder as liverpool_match_comments.jl

import json
import re
import random
from collections import Counter
import math
import matplotlib.pyplot as plt

INPUT_FILE = "liverpool_match_comments.jl"

# --- Your canonical Liverpool player map (lowercased canonical keys) ---
PLAYER_MAP = {
    "alisson becker": ["alisson", "alli", "ali", "alisson becker"],
    "giorgi mamardashvili": ["mamardashvili", "giorgi", "mama", "marmadashvili"],
    "freddie woodman": ["woodman", "freddie", "freddy"],
    "armin pecsi": ["pecsi", "armin pecsi"],
    "joe gomez": ["gomez", "joego", "jg"],
    "virgil van dijk": ["virgil", "vvd", "van dijk", "virgil vd"],
    "ibrahima konate": ["konate", "ibou", "ibrahima", "konaté"],
    "milos kerkez": ["kerkez", "milos"],
    "conor bradley": ["bradley", "conor"],
    "giovanni leoni": ["leoni", "gio"],
    "andy robertson": ["robertson", "robbo", "andy robbo"],
    "jeremie frimpong": ["frimpong", "jero", "jeremie"],
    "wataru endo": ["endo", "wataru", "wato", "endō"],
    "florian wirtz": ["wirtz", "flo", "florian"],
    "alexis mac allister": ["mac allister", "macca", "macca10", "alexis", "mac"],
    "curtis jones": ["curtis", "jones", "curtii"],
    "ryan gravenberch": ["gravenberch", "ryan", "gravy", "grav"],
    "alexander isak": ["isak", "isaac", "alexander"],
    "mohamed salah": ["salah", "mo", "mosalah", "king mo", "egyptian king"],
    "cody gakpo": ["gakpo", "cody", "gako", "gaks"],
    "hugo ekitike": ["ekitike", "hugo", "ekki"],
    "rio ngumoha": ["rio", "ngumoha", "rio n"]
}

# Build nickname lookup
NICKNAME_LOOKUP = {}
for canon, nicks in PLAYER_MAP.items():
    for n in nicks:
        NICKNAME_LOOKUP[n.lower()] = canon

# --- Helper: load comments ---
def load_comments(path=INPUT_FILE):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return [r.get("body", "") for r in rows]

# --- Count Liverpool player mentions using nickname lookup ---
def count_liverpool_mentions(comments):
    c = Counter()
    for text in comments:
        t = text.lower()
        for nick, canon in NICKNAME_LOOKUP.items():
            if nick in t:
                c[canon] += t.count(nick)
    return c

# --- Heuristic opponent name extraction (capitalized names) ---
def extract_opponent_name_mentions(comments, liverpool_canonicals):
    # regex: 1-3 capitalized words  (e.g., "Erling Haaland", "Phil Foden", "Doku")
    pattern = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2})\b")
    c = Counter()
    stopwords = set([
        "The","I","We","You","He","She","It","They","This","That","There",
        "Here","But","And","For","With","From","About","After","Before","Which"
    ])
    lfc_lower = {k.lower() for k in liverpool_canonicals}
    for text in comments:
        for match in pattern.findall(text):
            # skip common words and likely false positives
            if match in stopwords:
                continue
            key = match.strip()
            # skip if the name matches a Liverpool canonical (case-insensitive)
            if key.lower() in lfc_lower:
                continue
            # small filter: require at least 3 letters in first word
            first = key.split()[0]
            if len(first) < 3:
                continue
            # count
            c[key] += 1
    return c

# --- Simple text "word-cloud" scatter plot using matplotlib ---
def draw_text_cloud(counts, outpath, title):
    # counts: iterable of (word, count)
    items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:80]  # top 80
    if not items:
        print("No items to plot for", title)
        return
    # normalize sizes
    max_count = items[0][1]
    sizes = [max(8, 120 * (c / max_count)) for _, c in items]  # text sizes (pt)
    plt.figure(figsize=(12,8))
    plt.title(title, fontsize=16)
    occupied = []
    for (word, cnt), size in zip(items, sizes):
        # random placement with collision avoidance loop
        for _ in range(200):
            x = random.uniform(0, 1)
            y = random.uniform(0, 1)
            # naive collision checking
            ok = True
            for ox, oy, os in occupied:
                if (abs(x-ox) < 0.06*math.log(os+10)) and (abs(y-oy) < 0.06*math.log(os+10)):
                    ok = False
                    break
            if ok:
                occupied.append((x,y,size))
                plt.text(x, y, word, fontsize=size, ha='center', va='center', transform=plt.gca().transAxes)
                break
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(outpath, dpi=200)
    plt.close()
    print("Saved:", outpath)

def main():
    comments = load_comments(INPUT_FILE)
    print("Loaded", len(comments), "comments")

    lfc_counts = count_liverpool_mentions(comments)
    print("Top Liverpool mentions:", lfc_counts.most_common(10))

    opponent_counts = extract_opponent_name_mentions(comments, list(PLAYER_MAP.keys()))
    print("Top opponent mentions (sample):", opponent_counts.most_common(10))

    draw_text_cloud(dict(lfc_counts), "liverpool_player_wordcloud.png", "Liverpool player mentions")
    draw_text_cloud(dict(opponent_counts), "opponent_player_wordcloud.png", "Opponent player/manager mentions")

if __name__ == "__main__":
    main()
