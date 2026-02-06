#!/usr/bin/env python3
"""
Generates index.html and previouscunts.html from images in the cunts/ folder.
Image filenames are expected in the format:
    YYYY-MM-DD at HH.MM.SS in Location.jpeg
"""

import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

CUNTS_DIR = Path(__file__).parent / "cunts"
INDEX_PATH = Path(__file__).parent / "index.html"
PREVIOUS_PATH = Path(__file__).parent / "previouscunts.html"

IMAGE_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) at (\d{2}\.\d{2}\.\d{2}) in (.+)\.(jpe?g|png|webp|gif)$",
    re.IGNORECASE,
)


def parse_images():
    """Return a list of (sort_key, date_str, time_str, location, filename) sorted newest-first."""
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


def enc(name):
    return quote(name)


# ── Shared HTML ──────────────────────────────────────────────

HEAD = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
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

    /* ── gradient accent bar ── */
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
      max-width: 860px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    /* ── site title ── */
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

    /* ── latest card ── */
    .latest-card {{
      width: 100%;
      background: #1a1a2e;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.06);
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
    .latest-meta .location {{
      color: #6bcb77;
      font-weight: 600;
    }}

    .latest-card img {{
      width: 100%;
      display: block;
    }}

    /* ── nav link ── */
    .nav-link {{
      display: inline-block;
      margin-top: 2rem;
      padding: 0.75rem 2rem;
      background: linear-gradient(135deg, #4d96ff, #6bcb77);
      color: #fff;
      text-decoration: none;
      border-radius: 50px;
      font-weight: 600;
      font-size: 1rem;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .nav-link:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(77,150,255,0.35);
    }}

    /* ── gallery grid (previous page) ── */
    .gallery {{
      width: 100%;
      display: grid;
      grid-template-columns: 1fr;
      gap: 2rem;
      margin-top: 1rem;
    }}

    .gallery-item {{
      background: #1a1a2e;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3);
      border: 1px solid rgba(255,255,255,0.05);
      transition: transform 0.2s;
    }}
    .gallery-item:hover {{
      transform: translateY(-3px);
    }}

    .gallery-item .meta {{
      text-align: center;
      padding: 1rem;
    }}
    .gallery-item .meta .date {{
      font-size: 0.95rem;
      color: #aaa;
    }}
    .gallery-item .meta .location {{
      color: #6bcb77;
      font-weight: 600;
    }}

    .gallery-item img {{
      width: 100%;
      display: block;
    }}

    .empty {{
      text-align: center;
      color: #666;
      font-style: italic;
      margin-top: 3rem;
    }}

    @media (max-width: 600px) {{
      .site-title {{ font-size: 1.5rem; }}
      .container {{ padding: 1.2rem 1rem 3rem; }}
      .latest-header {{ padding: 1rem 1rem 0.75rem; }}
      .latest-meta {{ font-size: 1rem; }}
    }}
  </style>
</head>
<body>
  <div class="container">
"""

FOOT = """\
  </div>
</body>
</html>
"""


# ── Page generators ──────────────────────────────────────────

def generate_index(images):
    parts = [HEAD.format(title="Parked like a cunt in Scotland")]

    parts.append('    <h1 class="site-title"><span class="emoji">🚗</span> Parked like a cunt in Scotland</h1>')

    if images:
        _, date_str, time_str, location, filename = images[0]
        nice_date = format_date(date_str)
        nice_time = format_time(time_str)
        encoded = enc(filename)

        parts.append(f"""
    <div class="latest-card">
      <div class="latest-header">
        <div class="latest-label">Latest</div>
        <div class="latest-meta">{nice_date} at {nice_time} in <span class="location">{location}</span></div>
      </div>
      <img src="cunts/{encoded}" alt="Parked like a cunt in {location}">
    </div>""")
    else:
        parts.append('    <p class="empty">No cunts spotted yet. Stay tuned.</p>')

    parts.append('\n    <a href="previouscunts.html" class="nav-link">Previous cunts →</a>')

    parts.append(FOOT)
    INDEX_PATH.write_text("\n".join(parts))
    print(f"✅ Generated {INDEX_PATH}")


def generate_previous(images):
    parts = [HEAD.format(title="Previous Cunts")]

    parts.append('    <h1 class="site-title">Previous Cunts</h1>')
    parts.append('    <a href="index.html" class="nav-link" style="margin-top:0; margin-bottom:2rem;">← Back to latest</a>')

    previous = images[1:] if len(images) > 1 else images

    if not previous:
        parts.append('    <p class="empty">No previous cunts yet.</p>')
    else:
        parts.append('    <div class="gallery">')
        for _, date_str, time_str, location, filename in previous:
            nice_date = format_date(date_str)
            nice_time = format_time(time_str)
            encoded = enc(filename)

            parts.append(f"""      <div class="gallery-item">
        <div class="meta">
          <span class="date">{nice_date} at {nice_time} in </span>
          <span class="location">{location}</span>
        </div>
        <img src="cunts/{encoded}" alt="Parked like a cunt in {location}">
      </div>""")
        parts.append("    </div>")

    parts.append(FOOT)
    PREVIOUS_PATH.write_text("\n".join(parts))
    print(f"✅ Generated {PREVIOUS_PATH}")


if __name__ == "__main__":
    images = parse_images()
    print(f"Found {len(images)} image(s) in cunts/")
    generate_index(images)
    generate_previous(images)
    print("🎉 Done!")
