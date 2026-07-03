#!/usr/bin/env python3
"""Generate the doomscrollstats.com LinkedIn launch carousel (4x 1080x1350, devprint style)."""
import subprocess, os
W,H=1080,1350
OUT="/Users/jhammant/dev/doomscrollstats/launch"
os.makedirs(OUT,exist_ok=True)

DEFS='''
  <radialGradient id="pg" cx="14%" cy="10%" r="62%"><stop offset="0" stop-color="#7c5cff" stop-opacity="0.42"/><stop offset="1" stop-color="#7c5cff" stop-opacity="0"/></radialGradient>
  <radialGradient id="cg" cx="88%" cy="14%" r="58%"><stop offset="0" stop-color="#31d9ff" stop-opacity="0.22"/><stop offset="1" stop-color="#31d9ff" stop-opacity="0"/></radialGradient>
  <radialGradient id="mg" cx="50%" cy="98%" r="60%"><stop offset="0" stop-color="MOODCOL" stop-opacity="0.20"/><stop offset="1" stop-color="MOODCOL" stop-opacity="0"/></radialGradient>
  <linearGradient id="rain" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#31d9ff"/><stop offset="0.4" stop-color="#7c5cff"/><stop offset="0.7" stop-color="#ff5cc8"/><stop offset="1" stop-color="#ffd166"/></linearGradient>
  <linearGradient id="rainh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5fe0ff"/><stop offset="0.5" stop-color="#b6a6ff"/><stop offset="1" stop-color="#ffc6ec"/></linearGradient>
  <linearGradient id="head" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#cdd6ff"/></linearGradient>
'''

def header(mood="#7c5cff"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>{DEFS.replace("MOODCOL",mood)}</defs>
  <rect width="{W}" height="{H}" fill="#070913"/>
  <rect width="{W}" height="{H}" fill="url(#pg)"/>
  <rect width="{W}" height="{H}" fill="url(#cg)"/>
  <rect width="{W}" height="{H}" fill="url(#mg)"/>
  <g transform="translate(920,140)" opacity="0.9">
    <circle r="150" fill="none" stroke="#ffffff" stroke-opacity="0.09"/>
    <circle r="96" fill="none" stroke="#ffffff" stroke-opacity="0.06"/>
    <circle r="42" fill="url(#rain)"/>
    <circle cx="0" cy="-96" r="8" fill="#62f0a7"/><circle cx="150" cy="10" r="11" fill="#ff5cc8"/><circle cx="-70" cy="118" r="7" fill="#ffd166"/>
  </g>
  <g transform="translate(72,74)">
    <rect width="64" height="64" rx="17" fill="url(#rain)"/>
    <text x="32" y="47" font-family="sans-serif" font-size="37" font-weight="900" fill="#0a0d18" text-anchor="middle">d</text>
    <text x="82" y="44" font-family="sans-serif" font-size="33" font-weight="900" fill="#eef3ff">doomscrollstats<tspan fill="#5b6478">.com</tspan></text>
  </g>'''

def footer(tag="free · private · on-device · open-source"):
    return f'''  <text x="72" y="1288" font-family="sans-serif" font-size="27" font-weight="800"><tspan fill="#62f0a7">doomscrollstats.com</tspan></text>
  <text x="72" y="1322" font-family="sans-serif" font-size="20" fill="#9aa7c7">{tag}</text>
</svg>'''

def eyebrow(y,txt,col="#9aa7c7"):
    return f'<text x="74" y="{y}" font-family="sans-serif" font-size="24" font-weight="800" letter-spacing="5" fill="{col}">{txt}</text>'

# ---- Card 1: the hook (a question) ----
c1=header("#7c5cff")+ eyebrow(320,"A MIRROR FOR YOUR FEED")+'''
  <text font-family="Georgia, serif" font-style="italic" font-weight="900" fill="url(#head)" font-size="96"><tspan x="70" y="470">What is your</tspan><tspan x="70" y="580">feed turning</tspan><tspan x="70" y="690">you into?</tspan></text>
  <text x="74" y="830" font-family="sans-serif" font-size="34" fill="#c7d0e6" font-weight="600">A free tool. Screenshot your feed and see</text>
  <text x="74" y="878" font-family="sans-serif" font-size="34" fill="#9aa7c7">what the algorithm is quietly training you to</text>
  <text x="74" y="926" font-family="sans-serif" font-size="34" font-weight="800" fill="url(#rainh)">be, feel &amp; buy.</text>
'''+footer()

# ---- Card 2: what it shows ----
def bullet(y,dot,head,sub):
    return (f'<circle cx="88" cy="{y-9}" r="8" fill="{dot}"/>'
            f'<text x="120" y="{y}" font-family="sans-serif" font-size="35" font-weight="800" fill="#eef3ff">{head}</text>'
            f'<text x="120" y="{y+42}" font-family="sans-serif" font-size="27" fill="#9aa7c7">{sub}</text>')
c2=header("#31d9ff")+eyebrow(300,"WHAT IT SHOWS YOU","#31d9ff")+'''
  <text font-family="Georgia, serif" font-style="italic" font-weight="900" fill="url(#head)" font-size="72"><tspan x="70" y="400">Your feed, read back</tspan><tspan x="70" y="484">to you.</tspan></text>
'''+bullet(620,"#31d9ff","What it makes you be, feel &amp; buy","the identity it&#39;s selling, on repeat")\
   +bullet(748,"#7c5cff","Who&#39;s really shaping it","the accounts &amp; their political lean")\
   +bullet(876,"#ff5cc8","Your blind spots","the viewpoints you never get shown")\
   +bullet(1004,"#ffd166","How bubbled you are","vs everyone else who&#39;s checked")\
   +bullet(1132,"#62f0a7","How much is AI slop","engagement-bait &amp; automated noise")\
   +footer()

# ---- Card 3: example read ----
c3=header("#e0484a")+eyebrow(300,"AN EXAMPLE READ","#ff9b9b")+'''
  <text x="74" y="476" font-family="sans-serif" font-size="118" fill="#ff6b6b">&#9876;</text>
  <text x="74" y="600" font-family="sans-serif" font-size="52" font-weight="900" fill="#eef3ff">The Culture Warrior</text>
  <text x="74" y="648" font-family="sans-serif" font-size="26" font-weight="700" letter-spacing="2" fill="#9aa7c7">POLITICS  ·  HEAVILY BUBBLED</text>
  <text font-family="Georgia, serif" font-style="italic" font-weight="900" fill="url(#rainh)" font-size="60"><tspan x="70" y="820">&#8220;90% outrage bait</tspan><tspan x="70" y="900">dressed as news</tspan><tspan x="70" y="980">&#8212; and it&#39;s working.&#8221;</tspan></text>
  <text x="74" y="1080" font-family="sans-serif" font-size="28" fill="#9aa7c7">Non-partisan by design: a hard-left and a hard-right</text>
  <text x="74" y="1118" font-family="sans-serif" font-size="28" fill="#9aa7c7">feed score exactly the same.</text>
'''+footer()

# ---- Card 4: CTA / trust ----
c4=header("#62f0a7")+eyebrow(300,"NO LOGIN · NOTHING STORED","#62f0a7")+'''
  <text font-family="Georgia, serif" font-style="italic" font-weight="900" fill="url(#head)" font-size="92"><tspan x="70" y="470">Try it on</tspan><tspan x="70" y="580">your feed.</tspan></text>
  <text x="74" y="700" font-family="sans-serif" font-size="30" fill="#c7d0e6" font-weight="700">Works on 7 feeds:</text>
  <text x="74" y="752" font-family="sans-serif" font-size="29" fill="#9aa7c7">X · Instagram · TikTok · YouTube ·</text>
  <text x="74" y="796" font-family="sans-serif" font-size="29" fill="#9aa7c7">Reddit · LinkedIn · Facebook</text>
  <text x="74" y="930" font-family="sans-serif" font-size="30" fill="#eef3ff" font-weight="700">Reads on your phone. No account. No</text>
  <text x="74" y="972" font-family="sans-serif" font-size="30" fill="#eef3ff" font-weight="700">tracking. The code is all open-source.</text>
  <rect x="72" y="1060" width="620" height="86" rx="18" fill="url(#rain)"/>
  <text x="382" y="1116" font-family="sans-serif" font-size="40" font-weight="900" fill="#0a0d18" text-anchor="middle">doomscrollstats.com</text>
'''+footer("what's yours?")

cards={"1-hook":c1,"2-what":c2,"3-example":c3,"4-cta":c4}
for name,svg in cards.items():
    sp=f"{OUT}/{name}.svg"; pp=f"{OUT}/launch-{name}.png"
    open(sp,"w").write(svg)
    subprocess.run(["rsvg-convert","-w",str(W),"-h",str(H),sp,"-o",pp],check=True)
    os.remove(sp)
    print("wrote",pp)
