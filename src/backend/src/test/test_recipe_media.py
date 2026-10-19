"""Tests for recipe media building, scraping, URL validation, and step normalization."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from AI.catalog.media_builder import (
    DEFAULT_BUNDLE_DIR,
    clean_url,
    extract_image_from_html,
    load_recipe_overrides,
    normalize_step,
    normalize_steps,
    parse_args,
    select_best_image_candidate,
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


def test_extract_image_json_ld_with_control_characters() -> None:
    """extract_image_from_html parses JSON-LD containing raw tabs and newlines inside strings."""
    # Raw newline and unescaped tab inside recipe description/name string
    html_with_control_chars = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Recipe",
          "name": "Tom Vien Dau Hu\n\tXot Ca",
          "description": "Mon ngon moi ngay\tvuong tron\nhuong vi",
          "image": [
            "https://monngonmoingay.com/wp-content/uploads/2023/08/tom-vien-300.jpg",
            "https://monngonmoingay.com/wp-content/uploads/2023/08/tom-vien-500.jpg",
            "https://monngonmoingay.com/wp-content/uploads/2023/08/tom-vien.jpg"
          ]
        }
        </script>
      </head>
    </html>
    """
    extracted = extract_image_from_html(html_with_control_chars, "https://monngonmoingay.com")
    assert extracted == "https://monngonmoingay.com/wp-content/uploads/2023/08/tom-vien.jpg"


def test_thumbnail_preference_and_ranking() -> None:
    """select_best_image_candidate prefers unsuffixed originals, larger sizes, and jpg over webp."""
    # Unsuffixed original beats -500 and -300
    cands1 = [
        "https://example.com/tom-vien-300.jpg",
        "https://example.com/tom-vien-500.jpg",
        "https://example.com/tom-vien.jpg",
    ]
    assert select_best_image_candidate(cands1) == "https://example.com/tom-vien.jpg"

    # When no unsuffixed exists, -500 beats -300
    cands2 = [
        "https://example.com/my-can-300.jpg",
        "https://example.com/my-can-500.jpg",
    ]
    assert select_best_image_candidate(cands2) == "https://example.com/my-can-500.jpg"

    # JPG format preferred over WEBP even when webp has higher dimension suffix
    cands3 = [
        "https://example.com/dau-hu-300.jpg",
        "https://example.com/dau-hu-500.jpg",
        "https://example.com/dau-hu-880.webp",
    ]
    assert select_best_image_candidate(cands3) == "https://example.com/dau-hu-500.jpg"

    # Dimension suffix -1024x202 beats -300x150
    cands4 = [
        "https://example.com/dish-300x150.jpg",
        "https://example.com/dish-1024x202.jpg",
    ]
    assert select_best_image_candidate(cands4) == "https://example.com/dish-1024x202.jpg"

    # Empty candidate list
    assert select_best_image_candidate([]) is None


def test_load_recipe_overrides_application_and_validation(tmp_path: Path) -> None:
    """load_recipe_overrides validates known IDs and malformed inputs."""
    valid_ids = {"uuid-1", "uuid-2"}

    # Valid override file
    valid_file = tmp_path / "valid_overrides.json"
    valid_file.write_text(
        '[{"id": "uuid-1", "name": "Dish 1", "steps": [{"step": 1, "text": "Step 1"}], "steps_source": "manual"}]',
        encoding="utf-8",
    )
    loaded = load_recipe_overrides(valid_file, valid_ids)
    assert "uuid-1" in loaded
    assert loaded["uuid-1"]["steps_source"] == "manual"

    # Unknown recipe id raises ValueError
    unknown_file = tmp_path / "unknown_overrides.json"
    unknown_file.write_text(
        '[{"id": "non-existent-uuid", "name": "Fake", "steps": []}]',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unknown recipe id in overrides"):
        load_recipe_overrides(unknown_file, valid_ids)

    # Malformed overrides: not a list
    not_list_file = tmp_path / "not_list.json"
    not_list_file.write_text('{"id": "uuid-1"}', encoding="utf-8")
    with pytest.raises(TypeError, match="must contain a JSON list"):
        load_recipe_overrides(not_list_file, valid_ids)

    # Missing id in entry
    missing_id_file = tmp_path / "missing_id.json"
    missing_id_file.write_text('[{"name": "No ID"}]', encoding="utf-8")
    with pytest.raises(ValueError, match="missing required 'id'"):
        load_recipe_overrides(missing_id_file, valid_ids)

    # None or non-existent path returns empty dict
    assert load_recipe_overrides(None, valid_ids) == {}
    assert load_recipe_overrides(tmp_path / "does_not_exist.json", valid_ids) == {}


def test_recipe_media_builder_determinism_and_steps_source() -> None:
    """Artifact records have steps_source and are deterministically sorted by ID."""
    import json

    media_artifact = DEFAULT_BUNDLE_DIR / "catalog" / "recipe_media.json"
    assert media_artifact.is_file(), f"Missing artifact: {media_artifact}"

    with media_artifact.open(mode="r", encoding="utf-8") as f:
        records = json.load(f)

    assert len(records) == 1075

    # Deterministic ID ordering
    ids = [str(r["id"]) for r in records]
    assert ids == sorted(ids), "recipe_media.json records must be sorted deterministically by ID"

    # Every entry has steps_source set
    valid_sources = {"detailed", "raw", "article_rewritten", "composed_from_article_tips"}
    for r in records:
        assert "steps_source" in r, f"Record {r['id']} missing steps_source"
        assert r["steps_source"] in valid_sources, f"Record {r['id']} has invalid steps_source: {r['steps_source']}"

    # The 7 curated recipes specifically have their override steps_source
    overridden_ids = {
        "05dae86b-448a-514e-a4dc-2a81394b5dbd",
        "2316d42e-fbe6-5443-98e4-81cf0c34a145",
        "4b767868-aae2-5b64-b459-fce529d7e0c9",
        "4d7a2558-9c7b-5750-844c-f0ca902223a0",
        "c5270778-4e98-584b-8b9f-4b8eb39b9afd",
        "de9e2f72-4152-56c5-ad24-b2d11d232d67",
        "e4792ee5-a1be-52be-99ff-0264e7e19dc5",
    }
    for r in records:
        if r["id"] in overridden_ids:
            assert r["steps_source"] in {"article_rewritten", "composed_from_article_tips"}
