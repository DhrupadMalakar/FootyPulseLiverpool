#!/usr/bin/env python3
# matchday.py

import subprocess

print("\n=== FOOTYPULSE: LIVERPOOL MATCHDAY PIPELINE ===\n")

def run(cmd):
    print(f"\n--- Running: {cmd} ---")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"ERROR running: {cmd}")
        exit(1)

# 1. Fetch match/post-match comments
run("python fetch_match_threads.py")

# 2. Analyze comments + generate final_fan_report.txt
run("python analyze_comments.py")

# 3. Generate wordclouds
run("python make_wordclouds.py")

# 4. Generate PDF report
run("python make_pdf_report.py")

print("\n🎉 DONE! Matchday report created successfully:\n")
print(" - final_fan_report.txt")
print(" - liverpool_player_wordcloud.png")
print(" - opponent_player_wordcloud.png")
print(" - liverpool_fan_report.pdf\n")
print("You can open the PDF with:\n   open liverpool_fan_report.pdf\n")
