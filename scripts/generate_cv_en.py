#!/usr/bin/env python3
"""Generate the four-page English CV PDF used by cagricakir.com.tr."""

from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "cagricakir_cv_en.pdf"

PAGE_W, PAGE_H = A4
LEFT = 62
RIGHT = 533
CONTENT_W = RIGHT - LEFT

BLACK = HexColor("#111111")
DARK_GREY = HexColor("#5E5E5E")
MID_GREY = HexColor("#A8A8A8")
LIGHT_GREY = HexColor("#D8D8D8")


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("Arial", font_dir / "Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", font_dir / "Arial Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Italic", font_dir / "Arial Italic.ttf"))


def split_lines(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if pdfmetrics.stringWidth(candidate, font, size) <= width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def paragraph(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    font: str = "Arial",
    size: float = 8.8,
    leading: float = 12.0,
    color: Color = DARK_GREY,
) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    for line in split_lines(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def rule(c: canvas.Canvas, y: float, color: Color = LIGHT_GREY, width: float = 0.45) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(LEFT, y, RIGHT, y)


def section_heading(c: canvas.Canvas, title: str, y: float) -> float:
    c.setFillColor(MID_GREY)
    c.setFont("Arial-Bold", 7.2)
    c.drawString(LEFT, y, title.upper())
    c.setStrokeColor(BLACK)
    c.setLineWidth(0.8)
    c.line(LEFT, y - 8, RIGHT, y - 8)
    return y - 24


def experience_row(
    c: canvas.Canvas,
    y: float,
    date: str,
    title: str,
    organisation: str,
    description: str,
    tags: str,
    row_height: float,
) -> float:
    body_x = 174
    body_w = RIGHT - body_x
    c.setFillColor(MID_GREY)
    c.setFont("Arial", 8.0)
    date_y = y
    for date_line in date.split("\n"):
        c.drawString(LEFT, date_y, date_line)
        date_y -= 11

    c.setFillColor(BLACK)
    c.setFont("Arial-Bold", 10.3)
    title_y = y
    for line in split_lines(title, "Arial-Bold", 10.3, body_w):
        c.drawString(body_x, title_y, line)
        title_y -= 11.2

    org_y = title_y - 0.5
    org_y = paragraph(c, organisation, body_x, org_y, body_w, size=8.4, leading=10.5)
    desc_y = paragraph(c, description, body_x, org_y - 3, body_w, size=8.7, leading=11.6)
    paragraph(c, tags, body_x, desc_y - 1.5, body_w, font="Arial-Italic", size=7.8, leading=10, color=MID_GREY)

    bottom = y - row_height
    rule(c, bottom)
    return bottom - 10


def appendix_item(
    c: canvas.Canvas,
    y: float,
    title: str,
    organisation: str,
    description: str,
    tags: str,
    gap: float = 7,
) -> float:
    c.setFillColor(BLACK)
    c.setFont("Arial-Bold", 9.3)
    c.drawString(LEFT, y, title)
    y -= 11
    y = paragraph(c, organisation, LEFT, y, CONTENT_W, size=7.9, leading=10)
    y = paragraph(c, description, LEFT, y - 1.5, CONTENT_W, size=8.2, leading=10.8)
    y = paragraph(c, tags, LEFT, y - 1, CONTENT_W, font="Arial-Italic", size=7.6, leading=9.4, color=MID_GREY)
    rule(c, y - 2)
    return y - gap


def draw_header(c: canvas.Canvas) -> None:
    c.setFillColor(BLACK)
    c.setFont("Arial-Bold", 27)
    c.drawString(LEFT, 773, "Sabri Çağrı Çakır")
    c.setFillColor(DARK_GREY)
    c.setFont("Arial", 9.4)
    c.drawString(LEFT, 752, "Chief Technology Officer · Board Member · Strategic Advisor")
    c.setFont("Arial", 8.1)
    c.drawString(
        LEFT,
        735,
        "Ankara, Türkiye · mail@cagricakir.com.tr · linkedin.com/in/scagricakir · cagricakir.com.tr",
    )
    c.setStrokeColor(BLACK)
    c.setLineWidth(1.1)
    c.line(LEFT, 722, RIGHT, 722)

    stats = [
        ("25", "Years of industry experience"),
        ("160+", "Completed projects"),
        ("1M+", "Platform users"),
        ("5", "Academic degrees"),
    ]
    cell_w = CONTENT_W / 4
    for index, (value, label) in enumerate(stats):
        cx = LEFT + cell_w * index + cell_w / 2
        c.setFillColor(BLACK)
        c.setFont("Arial-Bold", 22)
        c.drawCentredString(cx, 689, value)
        c.setFillColor(DARK_GREY)
        label_size = 7.1 if index == 0 else 7.5
        c.setFont("Arial", label_size)
        c.drawCentredString(cx, 673, label)
        if index < 3:
            c.setStrokeColor(LIGHT_GREY)
            c.setLineWidth(0.45)
            c.line(LEFT + cell_w * (index + 1), 665, LEFT + cell_w * (index + 1), 715)
    rule(c, 655)


def page_one(c: canvas.Canvas) -> None:
    draw_header(c)

    y = section_heading(c, "About", 624)
    about = (
        "As a CTO, Board Member and R&D leader, I bring 25 years of industry experience and 15+ years "
        "in leadership, managing technology organisations, building digital transformation architectures "
        "and helping organisations prepare for the future. Across more than 160 projects spanning defence "
        "to healthcare, I have treated technology as a tool and people as the centre of every decision. "
        "This people-first leadership approach contributed to Great Place to Work® certification for the "
        "organisation where I served."
    )
    y = paragraph(c, about, LEFT, y, CONTENT_W, size=8.8, leading=12.0)

    y = section_heading(c, "Experience", y - 25)
    y = experience_row(
        c,
        y,
        "2026 — Present",
        "Corporate Technology Investor & Strategic Advisor",
        "geoni.ai · Generative Engine Optimization · Ankara",
        "Invested in geoni.ai as a corporate technology investor and strategic advisor. The platform helps brands be accurately and visibly represented by AI search engines such as ChatGPT, Perplexity, Claude and Gemini.",
        "Generative Engine Optimization · AI Visibility · Venture Investment · Strategic Advisory",
        93,
    )
    y = experience_row(
        c,
        y,
        "Jan 2025 — Apr 2026",
        "Strategic Technology & Management Advisor and Board Member",
        "Lunadenta Teknoloji Bilişim Arge AŞ · Full-time · Ankara",
        "Advised on strategic technology planning, digital transformation, R&D management and organisational restructuring, guiding a technology-led growth agenda through an ecosystem-based management model.",
        "Strategic Advisory · Digital Transformation · R&D Management · Corporate Governance",
        90,
    )
    y = experience_row(
        c,
        y,
        "Jun 2024 — Dec 2024 /\nJan 2024 — Dec 2024",
        "Board Member",
        "ARDVENTURE · Full-time · Ankara",
        "Board Member of a Venture Capital Investment Trust (GSYO) and Board Member of a Crowdfunding Platform company.",
        "Venture Capital · Crowdfunding · Investment Strategy · Corporate Governance",
        71,
    )
    experience_row(
        c,
        y,
        "Mar 2019 — Dec 2024",
        "Board Member",
        "ARD Grup Bilişim Teknolojileri A.Ş. · BIST: ARDYZ · Ankara",
        "Held corporate responsibility in public-company governance and served on the Early Detection of Risk Committee. Played a key role in the IPO and the company’s move to BIST Star Market, coordinating CMB compliance and corporate auditability.",
        "Corporate Governance · Technology Roadmap · IT Strategy · Risk Management · IPO",
        90,
    )


def page_two(c: canvas.Canvas) -> None:
    y = 783
    y = experience_row(
        c,
        y,
        "Jan 2017 — Nov 2022",
        "Chief Technology Officer (CTO)",
        "ARD Grup Bilişim Teknolojileri A.Ş. · Ankara",
        "Designed the technical architecture of e-Invoice, e-Archive and e-Ledger platforms serving more than 50,000 taxpayer customers. Led 160+ projects across the public sector, defence, healthcare and cybersecurity, including critical infrastructure work under a NATO Facility Security Clearance.",
        "e-Transformation · Cybersecurity · IT Infrastructure · Video Analytics · Virtualisation · SDLC · ITEA",
        91,
    )
    y = experience_row(
        c,
        y,
        "Feb 2017 — May 2022",
        "Chief Research Officer (CRO)",
        "ARD Grup Bilişim Teknolojileri A.Ş. · Ankara",
        "Managed international and national R&D incentive projects and coordinated multi-stakeholder programmes under ITEA, TÜBİTAK and Celtic.",
        "R&D Management · ITEA · TÜBİTAK · Celtic · International Project Management",
        72,
    )
    y = experience_row(
        c,
        y,
        "Jan 2010 — Feb 2017",
        "Director",
        "ARD Grup Bilişim Teknolojileri A.Ş. · Ankara",
        "First major leadership role in a 15-year career at ARD Group, managing technology operations and contributing to corporate growth.",
        "Technology Management · Project Management · Business Development · Process Improvement",
        68,
    )

    y = section_heading(c, "Academic Background", y - 14)
    col_w = CONTENT_W / 2
    rows = [
        (
            ("PhD", "Management Information Systems", "Distance Learning · 2024"),
            ("Master’s Degree", "Industrial & Organisational Psychology", "Distance Learning · 2020"),
        ),
        (
            ("Master’s Degree — MCA", "Management Information Systems", "Ahmet Yesevi University · 2016–2018"),
            ("Bachelor’s Degree", "Business Administration", "Anadolu University · 2006–2010"),
        ),
        (
            ("Bachelor’s Degree", "Physics", "Dokuz Eylül University · 2000–2004"),
            None,
        ),
    ]
    row_h = 48
    for left_item, right_item in rows:
        for idx, item in enumerate((left_item, right_item)):
            if item is None:
                continue
            x = LEFT + idx * col_w
            c.setFillColor(MID_GREY)
            c.setFont("Arial", 7.1)
            c.drawString(x, y, item[0])
            c.setFillColor(BLACK)
            c.setFont("Arial-Bold", 9.6)
            c.drawString(x, y - 12, item[1])
            c.setFillColor(DARK_GREY)
            c.setFont("Arial", 8.1)
            c.drawString(x, y - 23, item[2])
        rule(c, y - 31)
        c.setStrokeColor(LIGHT_GREY)
        c.setLineWidth(0.45)
        c.line(LEFT + col_w, y + 5, LEFT + col_w, y - 31)
        y -= row_h

    y = section_heading(c, "Core Competencies", y - 4)
    label_w = 128
    competencies = [
        ("TECHNOLOGY LEADERSHIP & STRATEGY", "Digital Transformation · Technology Roadmaps · IT Strategy · Resilient & Sustainable Critical-System Design · Interim Management · Investment Strategy"),
        ("SOFTWARE DEVELOPMENT & ARCHITECTURE", "Software Architecture · Enterprise Software · SDLC · Software Project Management · Systems Integration · e-Transformation Platforms"),
        ("INFRASTRUCTURE & CLOUD", "Cloud Computing · Virtualisation · Server & Storage Management · Backup & Disaster Recovery · SDN · VPN"),
        ("CYBERSECURITY & AI", "Cybersecurity · Network Security · High-Security Systems · Video Analytics · AI-Enabled Software"),
        ("PROJECT & PROGRAMME MANAGEMENT", "Project Management · Programme Management · International Project Management · Change Management · Process Improvement"),
        ("R&D & BUSINESS ANALYSIS", "R&D Management · ITEA & TÜBİTAK Projects · Business Analysis · Data Analytics · Business Intelligence · Business Development"),
    ]
    for label, text in competencies:
        lines = split_lines(text, "Arial", 8.0, CONTENT_W - label_w - 10)
        row_h = max(31, len(lines) * 10 + 10)
        c.setFillColor(MID_GREY)
        c.setFont("Arial", 6.5)
        for idx, line in enumerate(split_lines(label, "Arial", 6.5, label_w - 8)):
            c.drawString(LEFT, y - idx * 8, line)
        text_y = y
        c.setFillColor(DARK_GREY)
        c.setFont("Arial", 8.0)
        for line in lines:
            c.drawString(LEFT + label_w + 10, text_y, line)
            text_y -= 10
        c.setStrokeColor(LIGHT_GREY)
        c.setLineWidth(0.45)
        c.line(LEFT + label_w, y + 7, LEFT + label_w, y - row_h + 7)
        rule(c, y - row_h + 7)
        y -= row_h


def appendix_header(c: canvas.Canvas) -> float:
    c.setFillColor(BLACK)
    c.setFont("Arial-Bold", 18)
    c.drawString(LEFT, 775, "Sabri Çağrı Çakır")
    c.setFillColor(DARK_GREY)
    c.setFont("Arial", 9.4)
    c.drawString(LEFT, 758, "Projects & Achievements Appendix · ARD Grup Bilişim Teknolojileri A.Ş. (2010–2025)")
    c.setStrokeColor(BLACK)
    c.setLineWidth(1.0)
    c.line(LEFT, 746, RIGHT, 746)
    return 718


def page_three(c: canvas.Canvas) -> None:
    y = appendix_header(c)
    y = section_heading(c, "Legal & Justice IT", y)
    y = appendix_item(
        c,
        y,
        "National Legal Network Project (UHAP)",
        "Union of Turkish Bar Associations & All Bar Associations · UYAP Integration",
        "The private sector’s most comprehensive judicial software project, serving bar associations, Police Departments, Public Prosecutors’ Offices and Courts across Türkiye. Fully integrated with the UYAP system.",
        "UHAP · UYAP · Ministry of Justice · Legal Technology",
    )
    y = appendix_item(
        c,
        y,
        "Bar Association and Law Office Software Suite",
        "Union of Turkish Bar Associations",
        "A comprehensive legal-software ecosystem including BAROTEK (Bar Association Management), BÜROTEK (Law Office Management), İCRATEK (Enforcement Proceedings), KARARTEK (Case Law Search), the Hearing Tracking System and OCAS (Automated Lawyer Assignment).",
        "BAROTEK · BÜROTEK · İCRATEK · KARARTEK · OCAS",
    )

    y = section_heading(c, "Healthcare IT", y - 17)
    y = appendix_item(
        c,
        y,
        "University Hospital Health Information Systems",
        "Hacettepe University · Akdeniz University Faculty of Medicine · Association of Public Hospitals",
        "Hospital information-system solutions covering General Surgery, Pharmaceutical Toxicology, Internal Medicine and other clinical units, including smart operating-theatre and laboratory systems.",
        "Healthcare IT · HIS · Smart Operating Theatre · Laboratory Management",
    )

    y = section_heading(c, "Artificial Intelligence & Security Technologies", y - 17)
    y = appendix_item(
        c,
        y,
        "FOLLOWINO — AI-Based Pandemic Prevention System",
        "Public Institutions & Private Sector · 2020",
        "Developed during COVID-19 with deep-learning modules for people counting, occupancy analysis, person identification, thermal temperature screening and mask detection. The world’s first TÜV-certified pandemic prevention and social-distancing control system.",
        "Artificial Intelligence · Deep Learning · Video Analytics · TÜV Certification · COVID-19",
    )
    y = appendix_item(
        c,
        y,
        "Ministry of National Defence — 4th Main Maintenance Factory Directorate",
        "Ministry of National Defence · 2022",
        "An information-technology project for defence-industry infrastructure, delivered under NATO Facility Security Clearance and National Classified Facility Security Clearance requirements.",
        "Defence Technologies · NATO · Classified Project · IT Infrastructure",
    )
    y = appendix_item(
        c,
        y,
        "AI-Enabled Proactive Security Systems",
        "Strategic Partnership with Dallmeier Electronic GmbH · 2022",
        "AI-enabled proactive security solutions for border, airport and port environments, developed through a strategic partnership with German technology company Dallmeier.",
        "Video Analytics · Border Security · Airport Security · Port Security",
    )
    y = appendix_item(
        c,
        y,
        "Turkish National Police IT Projects",
        "General Directorate of Security",
        "Software development and systems-integration projects for national police units.",
        "Public Safety · Systems Integration",
    )
    section_heading(c, "e-Transformation & Public-Sector IT", y - 16)


def page_four(c: canvas.Canvas) -> None:
    y = 783
    y = appendix_item(
        c,
        y,
        "e-Transformation Platform",
        "Revenue Administration — Licensed Private Integrator",
        "Design, development and operation of e-Invoice, e-Archive and e-Ledger platforms serving more than 50,000 unique taxpayer customers, establishing the company as the sector’s private integrator with the largest customer base.",
        "e-Invoice · e-Archive · e-Ledger · Revenue Administration · Private Integrator · 50,000+ Users",
    )
    y = appendix_item(
        c,
        y,
        "Distance Learning Systems (DLS/LMS) & Smart Classroom Solutions",
        "Public Institutions & Universities",
        "Distance-learning systems (DLS and LMS), smart-classroom solutions and intelligent video-conferencing and meeting-room systems for public- and private-sector organisations.",
        "LMS · DLS · Distance Learning · Smart Classroom · Video Conferencing",
    )
    y = appendix_item(
        c,
        y,
        "Traffic Management Systems (TEDES, EDS, KGYS)",
        "Public Institutions",
        "Smart-city infrastructure including electronic enforcement, traffic enforcement and urban security management systems.",
        "TEDES · EDS · KGYS · Smart City · Traffic Management",
    )

    y = section_heading(c, "International R&D Projects", y - 18)
    y = appendix_item(
        c,
        y,
        "ITEA International R&D Programmes",
        "ITEA (Information Technology for European Advancement) · EU-Supported",
        "Projects delivered with international consortia under one of Europe’s leading R&D programmes for software-intensive systems, including technical and administrative coordination.",
        "ITEA · EU · International Consortium · Software R&D",
    )
    y = appendix_item(
        c,
        y,
        "TÜBİTAK R&D Projects",
        "TÜBİTAK — Scientific and Technological Research Council of Türkiye",
        "Software and technology-development projects delivered under national R&D incentive programmes.",
        "TÜBİTAK · National R&D · Technology Transfer",
    )
    y = appendix_item(
        c,
        y,
        "Celtic R&D Programme",
        "Celtic-Next (EUREKA Cluster) · Europe",
        "Collaborative European R&D projects in telecommunications and information technology.",
        "Celtic · EUREKA · Telecommunications · R&D",
    )

    note = (
        "Note: Due to space constraints, this document presents a representative selection from 15 years of corporate work rather than the full portfolio. "
        "A complete project list and references are available on request. This appendix was compiled from Public Disclosure Platform (KAP) filings and publicly available company sources. "
        "cagricakir.com.tr · mail@cagricakir.com.tr"
    )
    rule(c, y - 8)
    paragraph(c, note, LEFT, y - 20, CONTENT_W, size=7.1, leading=9.2, color=MID_GREY)


def generate() -> None:
    register_fonts()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Sabri Çağrı Çakır — Curriculum Vitae")
    c.setAuthor("Sabri Çağrı Çakır")
    c.setSubject("English curriculum vitae and selected projects")
    c.setCreator("cagricakir.com.tr")

    page_one(c)
    c.showPage()
    page_two(c)
    c.showPage()
    page_three(c)
    c.showPage()
    page_four(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    generate()
