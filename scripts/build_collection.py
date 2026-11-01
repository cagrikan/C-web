#!/usr/bin/env python3
"""Generate bilingual static collection gallery and detail pages from verified inventory."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".taste-skill" / "collection-inventory.json"
RESEARCHED_COPY = ROOT / ".taste-skill" / "researched-copy.json"
BASE = "https://cagricakir.com.tr"
EMAIL = "mail@cagricakir.com.tr"
PUBLISHED_IDS = {"revox-b77", "pioneer-s-z85d-pair"}
PUBLISHED_OVERRIDES = {
    "revox-b77": {
        "status": "sale-owner-working",
        "images": ["assets/collection/revox-b77-representative-scene.png"],
    },
    "pioneer-s-z85d-pair": {
        "status": "sale-unverified-working",
        "images": ["assets/collection/pioneer-s-z85d-pair-representative-scene.png"],
    },
}
RELATED_OFFICIAL_MODELS = {
    "revox-b77": [
        {
            "label_tr": "Güncel B77 MK III — Revox (Alice Cooper Limited Edition)",
            "label_en": "Current B77 MK III — Revox (Alice Cooper Limited Edition)",
            "url": "https://revox.com/de-de/products/revox-b77-mk-iii-stereo-tape-recorder-alice-cooper-limited-edition",
        }
    ]
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def title_for(item: dict, lang: str) -> str:
    return item.get("title_en") if lang == "en" and item.get("title_en") else item["title"]


def status_copy(status: str, lang: str) -> tuple[str, str]:
    copies = {
        "sale-owner-working": (
            "Tekliflere açık",
            "Open to offers",
        ),
        "sale-unverified-working": (
            "Tekliflere açık",
            "Open to offers",
        ),
        "pending": (
            "Satış ve çalışma durumu teyit bekliyor",
            "Sale and operating status pending confirmation",
        ),
        "display-only": (
            "Koleksiyonda · Satılık değil",
            "Collection display · Not for sale",
        ),
    }
    tr, en = copies[status]
    return (en, status) if lang == "en" else (tr, status)


def placeholder(title: str) -> str:
    return (
        '<div class="collection-placeholder" role="img" '
        f'aria-label="{esc(title)} için görsel hazırlanıyor">'
        f"<span>{esc(title)}</span></div>"
    )


def picture(item: dict, lang: str, detail: bool = False) -> str:
    title = title_for(item, lang)
    images = item["images"]
    if not images:
        return placeholder(title)
    scene_suffix = "representative interior scene" if lang == "en" else "temsili mekân sahnesi"
    primary = (
        '<div class="collection-photo">'
        f'<img src="{esc(images[0])}" alt="{esc(title)}, {scene_suffix}" width="1536" height="960" loading="eager" decoding="sync">'
        "</div>"
    )
    if not detail:
        return primary
    thumbs = "".join(
        f'<img src="{esc(src)}" alt="{esc(title)} — {index}. görünüm" width="1200" height="1500">'
        for index, src in enumerate(images[1:], start=2)
    )
    thumbs_block = f'<div class="collection-thumbs">{thumbs}</div>' if thumbs else ""
    caption = "AI-generated illustrative scene." if lang == "en" else "Yapay zekâyla hazırlanmış temsili sahne."
    return f'<figure class="collection-figure">{primary}{thumbs_block}<figcaption>{caption}</figcaption></figure>'


def header(lang: str, collection_file: str, home_file: str, alt_file: str) -> str:
    if lang == "en":
        skip, nav_label, services, method, collection, contact, menu, alt = (
            "Skip to content",
            "Primary navigation",
            "Services",
            "Method",
            "Collection",
            "Contact",
            "Menu",
            "TR",
        )
        services_href = "index_en.html#services"
        method_href = "index_en.html#method"
    else:
        skip, nav_label, services, method, collection, contact, menu, alt = (
            "İçeriğe geç",
            "Ana navigasyon",
            "Hizmetler",
            "Çalışma modeli",
            "Koleksiyon",
            "İletişim",
            "Menü",
            "EN",
        )
        services_href = "index.html#hizmetler"
        method_href = "index.html#metod"
    return f"""
  <a class="skip-link" href="#main">{skip}</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="logo" href="{home_file}" aria-label="Sabri Çağrı Çakır">{'S. Çağrı Çakır'}</a>
      <details class="nav-menu" open>
        <summary>{menu}</summary>
        <nav aria-label="{nav_label}">
          <ul class="nav-list">
            <li><a href="{services_href}">{services}</a></li>
            <li><a href="{method_href}">{method}</a></li>
            <li><a href="{collection_file}" aria-current="page">{collection}</a></li>
            <li class="lang-switch"><a href="{alt_file}" lang="{'tr' if lang == 'en' else 'en'}">{alt}</a></li>
            <li><a class="nav-cta" href="mailto:{EMAIL}">{contact}</a></li>
          </ul>
        </nav>
      </details>
    </div>
  </header>"""


def footer(lang: str, collection_file: str) -> str:
    if lang == "en":
        copy = "© 2026 Sabri Çağrı Çakır · Ankara, Turkey · Personal collection"
        email, collection = "Email", "Collection"
    else:
        copy = "© 2026 Sabri Çağrı Çakır · Ankara, Türkiye · Kişisel koleksiyon"
        email, collection = "E-posta", "Koleksiyon"
    return f"""
  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <p class="footer-copy">{copy}</p>
        <div class="footer-links">
          <a href="mailto:{EMAIL}">{email}</a>
          <a href="{collection_file}">{collection}</a>
        </div>
      </div>
      <a class="geoni-badge" href="https://geoni.ai/s/01d55c80-5ff5-48c1-93dc-387c8262efb7" target="_blank" rel="noopener" title="AI Friendly — Checked by GEONI"><img src="https://geoni.ai/badge/01d55c80-5ff5-48c1-93dc-387c8262efb7" alt="AI Friendly — Checked by GEONI" width="232" height="44"></a>
    </div>
  </footer>"""


def head(
    *,
    lang: str,
    title: str,
    description: str,
    canonical_file: str,
    tr_file: str,
    en_file: str,
    structured_data: dict,
) -> str:
    canonical = f"{BASE}/{canonical_file}"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="tr-TR" href="{BASE}/{tr_file}">
  <link rel="alternate" hreflang="en" href="{BASE}/{en_file}">
  <link rel="alternate" hreflang="x-default" href="{BASE}/{tr_file}">
  <link rel="stylesheet" href="assets/site.css">
  <link rel="stylesheet" href="assets/collection.css">
  <script src="assets/site.js" defer></script>
  <script src="assets/collection.js" defer></script>
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary">
  <script type="application/ld+json">
{json.dumps(structured_data, ensure_ascii=False, indent=2)}
  </script>
</head>"""


def gallery(data: dict, lang: str) -> str:
    is_en = lang == "en"
    filename = "collection.html" if is_en else "koleksiyon.html"
    other = "koleksiyon.html" if is_en else "collection.html"
    home = "index_en.html" if is_en else "index.html"
    title = (
        "Technology, Sound & Image Collection | Sabri Çağrı Çakır"
        if is_en
        else "Teknoloji, Ses ve Görüntü Koleksiyonu | Sabri Çağrı Çakır"
    )
    description = (
        "A personal collection of computing, sound, photography and cinema objects. Selected pieces are open to offers."
        if is_en
        else "Bilgisayar, ses, fotoğraf ve sinema nesnelerinden oluşan kişisel koleksiyon. Seçili parçalar tekliflere açıktır."
    )
    cards = []
    elements = []
    for index, item in enumerate(data["items"], start=1):
        item_title = title_for(item, lang)
        category = item["category_en" if is_en else "category_tr"]
        category_key = {
            "Computing & Writing": "computing",
            "Bilgisayar & Yazı": "computing",
            "Sound & Music": "sound",
            "Ses & Müzik": "sound",
            "Photography & Cinema": "image",
            "Fotoğraf & Sinema": "image",
            "Time & Mechanism": "time",
            "Zaman & Mekanizma": "time",
        }[category]
        href = item["slug_en" if is_en else "slug_tr"]
        excerpt = item["excerpt_en" if is_en else "excerpt_tr"]
        status, code = status_copy(item["status"], lang)
        cards.append(
            f"""<a class="collection-card" data-category="{category_key}" href="{href}">
  {picture(item, lang)}
  <div class="collection-card-body">
    <h2>{esc(item_title)}</h2>
    <p>{esc(excerpt)}</p>
    <span class="collection-status" data-status="{code}">{esc(status)}</span>
    <span class="card-link">{'View record →' if is_en else 'Kaydı incele →'}</span>
  </div>
</a>"""
        )
        elements.append(
            {
                "@type": "ListItem",
                "position": index,
                "url": f"{BASE}/{href}",
                "name": item_title,
            }
        )

    labels = [("all", "All"), ("sound", "Sound & Music")] if is_en else [("all", "Tümü"), ("sound", "Ses & Müzik")]
    filters = "".join(
        f'<button class="collection-filter" type="button" data-filter="{key}" aria-pressed="{"true" if key == "all" else "false"}">{label}</button>'
        for key, label in labels
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title.split(" | ")[0],
        "url": f"{BASE}/{filename}",
        "inLanguage": lang,
        "about": "Personal collection of historical technology, sound and image objects",
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(elements), "itemListElement": elements},
    }
    hero = (
        (
            "The memory of machines.",
            "A personal technology, sound, photography and cinema collection of machines that wrote, calculated, recorded, projected and played. It is a secondary part of this site.",
            "Collection",
        )
        if is_en
        else (
            "Makinelerin hafızası.",
            "Yazan, hesaplayan, kaydeden, gösteren ve çalan makinelerden kişisel bir teknoloji, ses, fotoğraf ve sinema koleksiyonu. Bu sitenin danışmanlık odağından ayrı ve ikincil kişisel bölümüdür.",
            "Koleksiyon",
        )
    )
    return f"""{head(lang=lang, title=title, description=description, canonical_file=filename, tr_file='koleksiyon.html', en_file='collection.html', structured_data=schema)}
<body class="collection-page">
{header(lang, filename, home, other)}
  <main id="main">
    <section class="collection-hero">
      <div class="container">
        <div>
          <h1>{hero[0]}</h1>
          <p class="collection-intro">{hero[1]}</p>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="collection-tools" aria-label="{'Filter collection' if is_en else 'Koleksiyonu filtrele'}">{filters}</div>
        <div class="collection-grid">
          {''.join(cards)}
        </div>
      </div>
    </section>
  </main>
{footer(lang, filename)}
</body>
</html>
"""


def detail(item: dict, lang: str) -> str:
    is_en = lang == "en"
    filename = item["slug_en" if is_en else "slug_tr"]
    other = item["slug_tr" if is_en else "slug_en"]
    gallery_file = "collection.html" if is_en else "koleksiyon.html"
    home = "index_en.html" if is_en else "index.html"
    item_title = title_for(item, lang)
    excerpt = item["excerpt_en" if is_en else "excerpt_tr"]
    description = item["description_en" if is_en else "description_tr"]
    category = item["category_en" if is_en else "category_tr"]
    detail_descriptors = {
        "revox-b77": {
            "en": "Analogue reel-to-reel tape recorder · Sound & Music",
            "tr": "Analog makaralı teyp · Ses & Müzik",
        },
        "pioneer-s-z85d-pair": {
            "en": "Stereo speaker pair · Sound & Music",
            "tr": "Stereo hoparlör çifti · Ses & Müzik",
        },
    }
    category = detail_descriptors.get(item["id"], {}).get(lang, category)
    source_candidates = [*item.get("sources", []), *RELATED_OFFICIAL_MODELS.get(item["id"], [])]
    sources = list({source["url"]: source for source in source_candidates}.values())
    page_title = f"{item_title} | {'Collection' if is_en else 'Koleksiyon'}"
    schema = {
        "@context": "https://schema.org",
        "@type": "IndividualProduct",
        "name": item_title,
        "description": excerpt,
        "url": f"{BASE}/{filename}",
        "inLanguage": lang,
    }
    if item["images"]:
        schema["image"] = [f"{BASE}/{src}" for src in item["images"]]

    if is_en:
        back = "← Back to collection"
        inquire = "Send an offer"
        subject = f"Offer for collection item: {item_title}"
        sources_heading = "Historical references"
    else:
        back = "← Koleksiyona dön"
        inquire = "Teklif gönder"
        subject = f"Koleksiyon teklifi: {item_title}"
        sources_heading = "Tarihsel kaynaklar"

    source_links = "".join(
        f'<li><a href="{esc(source["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(source.get("label_en" if is_en else "label_tr", source.get("label", source["url"])))}</a></li>'
        for source in sources
    )
    source_block = (
        f'<section class="collection-sources" aria-labelledby="sources-heading"><h2 id="sources-heading">{sources_heading}</h2>'
        f'<ul>{source_links}</ul></section>'
        if source_links
        else ""
    )

    cta = ""
    if item["status"] in {"sale-owner-working", "sale-unverified-working"}:
        cta = f'<div class="actions"><a class="btn btn-primary" href="mailto:{EMAIL}?subject={quote(subject)}">{inquire}</a></div>'

    return f"""{head(lang=lang, title=page_title, description=excerpt, canonical_file=filename, tr_file=item['slug_tr'], en_file=item['slug_en'], structured_data=schema)}
<body class="collection-page">
{header(lang, gallery_file, home, other)}
  <main id="main">
    <article class="collection-detail">
      <div class="container collection-detail-grid">
        <div class="collection-detail-media">
          {picture(item, lang, detail=True)}
        </div>
        <div class="collection-detail-copy">
          <h1>{esc(item_title)}</h1>
          <p class="collection-category">{esc(category)}</p>
          <a class="collection-back" href="{gallery_file}">{back}</a>
          <p class="lede">{esc(excerpt)}</p>
          <div class="prose"><p>{esc(description)}</p></div>
          {cta}
{source_block}
        </div>
      </div>
    </article>
  </main>
{footer(lang, gallery_file)}
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    researched = json.loads(RESEARCHED_COPY.read_text(encoding="utf-8"))["items"]
    inventory_ids = {item["id"] for item in data["items"]}
    if inventory_ids != set(researched):
        missing = sorted(inventory_ids - set(researched))
        extra = sorted(set(researched) - inventory_ids)
        raise SystemExit(f"Researched copy coverage mismatch; missing={missing}, extra={extra}")
    for item in data["items"]:
        item.update(researched[item["id"]])
        if item["id"] in PUBLISHED_OVERRIDES:
            item.update(PUBLISHED_OVERRIDES[item["id"]])
    published_items = [item for item in data["items"] if item["id"] in PUBLISHED_IDS]
    if {item["id"] for item in published_items} != PUBLISHED_IDS:
        raise SystemExit("Published collection subset is incomplete")
    published_data = {**data, "items": published_items}
    outputs = {
        "koleksiyon.html": gallery(published_data, "tr"),
        "collection.html": gallery(published_data, "en"),
    }
    for item in published_items:
        outputs[item["slug_tr"]] = detail(item, "tr")
        outputs[item["slug_en"]] = detail(item, "en")
    for filename, content in outputs.items():
        (ROOT / filename).write_text(content, encoding="utf-8")
    update_discovery_files(published_data)
    print(f"Generated {len(outputs)} collection pages")


def update_discovery_files(data: dict) -> None:
    sitemap_path = ROOT / "sitemap.xml"
    sitemap = sitemap_path.read_text(encoding="utf-8")
    sitemap = re.sub(
        r"\s*<url>\s*<loc>https://cagricakir\.com\.tr/(?:koleksiyon|collection)[^<]*</loc>.*?</url>",
        "",
        sitemap,
        flags=re.DOTALL,
    )
    pairs = [("koleksiyon.html", "collection.html")]
    pairs.extend((item["slug_tr"], item["slug_en"]) for item in data["items"])
    entries = []
    for tr_file, en_file in pairs:
        for filename in (tr_file, en_file):
            entries.append(
                "  <url>\n"
                f"    <loc>{BASE}/{filename}</loc>\n"
                "    <lastmod>2026-11-01</lastmod>\n"
                "    <changefreq>monthly</changefreq>\n"
                "    <priority>0.6</priority>\n"
                f"    <xhtml:link rel=\"alternate\" hreflang=\"tr-TR\" href=\"{BASE}/{tr_file}\"/>\n"
                f"    <xhtml:link rel=\"alternate\" hreflang=\"en\" href=\"{BASE}/{en_file}\"/>\n"
                f"    <xhtml:link rel=\"alternate\" hreflang=\"x-default\" href=\"{BASE}/{tr_file}\"/>\n"
                "  </url>"
            )
    sitemap = sitemap.replace("</urlset>", "\n".join(entries) + "\n</urlset>")
    sitemap_path.write_text(sitemap, encoding="utf-8")

    llms_path = ROOT / "llms.txt"
    llms = llms_path.read_text(encoding="utf-8")
    marker = "## Personal collection"
    block = (
        "## Personal collection\n\n"
        "A secondary personal archive. Two sound-system records are currently public; remaining collection records are private drafts. "
        "Selected public pieces are open to offers through the listed contact channel.\n\n"
        f"- Turkish gallery: {BASE}/koleksiyon.html\n"
        f"- English gallery: {BASE}/collection.html\n"
        f"- Revox B77: {BASE}/koleksiyon-revox-b77.html | {BASE}/collection-revox-b77.html\n"
        f"- Pioneer S-Z85D speaker pair: {BASE}/koleksiyon-pioneer-s-z85d-hoparlor-cifti.html | {BASE}/collection-pioneer-s-z85d-speaker-pair.html\n"
    )
    if marker in llms:
        llms = re.sub(r"## Personal collection\n.*?(?=\n## |\Z)", block.rstrip(), llms, flags=re.DOTALL)
    else:
        llms = llms.rstrip() + "\n\n" + block
    llms_path.write_text(llms, encoding="utf-8")


if __name__ == "__main__":
    main()
