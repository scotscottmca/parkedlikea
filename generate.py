#!/usr/bin/env python3
"""
Generates a single index.html from images in the cunts/ folder.
Image filenames are expected in the format:
    YYYY-MM-DD at HH.MM.SS in Location.jpeg
"""

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

CUNTS_DIR = Path(__file__).parent / "cunts"
INDEX_PATH = Path(__file__).parent / "index.html"

IMAGE_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2}\.\d{2}) in (.+)\.(jpe?g|png|webp|gif)$",
    re.IGNORECASE,
)


def parse_images():
    images = []
    for f in CUNTS_DIR.iterdir():
        m = IMAGE_PATTERN.match(f.name)
        if m:
            date_str = m.group(1)
            time_str = m.group(2)
            location = m.group(3).strip()
            sort_key = f"{date_str} {time_str}"
            images.append((sort_key, date_str, time_str, location, f.name))
    images.sort(key=lambda x: x[0], reverse=True)
    return images


def format_time(time_str):
    parts = time_str.split(".")
    return f"{parts[0]}:{parts[1]}"


def format_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%-d %B %Y")


def make_anchor(date_str, time_str, location):
    slug = f"{date_str}-{time_str.replace('.', '')}-{location}"
    slug = re.sub(r"[^a-zA-Z0-9-]", "-", slug).lower().strip("-")
    return slug


def enc(name):
    return quote(name)


def generate(images):
    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Parked like a cunt in Scotland</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚗</text></svg>">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0f0f1a;
      color: #e8e8e8;
      min-height: 100vh;
    }}

    body::before {{
      content: '';
      display: block;
      height: 4px;
      background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff, #ff6b6b);
      background-size: 200% 100%;
      animation: shimmer 4s linear infinite;
    }}
    @keyframes shimmer {{
      0%   {{ background-position: 200% 0; }}
      100% {{ background-position: -200% 0; }}
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    /* ── title ── */
    .site-title {{
      font-size: 2.2rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 2.5rem;
      background: linear-gradient(135deg, #ff6b6b, #ffd93d);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1.3;
    }}
    .site-title .emoji {{
      -webkit-text-fill-color: initial;
    }}

    /* ── counter ── */
    .counter {{
      font-size: 1.1rem;
      font-weight: 600;
      color: #ff6b6b;
      text-align: center;
      margin-top: -1.5rem;
      margin-bottom: 2rem;
      letter-spacing: 1px;
    }}

    /* ── latest card ── */
    .latest-card {{
      width: 100%;
      max-width: 860px;
      background: #1a1a2e;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.06);
      position: relative;
    }}

    .latest-header {{
      text-align: center;
      padding: 1.5rem 1.5rem 1rem;
    }}

    .latest-label {{
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 3px;
      color: #ffd93d;
      margin-bottom: 0.5rem;
    }}

    .latest-meta {{
      font-size: 1.15rem;
      color: #c0c0c0;
      font-weight: 400;
    }}
    .latest-meta .location,
    .gallery-item .location {{
      color: #6bcb77;
      font-weight: 600;
    }}

    .latest-card img {{
      width: 100%;
      display: block;
    }}

    /* ── share button ── */
    .share-btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      margin-top: 0.6rem;
      padding: 0.35rem 0.9rem;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.12);
      color: #aaa;
      border-radius: 50px;
      font-size: 0.78rem;
      font-family: inherit;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .share-btn:hover {{
      background: rgba(255,255,255,0.14);
      color: #fff;
    }}
    .share-btn.copied {{
      background: rgba(107,203,119,0.2);
      border-color: #6bcb77;
      color: #6bcb77;
    }}

    /* ── divider ── */
    .divider {{
      width: 100%;
      max-width: 860px;
      margin: 3rem 0 2rem;
      border: none;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    }}

    /* ── section title ── */
    .section-title {{
      font-size: 1.6rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 1.5rem;
      color: #ffd93d;
    }}

    /* ── gallery grid ── */
    .gallery {{
      width: 100%;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.5rem;
    }}

    .gallery-item {{
      background: #1a1a2e;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
      border: 1px solid rgba(255,255,255,0.05);
      transition: transform 0.2s;
      display: flex;
      flex-direction: column;
    }}
    .gallery-item:hover {{
      transform: translateY(-3px);
    }}

    .gallery-item .meta {{
      text-align: center;
      padding: 0.8rem 0.6rem 0.5rem;
    }}
    .gallery-item .meta .date {{
      font-size: 0.8rem;
      color: #aaa;
      display: block;
      margin-bottom: 0.15rem;
    }}
    .gallery-item .meta .location {{
      font-size: 0.85rem;
    }}

    .gallery-item img {{
      width: 100%;
      display: block;
      flex: 1;
      object-fit: cover;
    }}

    .empty {{
      text-align: center;
      color: #666;
      font-style: italic;
      margin-top: 3rem;
    }}

    /* ── scroll target offset ── */
    .anchor-target {{
      scroll-margin-top: 1.5rem;
    }}

    /* ── responsive ── */
    @media (max-width: 900px) {{
      .gallery {{ grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
    }}
    @media (max-width: 600px) {{
      .site-title {{ font-size: 1.5rem; }}
      .container {{ padding: 1.2rem 1rem 3rem; }}
      .latest-header {{ padding: 1rem 1rem 0.75rem; }}
      .latest-meta {{ font-size: 1rem; }}
      .gallery {{ grid-template-columns: 1fr; gap: 1rem; }}
      .section-title {{ font-size: 1.3rem; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1 class="site-title"><span class="emoji">🚗</span> Parked like a cunt in Scotland</h1>
    <div class="counter">{len(images)} Total Cunt{"s" if len(images) != 1 else ""}</div>
"""

    # ── Latest image ──
    if images:
        _, date_str, time_str, location, filename = images[0]
        nice_date = format_date(date_str)
        nice_time = format_time(time_str)
        encoded = enc(filename)
        anchor = make_anchor(date_str, time_str, location)

        html += f"""
    <div class="latest-card anchor-target" id="{anchor}">
      <div class="latest-header">
        <div class="latest-label">Latest</div>
        <div class="latest-meta">{nice_date} at {nice_time} in <span class="location">{location}</span></div>
        <button class="share-btn" onclick="shareLink('{anchor}')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          Share
        </button>
      </div>
      <img src="cunts/{encoded}" alt="Parked like a cunt in {location}">
    </div>
"""
    else:
        html += '    <p class="empty">No cunts spotted yet. Stay tuned.</p>\n'

    # ── Previous section ──
    previous = images[1:] if len(images) > 1 else []

    if previous:
        html += """
    <hr class="divider">
    <h2 class="section-title">Previous Cunts</h2>
    <div class="gallery">
"""
        for _, date_str, time_str, location, filename in previous:
            nice_date = format_date(date_str)
            nice_time = format_time(time_str)
            encoded = enc(filename)
            anchor = make_anchor(date_str, time_str, location)

            html += f"""      <div class="gallery-item anchor-target" id="{anchor}">
        <div class="meta">
          <span class="date">{nice_date} at {nice_time}</span>
          <span class="location">{location}</span>
          <button class="share-btn" onclick="shareLink('{anchor}')">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
            Share
          </button>
        </div>
        <img src="cunts/{encoded}" alt="Parked like a cunt in {location}">
      </div>
"""
        html += "    </div>\n"

    # ── Script & footer ──
    html += """
    <script>
      function shareLink(anchor) {
        const url = window.location.origin + window.location.pathname + '#' + anchor;
        navigator.clipboard.writeText(url).then(() => {
          const btn = document.querySelector('#' + CSS.escape(anchor) + ' .share-btn');
          btn.classList.add('copied');
          btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            Copied!`;
          setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = `
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              Share`;
          }, 2000);
        });
      }
    </script>
  </div>
</body>
</html>
"""

    INDEX_PATH.write_text(html)
    print(f"✅ Generated {INDEX_PATH}")


if __name__ == "__main__":
    images = parse_images()
    print(f"Found {len(images)} image(s) in cunts/")
    generate(images)
    print("🎉 Done!")
