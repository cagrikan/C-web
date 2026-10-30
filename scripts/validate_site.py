#!/usr/bin/env python3
"""Validate the static site using only Python's standard library."""

from __future__ import annotations

import json
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://cagricakir.com.tr"

EXPECTED_PAGES = {
    "index.html": f"{BASE_URL}/",
    "index_en.html": f"{BASE_URL}/index_en.html",
    "fractional-cto-danismanligi.html": f"{BASE_URL}/fractional-cto-danismanligi.html",
    "fractional-cto-advisory.html": f"{BASE_URL}/fractional-cto-advisory.html",
    "yonetici-teknoloji-danismanligi.html": f"{BASE_URL}/yonetici-teknoloji-danismanligi.html",
    "executive-technology-advisor.html": f"{BASE_URL}/executive-technology-advisor.html",
    "yapay-zeka-gorunurlugu-ve-yonetisimi.html": f"{BASE_URL}/yapay-zeka-gorunurlugu-ve-yonetisimi.html",
    "ai-visibility-and-governance.html": f"{BASE_URL}/ai-visibility-and-governance.html",
    "dijital-donusum-ofisi.html": f"{BASE_URL}/dijital-donusum-ofisi.html",
    "digital-transformation-office.html": f"{BASE_URL}/digital-transformation-office.html",
    "dijital-donusum-danismani-nedir.html": f"{BASE_URL}/dijital-donusum-danismani-nedir.html",
    "digital-transformation-consultant.html": f"{BASE_URL}/digital-transformation-consultant.html",
    "geo-yapay-zeka-gorunurlugu-nedir.html": f"{BASE_URL}/geo-yapay-zeka-gorunurlugu-nedir.html",
    "geo-ai-visibility-guide.html": f"{BASE_URL}/geo-ai-visibility-guide.html",
}

LANGUAGE_PAIRS = [
    ("index.html", "index_en.html"),
    ("fractional-cto-danismanligi.html", "fractional-cto-advisory.html"),
    ("yonetici-teknoloji-danismanligi.html", "executive-technology-advisor.html"),
    ("yapay-zeka-gorunurlugu-ve-yonetisimi.html", "ai-visibility-and-governance.html"),
    ("dijital-donusum-ofisi.html", "digital-transformation-office.html"),
    ("dijital-donusum-danismani-nedir.html", "digital-transformation-consultant.html"),
    ("geo-yapay-zeka-gorunurlugu-nedir.html", "geo-ai-visibility-guide.html"),
]


@dataclass
class ParsedPage:
    path: Path
    lang: str | None = None
    title: str = ""
    descriptions: list[str] = field(default_factory=list)
    canonicals: list[str] = field(default_factory=list)
    alternates: dict[str, str] = field(default_factory=dict)
    hrefs: list[str] = field(default_factory=list)
    srcs: list[str] = field(default_factory=list)
    ids: list[str] = field(default_factory=list)
    json_ld: list[Any] = field(default_factory=list)
    raw_text: str = ""


class StaticPageParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.page = ParsedPage(path=path)
        self._in_title = False
        self._in_json_ld = False
        self._json_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key.lower(): value for key, value in attrs}
        tag = tag.lower()

        if tag == "html":
            self.page.lang = data.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and (data.get("name") or "").lower() == "description":
            if data.get("content"):
                self.page.descriptions.append(data["content"] or "")
        elif tag == "link":
            rel = (data.get("rel") or "").lower().split()
            href = data.get("href")
            if href:
                self.page.hrefs.append(href)
            if "canonical" in rel and href:
                self.page.canonicals.append(href)
            if "alternate" in rel and href and data.get("hreflang"):
                self.page.alternates[data["hreflang"] or ""] = href
        elif tag == "script" and (data.get("type") or "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_buffer = []

        if data.get("href") and tag != "link":
            self.page.hrefs.append(data["href"] or "")
        if data.get("src"):
            self.page.srcs.append(data["src"] or "")
        if data.get("id"):
            self.page.ids.append(data["id"] or "")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            raw = "".join(self._json_buffer).strip()
            if raw:
                self.page.json_ld.append(json.loads(raw))
            self._in_json_ld = False
            self._json_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.page.title += data
        if self._in_json_ld:
            self._json_buffer.append(data)
        else:
            self.page.raw_text += " " + data


def flatten_json_ld(value: Any) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    if isinstance(value, dict):
        nodes.append(value)
        graph = value.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                nodes.extend(flatten_json_ld(item))
    elif isinstance(value, list):
        for item in value:
            nodes.extend(flatten_json_ld(item))
    return nodes


def parse_pages(errors: list[str]) -> dict[str, ParsedPage]:
    pages: dict[str, ParsedPage] = {}
    for filename in EXPECTED_PAGES:
        path = ROOT / filename
        if not path.exists():
            errors.append(f"Missing expected page: {filename}")
            continue
        try:
            parser = StaticPageParser(path)
            parser.feed(path.read_text(encoding="utf-8"))
            parser.close()
            pages[filename] = parser.page
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Could not parse {filename}: {exc}")
    return pages


def validate_page_basics(pages: dict[str, ParsedPage], errors: list[str]) -> None:
    for filename, page in pages.items():
        expected_lang = "en" if filename.endswith("_en.html") or filename in {
            "fractional-cto-advisory.html",
            "executive-technology-advisor.html",
            "ai-visibility-and-governance.html",
            "digital-transformation-office.html",
            "digital-transformation-consultant.html",
            "geo-ai-visibility-guide.html",
        } else "tr"
        if not page.lang or not page.lang.lower().startswith(expected_lang):
            errors.append(f"{filename}: expected html lang starting with {expected_lang!r}, got {page.lang!r}")
        if not page.title.strip():
            errors.append(f"{filename}: missing title")
        if len(page.descriptions) != 1 or not page.descriptions[0].strip():
            errors.append(f"{filename}: expected exactly one non-empty meta description")
        if page.canonicals != [EXPECTED_PAGES[filename]]:
            errors.append(f"{filename}: canonical mismatch: {page.canonicals!r}")
        if len(page.ids) != len(set(page.ids)):
            errors.append(f"{filename}: duplicate HTML id values")
        if not page.json_ld:
            errors.append(f"{filename}: missing JSON-LD")

        for block in page.json_ld:
            for node in flatten_json_ld(block):
                if node.get("@type") == "FAQPage":
                    entities = node.get("mainEntity", [])
                    if not isinstance(entities, list):
                        errors.append(f"{filename}: FAQPage mainEntity must be a list")
                        continue
                    for entity in entities:
                        question = entity.get("name") if isinstance(entity, dict) else None
                        if question and question not in page.raw_text:
                            errors.append(f"{filename}: FAQ question is not visible in page text: {question}")


def validate_language_pairs(pages: dict[str, ParsedPage], errors: list[str]) -> None:
    for tr_file, en_file in LANGUAGE_PAIRS:
        if tr_file not in pages or en_file not in pages:
            continue
        tr_page, en_page = pages[tr_file], pages[en_file]
        tr_url, en_url = EXPECTED_PAGES[tr_file], EXPECTED_PAGES[en_file]
        for filename, page in ((tr_file, tr_page), (en_file, en_page)):
            if page.alternates.get("tr-TR") != tr_url:
                errors.append(f"{filename}: incorrect or missing tr-TR hreflang")
            if page.alternates.get("en") != en_url:
                errors.append(f"{filename}: incorrect or missing en hreflang")
            if "x-default" not in page.alternates:
                errors.append(f"{filename}: missing x-default hreflang")


def resolve_local_reference(source: str, reference: str) -> tuple[Path, str | None] | None:
    reference = reference.strip()
    if not reference or reference.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
        return None
    parsed = urllib.parse.urlsplit(reference)
    path_part = urllib.parse.unquote(parsed.path)
    fragment = urllib.parse.unquote(parsed.fragment) or None
    if not path_part:
        target = ROOT / source
    elif path_part.startswith("/"):
        target = ROOT / path_part.lstrip("/")
    else:
        target = (ROOT / source).parent / path_part
    if path_part.endswith("/"):
        target = target / "index.html"
    return target.resolve(), fragment


def validate_internal_links(pages: dict[str, ParsedPage], errors: list[str]) -> None:
    by_path = {page.path.resolve(): page for page in pages.values()}
    for filename, page in pages.items():
        for reference in page.hrefs + page.srcs:
            resolved = resolve_local_reference(filename, reference)
            if resolved is None:
                continue
            target, fragment = resolved
            if not target.exists():
                errors.append(f"{filename}: broken local reference {reference!r}")
                continue
            if fragment and target.suffix.lower() == ".html":
                target_page = by_path.get(target)
                if target_page is not None and fragment not in target_page.ids:
                    errors.append(f"{filename}: missing fragment #{fragment} in {target.name}")


def validate_supporting_files(errors: list[str]) -> None:
    css = ROOT / "assets/site.css"
    if not css.exists():
        errors.append("Missing assets/site.css")
    else:
        text = css.read_text(encoding="utf-8")
        if text.count("{") != text.count("}"):
            errors.append("assets/site.css: unbalanced braces")

    try:
        sitemap_root = ET.parse(ROOT / "sitemap.xml").getroot()
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {node.text for node in sitemap_root.findall("sm:url/sm:loc", namespace)}
        missing = sorted(set(EXPECTED_PAGES.values()) - locations)
        if missing:
            errors.append("sitemap.xml missing URLs: " + ", ".join(missing))
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml is invalid: {exc}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {BASE_URL}/sitemap.xml" not in robots:
        errors.append("robots.txt: sitemap declaration is missing or incorrect")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    service_urls = {
        EXPECTED_PAGES[name]
        for name in EXPECTED_PAGES
        if name in {
            "fractional-cto-danismanligi.html",
            "fractional-cto-advisory.html",
            "yonetici-teknoloji-danismanligi.html",
            "executive-technology-advisor.html",
            "yapay-zeka-gorunurlugu-ve-yonetisimi.html",
            "ai-visibility-and-governance.html",
            "dijital-donusum-ofisi.html",
            "digital-transformation-office.html",
        }
    }
    for url in sorted(service_urls):
        if url not in llms:
            errors.append(f"llms.txt missing service URL: {url}")


def validate_known_regressions(errors: list[str]) -> None:
    english_home = (ROOT / "index_en.html").read_text(encoding="utf-8")
    for bad_text in ("Contacte Geç", "Experiencei İncele", "Hakkımda", "Birlikte çalışalım"):
        if bad_text in english_home:
            errors.append(f"index_en.html contains mixed-language regression: {bad_text!r}")


def main() -> int:
    errors: list[str] = []
    pages = parse_pages(errors)
    validate_page_basics(pages, errors)
    validate_language_pairs(pages, errors)
    validate_internal_links(pages, errors)
    validate_supporting_files(errors)
    validate_known_regressions(errors)

    if errors:
        print("Site validation failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Site validation passed for {len(pages)} expected HTML pages.")
    print("JSON-LD, canonical URLs, hreflang pairs, local links, sitemap and support files are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
