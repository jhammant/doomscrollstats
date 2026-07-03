# 🌀 doomscroll.stats

**See the algorithm that's feeding you.** A free, open tool that reads your social feed and shows you its *shape* — what it's reinforcing, and what it's quietly trying to make you **be**, **feel**, and **buy**.

Live at **[doomscrollstats.com](https://doomscrollstats.com)**.

> A mirror, not an alarm. It never tells you "you're being radicalised" — it just shows you the shape of your feed, non-partisan by design (a hard-left and a hard-right bubble score identically), and lets you draw your own conclusion.

## What it does

You screenshot (or screen-record) your feed, drop it in, and it produces a read:

- **The highlight** — one punchy line: *what your feed IS* (e.g. *"90% AI-hustle bros selling you the dream of getting rich with ChatGPT"*)
- **Be / feel / buy** — the identity it shapes, the emotion it cultivates, what it sells you
- **How it influences you** + **your blind spots** (what it hides)
- **Who shapes your feed** — the accounts driving it, and their likely lean
- **Break your bubble** — concrete search terms / voices you're missing
- **Bias compass, topic & tone radars, bot-slop estimate, over-time history, and an aggregate "you're more bubbled than X% of feeds"**

Works on **X/Twitter, Instagram, TikTok, YouTube, LinkedIn, Reddit and Facebook.**

## How it works

| Stage | Text feeds (X, YouTube, LinkedIn, Reddit, Facebook) | Image feeds (Instagram, TikTok) |
|---|---|---|
| **Capture** | screenshots / screen-recording | screenshots / screen-recording |
| **Read** | on-device OCR (Tesseract.js) → on-device model *or* Nova Micro | frames → **Amazon Nova Pro** vision |
| **Analyse** | lean · heat · topic · bot per post + a narrative report | same, from the images |

**Privacy:** no accounts, no tracking cookies. Text feeds are read **on your device**. Image feeds are sent to the model and **immediately discarded — nothing about you is stored.**

## Architecture

- **Frontend** — a single self-contained `index.html` (no build step). On-device OCR via [Tesseract.js](https://tesseract.js.org/) and an optional in-browser classifier via [🤗 transformers.js](https://huggingface.co/docs/transformers.js).
- **Hosting** — S3 (static) behind CloudFront + ACM, on a Route 53 domain.
- **Analyzer** — `lambda/nova_function.py`, an AWS Lambda (Python, stdlib + boto3) behind an API Gateway HTTP API. Calls **Amazon Bedrock** (Nova Micro for text, Nova Pro for vision) via IAM — no API keys. An anonymous DynamoDB counter powers the aggregate comparison.
- **Guardrails** — request origin allowlist, API Gateway throttling, Lambda reserved concurrency, and an AWS Budget cap.

```
Browser ──(screenshots)──► on-device OCR/model ──► report
        └──(sharper / images)──► API Gateway ──► Lambda ──► Bedrock Nova ──► report
```

## Deploy your own

You'll need an AWS account with Bedrock Nova access enabled (us-east-1).

1. **Static site** — create an S3 bucket with website hosting, upload `index.html`, front it with CloudFront + an ACM cert on your domain (Route 53).
2. **Analyzer** — zip `lambda/nova_function.py`, create a Lambda (`python3.12`) with a role that allows `bedrock:InvokeModel` on the Nova models + `dynamodb:UpdateItem/GetItem`; expose it via an API Gateway HTTP API with CORS.
3. Set `API_URL` in `index.html` to your API Gateway URL, and update `ALLOWED_ORIGINS` in the Lambda to your domain.
4. Create a DynamoDB table `doomscroll-agg` (PK `id`, on-demand) for the aggregate counter.
5. Add an AWS Budget + API Gateway throttling so a viral spike can't run away with your bill.

## Honest limitations

Classifying short posts and images is inherently uncertain. Account lean is reliable for well-known accounts and a rough guess for small ones. The "% bot" figure and outlet positions are estimates, not facts. Treat every score as a **conversation starter, not a verdict.**

## Licence

MIT — see [LICENSE](LICENSE). Built by [Jon Hammant](https://hammant.io). ☕ [Buy me a coffee](https://www.buymeacoffee.com/jhammant) to help keep it free to run.
