#!/usr/bin/env python3
"""Generates the SEO head of every page, plus sitemap.xml.

Run from src/docs/asciidoc:  python3 ../seo/generate-docinfo.py

Asciidoctor picks up docinfo.html (shared, every page in the directory) and
<docname>-docinfo.html (private, that page only) and injects both into <head>.
Keeping them generated from this one table is what stops the descriptions,
canonicals, structured data and sitemap entries from drifting apart across
root/v1/v2 - a sitemap that lists a URL whose canonical points elsewhere is
what makes Search Console report the page as a duplicate.
"""

import datetime
import json
import pathlib
import subprocess

SITE = "https://springdoc.org"
OG_IMAGE = f"{SITE}/img/og-springdoc.png"
GA_ID = "G-1GEGWXWNH4"
ADS_CLIENT = "ca-pub-8127371937306964"

# page -> (title used in og:title and breadcrumbs, meta description)
PAGES = {
    "index": (
        "springdoc-openapi",
        "springdoc-openapi generates OpenAPI 3 documentation and serves Swagger UI for Spring "
        "Boot applications automatically, from your controllers, annotations and constraints.",
    ),
    "intro": (
        "Introduction",
        "What springdoc-openapi is and how it infers OpenAPI 3 API semantics at runtime from "
        "your Spring Boot configuration, class structure and annotations.",
    ),
    "getting-started": (
        "Getting Started",
        "Add springdoc-openapi to a Spring Boot project with one Maven or Gradle dependency and "
        "get /v3/api-docs and Swagger UI with no extra configuration.",
    ),
    "modules": (
        "Modules",
        "The springdoc-openapi starters and modules for Spring WebMvc, WebFlux, Cloud Function, "
        "Hateoas, Data REST, Security, Kotlin and GraalVM native images.",
    ),
    "features": (
        "Features",
        "springdoc-openapi features: API info and security schemes, @ControllerAdvice error "
        "handling, grouped OpenAPI definitions, Javadoc support and Swagger UI customisation.",
    ),
    "mcp": (
        "MCP Support",
        "Expose documented Spring @RestController endpoints as Model Context Protocol tools for "
        "Claude, Cursor and other AI agents, using springdoc-openapi and Spring AI.",
    ),
    "properties": (
        "Configuration Properties",
        "Complete reference of springdoc.* configuration properties for Spring Boot: OpenAPI "
        "generation, groups, caching and every supported Swagger UI setting.",
    ),
    "core-properties": (
        "Core Properties Reference",
        "Reference table of every springdoc.* core property: api-docs paths, packages and paths "
        "to scan, caching, model converters and MCP settings, with defaults.",
    ),
    "ui-properties": (
        "Swagger UI Properties Reference",
        "Reference table of every springdoc.swagger-ui.* property: path, layout, try-it-out, "
        "filtering, operation sorting, OAuth settings and display options.",
    ),
    "plugins": (
        "Maven and Gradle Plugins",
        "Generate OpenAPI JSON and YAML descriptions at build time with the springdoc-openapi "
        "Maven and Gradle plugins during the integration-test phase.",
    ),
    "demos": (
        "Live Demos",
        "Live Swagger UI and Scalar demos of springdoc-openapi running on Spring Boot Web MVC, "
        "WebFlux, functional endpoints, Hateoas and Spring Cloud Function.",
    ),
    "migrating-from-springfox": (
        "Migrating from SpringFox",
        "Step-by-step guide to replacing SpringFox and Swagger 2 with springdoc-openapi: "
        "dependency changes and the annotation mapping between the two libraries.",
    ),
    "migrating-from-springdoc-v1": (
        "Migrating from v1",
        "How to upgrade from springdoc-openapi v1: renamed starters, the new package layout and "
        "the Spring Boot 3 and Jakarta EE changes to expect.",
    ),
    "other-resources": (
        "Resources and Tutorials",
        "Tutorials, articles and community resources about springdoc-openapi, including "
        "Baeldung, DZone and conference presentations.",
    ),
    "faq": (
        "FAQ",
        "Answers to common springdoc-openapi questions: multiple OpenAPI groups, custom Swagger "
        "UI paths, security schemes, sorting, reverse proxies and Spring Security.",
    ),
    "sponsor": (
        "Sponsor",
        "Support springdoc-openapi through Open Collective or GitHub Sponsors, and see the "
        "benefits of the bronze, silver and gold sponsorship tiers.",
    ),
    "thanks": (
        "Special Thanks",
        "Acknowledgements for the people, companies and tools that support the springdoc-openapi "
        "project.",
    ),
    "privacy-policy": (
        "Privacy Policy",
        "Privacy policy for springdoc.org, covering the analytics and advertising cookies used "
        "on the site.",
    ),
}

# the pages that actually render an <ins class="adsbygoogle"> slot, per version directory
AD_PAGES = {
    "": {"index", "getting-started", "features", "mcp", "demos", "ui-properties", "properties"},
    "v1": set(),
    "v2": {"index", "getting-started", "features", "demos", "ui-properties", "properties"},
}

VERSIONS = {
    "":   {"label": "", "prefix": "", "boot": "Spring Boot 4", "version": "3",
           "priority": ("1.0", "0.8")},
    "v1": {"label": " (v1)", "prefix": "springdoc-openapi v1 docs (Spring Boot 2.x). ",
           "boot": "Spring Boot 2", "version": "1", "priority": ("0.3", "0.2")},
    "v2": {"label": " (v2)", "prefix": "springdoc-openapi v2 docs (Spring Boot 3.x). ",
           "boot": "Spring Boot 3", "version": "2", "priority": ("0.5", "0.4")},
}

# pages that do not exist in a given version directory
SKIP = {
    "":   {"privacy-policy"},
    "v1": {"mcp", "migrating-from-springdoc-v1"},
    "v2": {"mcp", "privacy-policy"},
}

# Versioned pages whose text is a near-verbatim copy of the root page - only the title suffix and
# the "you are reading the v1/v2 docs" banner differ. A self-referencing canonical on those makes
# Search Console report "Duplicate, Google chose a different canonical than the user", because
# Google folds them into the root page anyway. Pointing the canonical at the root URL states the
# same choice explicitly. Pages that carry version-specific content (index, getting-started,
# modules, features, demos and the property tables) keep their own canonical and stay indexable.
DUPLICATE_OF_ROOT = {
    "":   set(),
    "v1": {"intro", "migrating-from-springfox", "other-resources", "plugins", "sponsor",
           "thanks", "ui-properties"},
    "v2": {"faq", "intro", "migrating-from-springdoc-v1", "migrating-from-springfox",
           "other-resources", "plugins", "sponsor", "thanks", "ui-properties"},
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def shared_docinfo(ver):
    """docinfo.html - injected into the <head> of every page in the directory."""
    root = f"{SITE}/{ver}" if ver else SITE
    return f"""<style>
    #header #revnumber {{
        display: none
    }}
    /* reserve the ad slot so filling it cannot push the article down */
    ins.adsbygoogle {{ min-height: 280px }}
</style>

<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="theme-color" content="#6db33f">
<link rel="icon" href="{root}/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="{root}/img/springdoc/springdoc-favicon.svg">

<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="springdoc-openapi">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="springdoc-openapi - OpenAPI 3 and Swagger UI for Spring Boot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{OG_IMAGE}">

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{GA_ID}');
</script>
"""


def page_docinfo(ver, page, title, description):
    meta = VERSIONS[ver]
    root = f"{SITE}/{ver}" if ver else SITE
    # a duplicate of the root page indexes as the root page, so every URL it declares is that one
    duplicate = page in DUPLICATE_OF_ROOT[ver]
    home = SITE if duplicate else root
    url = home + "/" if page == "index" else f"{home}/{page}.html"
    og_title = ("springdoc-openapi - OpenAPI 3 & Swagger UI for Spring Boot"
                if page == "index" else f"{title} - springdoc-openapi") + meta["label"]
    desc = meta["prefix"] + description

    out = [f'<meta name="description" content="{esc(desc)}">',
           f'<link rel="canonical" href="{url}">',
           f'<meta property="og:title" content="{esc(og_title)}">',
           f'<meta property="og:description" content="{esc(desc)}">',
           f'<meta property="og:url" content="{url}">',
           f'<meta name="twitter:title" content="{esc(og_title)}">',
           f'<meta name="twitter:description" content="{esc(desc)}">',
           ""]

    if page == "index":
        out.append(ld({
            "@context": "https://schema.org",
            "@type": "SoftwareSourceCode",
            "name": "springdoc-openapi",
            "description": desc,
            "url": url,
            "codeRepository": "https://github.com/springdoc/springdoc-openapi",
            "programmingLanguage": "Java",
            "runtimePlatform": meta["boot"],
            "license": "https://www.apache.org/licenses/LICENSE-2.0",
            "author": {"@type": "Organization", "name": "springdoc",
                       "url": "https://github.com/springdoc"},
        }))
        if not ver:
            out.append(ld({
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": "springdoc-openapi",
                "url": SITE + "/",
            }))
    else:
        out.append(ld({
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": og_title,
            "description": desc,
            "url": url,
            "inLanguage": "en",
            "isPartOf": {"@type": "WebSite", "name": "springdoc-openapi", "url": SITE + "/"},
            "author": {"@type": "Organization", "name": "springdoc",
                       "url": "https://github.com/springdoc"},
        }))
        crumbs = [{"@type": "ListItem", "position": 1, "name": "springdoc-openapi",
                   "item": SITE + "/"}]
        if ver and not duplicate:
            crumbs.append({"@type": "ListItem", "position": 2, "name": f"v{meta['version']}",
                           "item": f"{root}/"})
        crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": title,
                       "item": url})
        out.append(ld({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": crumbs}))

    if page in AD_PAGES[ver]:
        out.append(
            "<!-- Loaded once per page here; the article body only carries the <ins> slots. -->\n"
            f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={ADS_CLIENT}" crossorigin="anonymous"></script>\n')

    return "\n".join(out)


def last_modified(path):
    """Date of the last commit that touched the source file, for <lastmod>."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        out = ""
    return out or datetime.date.today().isoformat()


def sitemap(base):
    """sitemap.xml - canonical URLs only, so it never advertises a page as its own original."""
    entries = []
    for ver in VERSIONS:
        d = base / ver if ver else base
        root = f"{SITE}/{ver}" if ver else SITE
        home, inner = VERSIONS[ver]["priority"]
        for page in PAGES:
            src = d / f"{page}.adoc"
            if page in SKIP[ver] or page in DUPLICATE_OF_ROOT[ver] or not src.exists():
                continue
            loc = f"{root}/" if page == "index" else f"{root}/{page}.html"
            entries.append(f"\t<url>\n\t\t<loc>{loc}</loc>\n"
                           f"\t\t<lastmod>{last_modified(src)}</lastmod>\n"
                           f"\t\t<priority>{home if page == 'index' else inner}</priority>\n"
                           "\t</url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(entries) + "\n</urlset>\n")


def main():
    base = pathlib.Path(".")
    for ver in VERSIONS:
        d = base / ver if ver else base
        (d / "docinfo.html").write_text(shared_docinfo(ver), encoding="utf-8")
        print("wrote", d / "docinfo.html")
        for page, (title, description) in PAGES.items():
            if page in SKIP[ver] or not (d / f"{page}.adoc").exists():
                continue
            target = d / f"{page}-docinfo.html"
            target.write_text(page_docinfo(ver, page, title, description), encoding="utf-8")
            print("wrote", target)
    (base / "sitemap.xml").write_text(sitemap(base), encoding="utf-8")
    print("wrote", base / "sitemap.xml")


if __name__ == "__main__":
    main()
