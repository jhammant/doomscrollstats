"""doomscroll.stats — Nova analyzer (multi-platform, multimodal).
Text platforms (X, YouTube): OCR text -> Nova Micro.
Visual platforms (Instagram, TikTok): screenshots/frames -> Nova Lite (vision).
Returns scoring + a full narrative read. Bedrock via IAM (no key). boto3 ships in the runtime."""
import json, re, base64, time, hashlib, boto3

REGION = "us-east-1"
MODEL_TEXT = "amazon.nova-micro-v1:0"
MODEL_VISION = "amazon.nova-pro-v1:0"   # Pro reads visual feeds (Instagram/TikTok) far better than Lite
TOPICS = ["Politics", "Culture", "Economy", "World", "Local", "Sport", "Tech", "Life"]
EMOS = ["Anger", "Fear", "Contempt", "Outrage", "Tribal", "Curiosity", "Hope", "Humor"]
HEADERS = {"Content-Type": "application/json"}
ALLOWED_ORIGINS = {
    "https://doomscrollstats.com",
    "https://www.doomscrollstats.com",
    "http://doomscrollstats-site.s3-website-eu-west-1.amazonaws.com",
}
_bedrock = boto3.client("bedrock-runtime", region_name=REGION)
_ddb = boto3.client("dynamodb", region_name=REGION)
AGG_TABLE = "doomscroll-agg"

def _uh(ip):
    """Short, stable, non-reversible per-visitor token — lets a live tail tell users apart without storing any PII."""
    return hashlib.sha256(("ds" + (ip or "?")).encode()).hexdigest()[:8]

def _log(evt, **kw):
    """One greppable line per usage event, for `aws logs tail --filter-pattern USE`."""
    try:
        print("USE " + json.dumps({"evt": evt, **kw}, separators=(",", ":")))
    except Exception:
        pass

def _stats(score, ip=""):
    """Anonymous aggregate: bucket the balance score, return how bubbled vs everyone. Stores only a counter."""
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        return _resp(400, {"error": "bad score"})
    b = min(9, score // 10)
    try:
        _ddb.update_item(TableName=AGG_TABLE, Key={"id": {"S": "scores"}},
                         UpdateExpression="ADD #k :one",
                         ExpressionAttributeNames={"#k": "b" + str(b)},
                         ExpressionAttributeValues={":one": {"N": "1"}})
        item = _ddb.get_item(TableName=AGG_TABLE, Key={"id": {"S": "scores"}}).get("Item", {})
        counts = [int(item.get("b" + str(i), {}).get("N", "0")) for i in range(10)]
        total = sum(counts) or 1
        more_bubbled = round(sum(counts[b + 1:]) / total * 100)  # feeds more balanced than you -> you're more bubbled than them
        _log("score", score=score, pct=more_bubbled, n=total, u=_uh(ip))
        return _resp(200, {"moreBubbledThan": more_bubbled, "samples": total})
    except Exception as e:
        return _resp(200, {"moreBubbledThan": None, "samples": 0, "error": str(e)[:120]})

RL_LIMIT = 30  # backup bot protection: max requests per minute per IP
def _rate_ok(ip):
    if not ip:
        return True
    key = "rl#" + ip + "#" + str(int(time.time() // 60))
    try:
        r = _ddb.update_item(
            TableName=AGG_TABLE, Key={"id": {"S": key}},
            UpdateExpression="SET #t = :ttl ADD #c :one",
            ExpressionAttributeNames={"#t": "ttl", "#c": "c"},
            ExpressionAttributeValues={":ttl": {"N": str(int(time.time()) + 180)}, ":one": {"N": "1"}},
            ReturnValues="UPDATED_NEW")
        return int(r["Attributes"]["c"]["N"]) <= RL_LIMIT
    except Exception:
        return True  # fail open — never block real users on a DB hiccup

PLATFORM_FRAME = {
    "x": "Platform: X/Twitter (text feed). Political lean is meaningful here — score it. Focus on lean, topic mix and outrage.",
    "youtube": "Platform: YouTube recommendations. Focus on topic rabbit-holes and what it is pulling the viewer toward. lean is 0 unless a post is clearly political.",
    "instagram": "Platform: Instagram. lean is almost always 0 — the manipulation is identity, aspiration, consumerism and body-image. Focus makesYou.be / .feel / .buy and what it is reinforcing about how the viewer should look and live.",
    "tiktok": "Platform: TikTok For You. lean is almost always 0. Focus on the emotional pull, the identity it is building, and the rabbit-hole. Judge the vibe and what it is optimising the viewer to feel.",
    "linkedin": "Platform: LinkedIn home feed. lean is usually low — the manipulation is professional status, career aspiration, hustle/'thought-leadership' culture and engagement-bait. Focus on the career identity it reinforces and makesYou.be/feel/buy. Flag humble-brags, 'broetry' (one-line-per-paragraph posts) and engagement-farming ('Agree?', 'thoughts?') as bot-ish.",
    "reddit": "Platform: Reddit home/popular. Communities (subreddits) drive it and political lean varies widely by community. Focus on which communities/topics dominate, the rabbit-holes, tribalism and any us-vs-them framing. 'accounts' can be subreddits or users.",
    "facebook": "Platform: Facebook News Feed. Focus on emotional engagement-bait, outrage, us-vs-them and what identity/products it pushes; political lean can be meaningful here. Flag rage-bait, chain-post and low-quality viral content as bot-ish.",
}

SYSTEM_BASE = (
    "You are a calibrated, strictly non-partisan media-literacy analyst. You are shown one person's social-media "
    "feed and must explain what the algorithm is doing to them. Equal-intensity posts on opposite sides get "
    "equal-magnitude scores. Return ONLY a single JSON object (no prose, no markdown, no code fence) with EXACTLY these keys:\n"
    '{"posts":[{"author":"handle/creator or empty","text":"short description","lean":-1..1,"heat":0..1,'
    f'"topic":one of {TOPICS},"emo":one of {EMOS},"bot":0..1}}],'
    '"highlight":"ONE punchy, screenshot-worthy sentence a friend would repeat, summarising what this feed IS "'
    '(e.g. \\"90% AI-hustle bros selling you the dream of getting rich with ChatGPT\\" or \\"gym thirst-traps and $200 supplements, on repeat\\"). Be vivid and specific, not generic.",'
    '"reinforcing":"1-2 sentences: the dominant narrative/identity this feed keeps affirming",'
    '"makesYou":{"be":"the identity it is shaping you into","feel":"the core emotion it cultivates","buy":"what it is selling you"},'
    '"howInfluencing":"1-2 sentences on the mechanism (repetition, FOMO, outrage, aspiration, tribalism...)",'
    '"blindSpots":["a viewpoint or reality notably ABSENT","another"],'
    '"accounts":[{"handle":"@x or creator","lean":-1..1,"share":0..1,"note":"what they push"}],'
    '"suggestions":[{"toGet":"a viewpoint/topic this feed lacks","do":"a specific search query in quotes or a type of account to follow"}],'
    '"aiSlopPct":0-100 rough estimate of engagement-farmed/low-effort/automated content}\n'
    "heat: most informational/promotional posts are 0.2-0.4; reserve >0.6 for genuinely angry/fearful/tribal content. "
    "For 'accounts', only give a non-zero lean when you genuinely have evidence — the account is well-known to you, OR its posts in this feed are clearly political. Otherwise use lean 0. "
    "In each account's 'note', state the basis honestly (e.g. 'well-known right-leaning outlet' vs 'inferred from one political post' vs 'not enough to tell'). Do not fake confidence about accounts you don't recognise. "
    "Use the account unit that actually drives THIS platform: subreddits (e.g. r/antiwork) for Reddit, creators/handles for TikTok/YouTube/Instagram/X/LinkedIn, pages or groups for Facebook — list the specific ones you saw. Make each 'suggestions.do' fit the platform too (a subreddit to join for Reddit, a creator/account to follow, or a specific search query). "
    "Keep strings short and specific. 'suggestions' must be 2-4 concrete items, never placeholders. "
    "'bot'/'aiSlopPct' are honest guesses. Do not invent specific real handles you are unsure about."
)

def _resp(code, obj):
    return {"statusCode": code, "headers": HEADERS, "body": json.dumps(obj)}

def lambda_handler(event, context):
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin") or ""
    method = ((event.get("requestContext") or {}).get("http") or {}).get("method", "POST")
    if method == "OPTIONS":
        return _resp(200, {"ok": True})
    if origin not in ALLOWED_ORIGINS:
        return _resp(403, {"error": "requests must come from doomscrollstats.com"})
    ip = ((event.get("requestContext") or {}).get("http") or {}).get("sourceIp", "")
    if not _rate_ok(ip):
        return _resp(429, {"error": "too many requests — please slow down"})
    try:
        body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body).decode("utf-8")
        data = json.loads(body)
        if data.get("stat") is not None:
            return _stats(data.get("stat"), ip)
        platform = str(data.get("platform", "x")).lower()
        if platform not in PLATFORM_FRAME:
            platform = "x"
        system = [{"text": SYSTEM_BASE + "\n" + PLATFORM_FRAME[platform]}]
        images = data.get("images") or []
        feed = str(data.get("feedText", ""))[:12000].strip()

        if images:  # visual platforms -> Nova Pro vision
            content = [{"text": "These images are screenshots/frames from one person's feed, in scroll order. "
                                "Look carefully at each: the imagery, the creators, captions, on-screen text, products, aesthetics and vibe. "
                                "Identify the distinct posts/reels/videos, work out what the algorithm is feeding this person, "
                                "and fill the schema. Even where there is little text, judge what the visuals are selling and reinforcing. "
                                "Make 'highlight' vivid and specific to what you actually see. "
                                "If an image is blank, a loading screen, or has no real feed content, ignore it — never invent posts."}]
            for img in images[:8]:
                try:
                    raw = base64.b64decode(img.split(",")[-1])
                    content.append({"image": {"format": "jpeg", "source": {"bytes": raw}}})
                except Exception:
                    continue
            if len(content) < 2:
                return _resp(400, {"error": "no valid images"})
            model = MODEL_VISION
            messages = [{"role": "user", "content": content}]
        else:  # text platforms
            if len(feed) < 20:
                return _resp(400, {"error": "feedText too short"})
            model = MODEL_TEXT
            messages = [{"role": "user", "content": [{"text": "Feed OCR text (may be messy — extract the real posts):\n\n" + feed}]}]

        out = _bedrock.converse(modelId=model, system=system, messages=messages,
                                inferenceConfig={"maxTokens": 3000, "temperature": 0})
        text = out["output"]["message"]["content"][0]["text"]
        m = re.search(r"\{.*\}", text, re.S)
        result = json.loads(m.group(0) if m else text)
        for p in result.get("posts", []):
            if isinstance(p, dict):
                if p.get("topic") not in TOPICS:
                    p["topic"] = "Life"
                if p.get("emo") not in EMOS:
                    p["emo"] = "Curiosity"
        result["model"] = model
        result["platform"] = platform
        _log("analyze", plat=platform, mode=("vision" if images else "text"),
             posts=len(result.get("posts", []) or []), ai=result.get("aiSlopPct"), u=_uh(ip))
        return _resp(200, result)
    except Exception as e:
        return _resp(500, {"error": str(e)[:400]})
