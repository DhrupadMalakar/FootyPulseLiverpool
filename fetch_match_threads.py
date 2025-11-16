# ---------------- SECTION 1: Reddit Credentials + Basic Settings ----------------

CLIENT_ID = "b2BTHQm-DysnD_-6nlH87Q"
CLIENT_SECRET = "Dz4lNysLQ8N5Pu1WRCzkPZaw7YFuzw"
USERNAME = "wintersoldier0587"
PASSWORD = "Hiramala1993!"
USER_AGENT = "FootyPulseMatchFetcher/0.1 (by wintersoldier0587)"

SUBREDDIT = "LiverpoolFC"
SCAN_LIMIT = 200
TARGET_COMMENTS = 1000
OUTFILE = "liverpool_match_comments.jl"

# ---------------- SECTION 2: Detecting Match / Post-Match Threads ----------------

MATCH_KEYWORDS = [
    "match thread", "post match", "post-match", "pre match", "pre-match",
    "matchthread", "match day", "matchday", "postmatch", "full-time",
    "ft", "post match thread"
]

def looks_like_match_thread(submission):
    title = (submission.title or "").lower()
    flair = (submission.link_flair_text or "").lower() if getattr(submission, "link_flair_text", None) else ""
    
    # Check flair first
    if any(k in flair for k in MATCH_KEYWORDS):
        return True

    # Check title
    if any(k in title for k in MATCH_KEYWORDS):
        return True

    # Extra safe check
    if title.strip().startswith("[match"):
        return True

    return False
# ---------------- SECTION 3: Connect to Reddit + Find Match Threads ----------------

import praw
import time
import json
from tqdm import tqdm

def init_reddit():
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        user_agent=USER_AGENT,
        check_for_async=False
    )

def find_candidate_threads(reddit, limit=SCAN_LIMIT):
    subreddit = reddit.subreddit(SUBREDDIT)
    candidates = []

    print(f"Scanning newest {limit} posts in r/{SUBREDDIT}...")

    for submission in subreddit.new(limit=limit):
        try:
            if looks_like_match_thread(submission):
                candidates.append({
                    "id": submission.id,
                    "title": submission.title,
                    "created_utc": int(submission.created_utc),
                    "num_comments": submission.num_comments,
                    "flair": submission.link_flair_text
                })
        except Exception:
            continue

    candidates = sorted(candidates, key=lambda x: x["created_utc"], reverse=True)
    print(f"Found {len(candidates)} candidate match threads.")
    return candidates

# ---------------- SECTION 4: Fetch Comments for a Thread ----------------

def fetch_comments_from_submission(reddit, post_id):
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=None)

    comments = []

    for c in submission.comments.list():
        comments.append({
            "id": c.id,
            "body": c.body,
            "author": str(c.author) if c.author else None,
            "created_utc": int(c.created_utc),
            "score": c.score,
            "parent_id": c.parent_id,
            "link_id": c.link_id,
            "submission_id": post_id
        })

    return comments

# ---------------- SECTION 5: Main Runner ----------------

def main():
    reddit = init_reddit()
    candidates = find_candidate_threads(reddit, limit=SCAN_LIMIT)

    collected = 0
    seen = set()

    print(f"\nTarget: {TARGET_COMMENTS} comments")
    print("Starting collection...\n")

    with open(OUTFILE, "w", encoding="utf-8") as f:
        for thread in candidates:
            if collected >= TARGET_COMMENTS:
                break

            print(f"\nFetching from: {thread['title']}  (ID: {thread['id']})")

            try:
                comments = fetch_comments_from_submission(reddit, thread["id"])
            except Exception as e:
                print("Error fetching comments:", e)
                time.sleep(2)
                continue

            for c in comments:
                if c["id"] in seen:
                    continue
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
                seen.add(c["id"])
                collected += 1

                if collected >= TARGET_COMMENTS:
                    break

            print(f"Collected so far: {collected}")

            time.sleep(2)  # polite pause

    print(f"\nDone! Total collected: {collected}")
    print(f"Saved to: {OUTFILE}")


if __name__ == "__main__":
    main()

