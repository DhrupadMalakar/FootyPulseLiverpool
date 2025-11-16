# ---------------- SECTION 1: Load and Clean Data ----------------

import pandas as pd
import json

INPUT_FILE = "liverpool_match_comments.jl"

def load_comments():
    rows = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                rows.append(obj)
            except:
                continue

    df = pd.DataFrame(rows)

    # Basic cleaning
    df = df.dropna(subset=["body"])           # remove rows with no body
    df = df[df["body"].str.strip() != ""]     # remove blank comments
    df = df[~df["body"].str.contains("deleted", case=False, na=False)]
    df = df[~df["body"].str.contains("removed", case=False, na=False)]

    df.reset_index(drop=True, inplace=True)
    return df

if __name__ == "__main__":
    df = load_comments()
    print("Loaded comments:", len(df))
    print("\nSample comments:")
    print(df["body"].head(10))

# ---------------- SECTION 2: Basic Keyword + Theme Extraction ----------------

# ---------------- SECTION 2: Player Extraction with Nickname Mapping ----------------

import re
from collections import Counter

PLAYER_MAP = {
    # Goalkeepers
    "alisson becker": ["alisson", "alli", "ali", "alisson becker"],
    "giorgi mamardashvili": ["mamardashvili", "giorgi", "mama", "marmadashvili"],
    "freddie woodman": ["woodman", "freddie", "freddy"],
    "armin pecsi": ["pecsi", "armin pecsi"],

    # Defenders
    "joe gomez": ["gomez", "joego", "jg"],
    "virgil van dijk": ["virgil", "vvd", "van dijk", "virgil vd"],
    "ibrahima konate": ["konate", "ibou", "ibrahima"],
    "milos kerkez": ["kerkez", "milos"],
    "conor bradley": ["bradley", "conor"],
    "giovanni leoni": ["leoni", "gio"],
    "andy robertson": ["robertson", "robbo", "andy robbo"],
    "jeremie frimpong": ["frimpong", "jero", "jeremie"],

    # Midfielders
    "wataru endo": ["endo", "wataru", "wato"],
    "florian wirtz": ["wirtz", "flo", "florian"],
    "alexis mac allister": ["mac allister", "macca", "macca10", "alexis", "mac"],
    "curtis jones": ["curtis", "jones", "curtii"],
    "ryan gravenberch": ["gravenberch", "ryan", "gravy", "grav"],

    # Forwards
    "alexander isak": ["isak", "isaac", "alexander"],
    "mohamed salah": ["salah", "mo", "mosalah", "king mo", "egyptian king"],
    "cody gakpo": ["gakpo", "cody", "gako", "gaks"],
    "hugo ekitike": ["ekitike", "hugo", "ekki"],
    "rio ngumoha": ["rio", "ngumoha", "rio n"]
}

# Flatten nickname map for fast lookup
NICKNAME_LOOKUP = {}
for player, nicknames in PLAYER_MAP.items():
    for n in nicknames:
        NICKNAME_LOOKUP[n.lower()] = player

def extract_player_mentions(df):
    counter = Counter()
    for text in df["body"]:
        lower = text.lower()
        for nickname, canonical in NICKNAME_LOOKUP.items():
            if nickname in lower:
                counter[canonical] += 1
    return counter.most_common()

# ---------------- SECTION 2B: Keyword Extraction (restored) ----------------

import re
from collections import Counter

def extract_top_keywords(df, top_n=20):
    words = []
    for text in df["body"]:
        tokens = re.findall(r"[a-zA-Z]+", text.lower())
        words.extend(tokens)

    common = Counter(words)

    # remove boring words
    stopwords = {
        "the", "and", "with", "this", "have", "they", "that", "were",
        "from", "just", "what", "when", "your", "their", "them",
        "then", "than", "into", "there", "here", "were", "like",
        "been", "it's", "its", "for", "into", "over", "will", "should",
        "would", "could", "into", "after", "before", "even", "some"
    }

    filtered = [(w, c) for w, c in common.items() if w not in stopwords and len(w) > 3]
    filtered = sorted(filtered, key=lambda x: x[1], reverse=True)

    return filtered[:top_n]


# ---------------- SECTION 3: Embeddings + Clustering ----------------

from openai import OpenAI
import numpy as np
from sklearn.cluster import KMeans

client = OpenAI()

EMBED_MODEL = "text-embedding-3-small"     # cheap and good
N_CLUSTERS = 12                            # balanced mode: ~12 themes

def compute_embeddings(texts):
    # break into chunks if needed
    batch_size = 100
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=batch
        )
        vectors.extend([d.embedding for d in response.data])
    return np.array(vectors)

def cluster_comments(df):
    texts = df["body"].tolist()
    print("Computing embeddings for", len(texts), "comments...")
    emb = compute_embeddings(texts)

    print("Clustering into", N_CLUSTERS, "groups...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42)
    labels = kmeans.fit_predict(emb)

    df["cluster"] = labels
    return df, kmeans.cluster_centers_

# ---------------- SECTION 4: GPT Summaries for Each Cluster ----------------

# ---------------- SECTION 4: GPT Summaries for Each Cluster ----------------

def summarize_cluster(comments):
    prompt = f"""
You are analyzing Liverpool FC fan reactions from real Reddit comments.

Important rules:
- Only the following players are Liverpool FC players:
  Alisson Becker, Giorgi Mamardashvili, Freddie Woodman, Armin Pecsi,
  Joe Gomez, Virgil van Dijk, Ibrahima Konate, Milos Kerkez, Conor Bradley,
  Giovanni Leoni, Andy Robertson, Jeremie Frimpong,
  Wataru Endo, Florian Wirtz, Alexis Mac Allister, Curtis Jones,
  Ryan Gravenberch, Alexander Isak, Mohamed Salah, Cody Gakpo,
  Hugo Ekitike, Rio Ngumoha.
- ANY OTHER PLAYER mentioned in the comments (e.g., Doku, Haaland, Rodri,
  Foden, Trent, Jota, etc.) is NOT a Liverpool player. Treat them as
  opponents or external players.
- NEVER misclassify a non-Liverpool player as a Liverpool player.
- If fans talk about non-Liverpool players, summarize them correctly
  as opponents or external references.
- Maintain strict separation between Liverpool player analysis and opponent analysis.

Now analyze these comments:

{comments}

Write:
- Emotional mood in 2 lines
- Main complaints in 2–3 bullets
- Main praise in 2–3 bullets
- Player-related themes (Liverpool players vs opponent players)
- Tactical/structural themes
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()


def summarize_full_fanbase(cluster_summaries):
    prompt = f"""
You are analyzing the overall Liverpool FC fanbase mood based on summaries from {len(cluster_summaries)} clusters.

Important rules:
- Only the following players are Liverpool FC players:
  Alisson Becker, Giorgi Mamardashvili, Freddie Woodman, Armin Pecsi,
  Joe Gomez, Virgil van Dijk, Ibrahima Konate, Milos Kerkez, Conor Bradley,
  Giovanni Leoni, Andy Robertson, Jeremie Frimpong,
  Wataru Endo, Florian Wirtz, Alexis Mac Allister, Curtis Jones,
  Ryan Gravenberch, Alexander Isak, Mohamed Salah, Cody Gakpo,
  Hugo Ekitike, Rio Ngumoha.
- ANY OTHER PLAYER mentioned is NOT a Liverpool player. Treat names like:
  Doku, Haaland, Rodri, Foden, Akanji, Stones, Trent (Madrid), Modric, Jota, etc.
  as opponents or external players.
- NEVER misclassify non-Liverpool players as Liverpool players.
- Maintain absolute separation between Liverpool-related analysis
  and opponent-related analysis.
- If fans praise or criticise non-Liverpool players, summarize that
  as opponent-related discussion.

Cluster summaries:
{cluster_summaries}

Write a final report including:

1. Overall emotional mood (3–4 lines)
2. What fans are angry or worried about (3–5 bullets)
3. What fans still support or appreciate (2–4 bullets)
4. Tactical or structural patterns they keep mentioning
5. Liverpool players fans discussed the most
6. Opponent players fans mentioned and why
7. One concluding sentence summarizing the fanbase mood
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=650
    )
    return response.choices[0].message.content.strip()


# ---------------- SECTION 5: Execute Balanced Analysis ----------------

if __name__ == "__main__":
    df = load_comments()

    # Extract basic stats
    print("\n=== PLAYER MENTIONS ===")
    players = extract_player_mentions(df)
    for p, c in players:
        print(f"{p}: {c}")

    print("\n=== TOP KEYWORDS ===")
    for w, c in extract_top_keywords(df):
        print(f"{w}: {c}")

    print("\n=== BUILDING CLUSTERS ===")
    df, centers = cluster_comments(df)

    cluster_summaries = []

    print("\n=== SUMMARIZING EACH CLUSTER ===")
    for cl in range(N_CLUSTERS):
        group = df[df["cluster"] == cl]["body"].tolist()
        sample = group[:12] if len(group) > 12 else group
        text_block = "\n".join(sample)

        print(f"\nCluster {cl}: summarizing {len(sample)} samples")
        summary = summarize_cluster(text_block)
        print(summary)
        cluster_summaries.append(summary)

    print("\n=== FINAL LIVERPOOL FANBASE REPORT ===")
    final_report = summarize_full_fanbase(cluster_summaries)
    print("\n" + final_report + "\n")

    # --- Save final report for PDF generation ---
    try:
        with open("final_fan_report.txt", "w", encoding="utf-8") as f:
            f.write(final_report)
        print("Saved: final_fan_report.txt")
    except Exception as e:
        print("Error saving final_fan_report.txt:", e)


# --- Save final report for PDF generation ---
try:
    with open("final_fan_report.txt", "w", encoding="utf-8") as f:
        f.write(final_report)
    print("Saved: final_fan_report.txt")
except Exception as e:
    print("Error saving final_fan_report.txt:", e)


