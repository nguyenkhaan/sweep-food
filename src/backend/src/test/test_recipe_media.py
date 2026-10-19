"""Tests for recipe media building, scraping, URL validation, and step normalization."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from AI.catalog.media_builder import (
    clean_url,
    extract_image_from_html,
    normalize_step,
    normalize_steps,
    parse_args,
    validate_image_url,
)


def test_clean_url_edge_cases() -> None:
    """clean_url sanitizes whitespace, entities, resolves paths, and enforces HTTPS."""
    base = "https://example.com/recipes/dish-1"

    # None, empty, or non-string inputs
    assert clean_url(None, base) is None
    assert clean_url("", base) is None
    assert clean_url("   ", base) is None

    # HTML entity unescaping and whitespace stripping
    raw_with_entities = "  https://example.com/img.jpg?a=1&amp;b=2  "
    assert clean_url(raw_with_entities, base) == "https://example.com/img.jpg?a=1&b=2"

    # Relative paths
    assert clean_url("/images/food.jpg", base) == "https://example.com/images/food.jpg"
    assert clean_url("food.jpg", base) == "https://example.com/recipes/food.jpg"

    # Protocol upgrading from HTTP to HTTPS
    assert clean_url("http://cdn.example.com/pic.png", base) == "https://cdn.example.com/pic.png"

    # Non-HTTP(S) schemes rejected
    assert clean_url("ftp://example.com/pic.jpg", base) is None
    assert clean_url("javascript:void(0)", base) is None
    assert clean_url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUg", base) is None


def test_extract_image_json_ld_single_and_object() -> None:
    """extract_image_from_html extracts Recipe image from JSON-LD schemas."""
    # Single string image in Recipe JSON-LD
    html_single = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Recipe",
          "name": "Pho Bo",
          "image": "https://example.com/pho.jpg"
        }
        </script>
      </head>
    </html>
    """
    assert extract_image_from_html(html_single, "https://example.com") == "https://example.com/pho.jpg"

    # ImageObject with url
    html_object = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@type": "Recipe",
          "name": "Pho Bo",
          "image": {
            "@type": "ImageObject",
            "url": "https://example.com/pho-obj.jpg"
          }
        }
        </script>
      </head>
    </html>
    """
    assert extract_image_from_html(html_object, "https://example.com") == "https://example.com/pho-obj.jpg"

    # Array of images (prefers last/highest resolution)
    html_list = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@type": "Recipe",
          "image": [
            "https://example.com/pho-100.jpg",
            "https://example.com/pho-500.jpg",
            "https://example.com/pho-1000.jpg"
          ]
        }
        </script>
      </head>
    </html>
    """
    assert extract_image_from_html(html_list, "https://example.com") == "https://example.com/pho-1000.jpg"


def test_extract_image_json_ld_graph_and_meta_fallbacks() -> None:
    """extract_image_from_html handles @graph nodes and falls back to og:image and twitter:image."""
    # @graph node containing Recipe
    html_graph = """
    <html>
      <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@graph": [
          {"@type": "WebSite", "url": "https://example.com"},
          {"@type": "Recipe", "image": "https://example.com/graph-recipe.jpg"}
        ]
      }
      </script>
    </html>
    """
    assert extract_image_from_html(html_graph, "https://example.com") == "https://example.com/graph-recipe.jpg"

    # OpenGraph meta fallback when JSON-LD is absent
    html_og = """
    <html>
      <head>
        <meta property="og:image" content="https://example.com/og-image.jpg" />
      </head>
    </html>
    """
    assert extract_image_from_html(html_og, "https://example.com") == "https://example.com/og-image.jpg"

    # OpenGraph reversed attribute order (content before property)
    html_og_rev = """
    <html>
      <head>
        <meta content="https://example.com/og-rev.jpg" property="og:image" />
      </head>
    </html>
    """
    assert extract_image_from_html(html_og_rev, "https://example.com") == "https://example.com/og-rev.jpg"

    # Twitter meta fallback when JSON-LD and og:image are absent
    html_tw = """
    <html>
      <head>
        <meta name="twitter:image" content="https://example.com/twitter-image.jpg" />
      </head>
    </html>
    """
    assert extract_image_from_html(html_tw, "https://example.com") == "https://example.com/twitter-image.jpg"

    # Precedence: JSON-LD beats OpenGraph
    html_both = """
    <html>
      <head>
        <meta property="og:image" content="https://example.com/og-image.jpg" />
        <script type="application/ld+json">
        {"@type": "Recipe", "image": "https://example.com/jsonld-winner.jpg"}
        </script>
      </head>
    </html>
    """
    assert extract_image_from_html(html_both, "https://example.com") == "https://example.com/jsonld-winner.jpg"

    # Missing image
    assert extract_image_from_html("<html><body><p>No images</p></body></html>", "https://example.com") is None


def test_normalize_step_and_normalize_steps() -> None:
    """normalize_step structures step number, title, and content."""
    # Standard detailed step
    step1 = normalize_step({"step": 1, "title": "Sơ chế", "content": "Rửa sạch rau."}, 1)
    assert step1 == {"step": 1, "title": "Sơ chế", "content": "Rửa sạch rau."}

    # Step number as string and missing title
    step2 = normalize_step({"step": "2", "content": "Nấu nước dùng."}, 1)
    assert step2 == {"step": 2, "title": "", "content": "Nấu nước dùng."}

    # Fallback step number when invalid/missing
    step3 = normalize_step({"step": "not-a-number", "title": "Hoàn tất"}, 5)
    assert step3 == {"step": 5, "title": "Hoàn tất", "content": ""}

    # normalize_steps prefers detailed over raw
    detailed = [{"step": 1, "title": "Step A", "content": "Detailed text"}]
    raw = [{"step": 1, "title": "Raw Step", "content": "Raw text"}]
    chosen = normalize_steps(detailed, raw)
    assert len(chosen) == 1
    assert chosen[0]["title"] == "Step A"

    # Falls back to raw when detailed is empty
    chosen_raw = normalize_steps(None, raw)
    assert len(chosen_raw) == 1
    assert chosen_raw[0]["title"] == "Raw Step"

    # Empty when both are absent
    assert normalize_steps(None, None) == []


@pytest.mark.asyncio
async def test_validate_image_url_with_mock_transport() -> None:
    """validate_image_url verifies status 200/206 and image/* content type using MockTransport."""
    def handler(request: httpx.Request) -> httpx.Response:
        url_str = str(request.url)
        if url_str == "https://cdn.example.com/valid.jpg":
            return httpx.Response(200, headers={"content-type": "image/jpeg"}, content=b"\xff\xd8\xff")
        if url_str == "https://cdn.example.com/valid-partial.png":
            return httpx.Response(206, headers={"content-type": "image/png"}, content=b"\x89PNG")
        if url_str == "https://cdn.example.com/not-found.jpg":
            return httpx.Response(404, headers={"content-type": "text/html"}, content=b"Not found")
        if url_str == "https://cdn.example.com/html-page.jpg":
            return httpx.Response(200, headers={"content-type": "text/html; charset=utf-8"}, content=b"<html>")
        if url_str == "https://cdn.example.com/range-rejected.jpg":
            # Rejects Range header with 403, accepts GET without Range
            if "Range" in request.headers:
                return httpx.Response(403, headers={"content-type": "text/plain"}, content=b"Forbidden")
            return httpx.Response(200, headers={"content-type": "image/jpeg"}, content=b"image-data")
        if url_str == "https://cdn.example.com/forbidden.jpg":
            return httpx.Response(403, headers={"content-type": "text/plain"}, content=b"Forbidden")
        return httpx.Response(500, content=b"Server error")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        # Valid 200 image
        valid, reason = await validate_image_url(client, "https://cdn.example.com/valid.jpg")
        assert valid is True
        assert reason == "valid"

        # Valid 206 partial content image
        valid, reason = await validate_image_url(client, "https://cdn.example.com/valid-partial.png")
        assert valid is True
        assert reason == "valid"

        # 404 status
        valid, reason = await validate_image_url(client, "https://cdn.example.com/not-found.jpg")
        assert valid is False
        assert reason == "status_404"

        # 200 with invalid content type
        valid, reason = await validate_image_url(client, "https://cdn.example.com/html-page.jpg")
        assert valid is False
        assert reason == "invalid_content_type_text/html"

        # Range header rejected with 403, retried without Range -> succeeds
        valid, reason = await validate_image_url(client, "https://cdn.example.com/range-rejected.jpg")
        assert valid is True
        assert reason == "valid"

        # 403 on both Range and full GET
        valid, reason = await validate_image_url(client, "https://cdn.example.com/forbidden.jpg")
        assert valid is False
        assert reason == "status_403"


@pytest.mark.asyncio
async def test_validate_image_url_network_errors() -> None:
    """validate_image_url maps httpx network exceptions to structured failure reasons."""
    def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("Connection timed out", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler)) as client:
        valid, reason = await validate_image_url(client, "https://example.com/timeout.jpg")
        assert valid is False
        assert reason == "connect_timeout"

    def connect_error_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(connect_error_handler)) as client:
        valid, reason = await validate_image_url(client, "https://example.com/error.jpg")
        assert valid is False
        assert reason == "connect_error"


def test_parse_args_cli() -> None:
    """parse_args parses command line options correctly."""
    args = parse_args(["--raw", "raw.json", "--detailed", "detailed.json", "--no-network"])
    assert args.raw == Path("raw.json")
    assert args.detailed == Path("detailed.json")
    assert args.no_network is True
