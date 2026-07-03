#!/usr/bin/env python3
"""Live tail of doomscrollstats.com usage — one line per person using the site, right now.

Privacy-safe: each event carries only an 8-char visitor hash (sha256 of a salted IP,
truncated) so you can tell people apart in the stream without ever storing personal data.

Usage:
    python3 watch-live.py

Ctrl-C to stop. Requires AWS creds with CloudWatch Logs read on /aws/lambda/doomscroll-nova.
"""
import subprocess, json

CMD = ["aws", "logs", "tail", "/aws/lambda/doomscroll-nova", "--follow",
       "--filter-pattern", "USE", "--format", "short", "--region", "us-east-1"]
PLAT = {"x": "X", "instagram": "Instagram", "tiktok": "TikTok", "youtube": "YouTube",
        "reddit": "Reddit", "linkedin": "LinkedIn", "facebook": "Facebook"}

print("👀 watching doomscrollstats.com — live. Ctrl-C to stop.\n")
p = subprocess.Popen(CMD, stdout=subprocess.PIPE, text=True)
try:
    for line in p.stdout:
        i = line.find("USE {")
        if i < 0:
            continue
        try:
            d = json.loads(line[i + 4:])
        except Exception:
            continue
        u = d.get("u", "?")
        if d.get("evt") == "analyze":
            mode = "📸 vision" if d.get("mode") == "vision" else "📝 text  "
            plat = PLAT.get(d.get("plat"), str(d.get("plat", "?")))
            print(f"🔮 {plat:10} read  {mode}  ·  {d.get('posts', 0)} posts  ·  {d.get('ai', '?')}% AI-slop   [{u}]")
        elif d.get("evt") == "score":
            print(f"📊 score {str(d.get('score')):>3}   ·  more bubbled than {str(d.get('pct')):>2}% of {d.get('n')} feeds   [{u}]")
except KeyboardInterrupt:
    p.terminate()
    print("\n👋 stopped.")
