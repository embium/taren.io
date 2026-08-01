"""
Reddit HTML Parser
==================
Extracts posts from subreddit_page.html and comments from comments_page.html.

Post fields:
    post_id, title, author, created_at, content, score, num_comments, url

Comment fields:
    comment_id, body, url, parent_comment_id (None = top-level), author, created_at, score
"""

from __future__ import annotations

import json
import re
import datetime
from pathlib import Path
from typing import Any, Optional, Union

from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# BeautifulSoup's find() returns Tag | NavigableString | None, and attribute
# access returns _AttributeValue (str | list[str]).  The three helpers below
# narrow those types once so every call-site stays clean.


def _tag(elem: Union[Tag, PageElement, None]) -> Optional[Tag]:
    """Return *elem* if it is a Tag, otherwise None."""
    return elem if isinstance(elem, Tag) else None


def _attr(tag: Tag, name: str, default: str = "") -> str:
    """Return a single-string attribute value from *tag*, or *default*."""
    val = tag.get(name, default)
    if isinstance(val, list):
        return " ".join(val)
    return val if val is not None else default


def _find_tag(parent: Tag, *args: object, **kwargs: object) -> Optional[Tag]:
    """Like Tag.find() but always returns Tag | None (never NavigableString)."""
    return _tag(parent.find(*args, **kwargs))  # type: ignore[arg-type]


def _parse_iso(dt_str: str) -> datetime.datetime:
    """Parse an ISO-8601 datetime string into a timezone-aware datetime."""
    return datetime.datetime.fromisoformat(dt_str).astimezone(
        datetime.timezone.utc
    )


def _md_body(md_div: Tag) -> Optional[str]:
    """Extract readable text from a Reddit ``.md`` div.

    - Replaces ``<img>`` tags with a ``[image]`` placeholder.
    - Returns ``None`` when the resulting text is empty.
    """
    # Replace every <img> with a text sentinel so get_text captures it
    for img in md_div.find_all("img"):
        img.replace_with("[image]")
    text = md_div.get_text(separator="\n", strip=True)
    return text if text else None


def _get_score(thing: Tag) -> Optional[int]:
    """Return the canonical (unvoted) score from a post or comment thing div.

    Old Reddit renders three score spans: dislikes / unvoted / likes.
    The ``unvoted`` one has the real score in its ``title`` attribute.
    """
    span = _find_tag(thing, "span", class_="score unvoted")
    if span:
        title = _attr(span, "title")
        try:
            return int(title)
        except (ValueError, TypeError):
            pass
    # Fallback: data-score attribute on the thing div itself (posts only)
    try:
        return int(_attr(thing, "data-score"))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Post parsing
# ---------------------------------------------------------------------------


def parse_posts(html: str) -> list[dict] | None:
    """Parse a subreddit listing page and return a list of post dicts."""
    soup = BeautifulSoup(html, "html.parser")

    # Posts live inside #siteTable and have data-type="link"
    site_table = _find_tag(soup, "div", id="siteTable")
    if site_table is None:
        return

    posts: list[dict] = []

    # Only grab *direct* children that are post things – not nested children
    # (there shouldn't be any in a listing page, but be safe).
    thing_divs = site_table.find_all(
        "div",
        attrs={"data-type": "link"},
        recursive=False,
    )

    for thing in thing_divs:
        if not isinstance(thing, Tag):
            continue
        post_id = _attr(thing, "data-fullname").replace("t3_", "")
        if not post_id:
            continue

        # --- Title ---
        title_a = _find_tag(thing, "a", class_="title")
        title = " ".join(title_a.get_text().split()) if title_a else None

        # --- Author ---
        author = _attr(thing, "data-author") or None

        # --- Timestamp ---
        time_elem = _find_tag(thing, "time")
        created_at: Optional[datetime.datetime] = None
        if time_elem:
            dt_str = _attr(time_elem, "datetime")
            if dt_str:
                dt = datetime.datetime.fromisoformat(dt_str)
                created_at = dt.astimezone(datetime.timezone.utc)

        # --- Score ---
        score = _get_score(thing)

        # --- Num comments ---
        num_comments: Optional[int] = None
        try:
            num_comments = int(_attr(thing, "data-comments-count"))
        except (ValueError, TypeError):
            comments_a = _find_tag(thing, "a", class_="comments")
            if comments_a:
                text = comments_a.get_text(strip=True)  # e.g. "50 comments"
                try:
                    num_comments = int(text.split()[0])
                except (ValueError, IndexError):
                    pass

        # --- URL (canonical reddit.com permalink) ---
        permalink = _attr(thing, "data-permalink")
        subreddit = _attr(thing, "data-subreddit")
        url = f"https://reddit.com{permalink}" if permalink else None

        # --- Post body (text posts only – not available in listing pages) ---
        # Listing pages lazy-load body content; only comments pages have it.
        # content: Optional[str] = None

        posts.append(
            {
                "post_id": post_id,
                "title": title,
                "author": author,
                "created_at": created_at if created_at else None,
                # "content": content,
                "score": score,
                "num_comments": num_comments,
                "subreddit": subreddit,
                "url": url,
            }
        )

    return posts


# ---------------------------------------------------------------------------
# Comments-page post parsing
# ---------------------------------------------------------------------------


def parse_post_from_comments_page(html: str) -> Optional[dict]:
    """Parse the *post* entry from a comments page (includes body text)."""
    soup = BeautifulSoup(html, "html.parser")

    # The post itself appears as a data-type="link" thing at the top of the page
    thing = _find_tag(soup, "div", attrs={"data-type": "link"})
    if thing is None:
        return None

    post_id = _attr(thing, "data-fullname").replace("t3_", "")
    if not post_id:
        return None

    # --- Title ---
    title_a = _find_tag(thing, "a", class_="title")
    title = " ".join(title_a.get_text().split()) if title_a else None

    # --- Author ---
    author = _attr(thing, "data-author") or None

    # --- Timestamp ---
    time_elem = _find_tag(thing, "time")
    created_at = None
    if time_elem:
        dt_str = _attr(time_elem, "datetime")
        if dt_str:
            dt = datetime.datetime.fromisoformat(dt_str)
            created_at = dt.astimezone(datetime.timezone.utc)
            print("COMMENT", created_at)

    # --- Score (from the linkinfo sidebar – more reliable on comments pages) ---
    score: Optional[int] = None
    linkinfo = _find_tag(soup, "div", class_="linkinfo")
    if linkinfo:
        number_span = _find_tag(linkinfo, "span", class_="number")
        if number_span:
            try:
                score = int(number_span.get_text(strip=True).replace(",", ""))
            except ValueError:
                pass
    if score is None:
        score = _get_score(thing)

    # --- Num comments ---
    num_comments: Optional[int] = None
    comments_a = _find_tag(thing, "a", class_="comments")
    if comments_a:
        text = comments_a.get_text(strip=True)
        try:
            num_comments = int(text.split()[0])
        except (ValueError, IndexError):
            pass

    # --- Body (self-text posts only) ---
    content: Optional[str] = None
    # The post body is inside the thing div itself, in .usertext-body > .md
    entry_div = _find_tag(thing, "div", class_="entry")
    if entry_div:
        usertext = _find_tag(entry_div, "div", class_="usertext-body")
        if usertext:
            md_div = _find_tag(usertext, "div", class_="md")
            if md_div:
                content = _md_body(md_div)

    # --- URL ---
    permalink = _attr(thing, "data-permalink")
    subreddit = _attr(thing, "data-subreddit")
    url = f"https://reddit.com{permalink}" if permalink else None

    return {
        "post_id": post_id,
        "title": title,
        "author": author,
        "created_at": created_at if created_at else None,
        "content": content,
        "score": score,
        "num_comments": num_comments,
        "subreddit": subreddit,
        "url": url,
    }


# ---------------------------------------------------------------------------
# Comment parsing
# ---------------------------------------------------------------------------


def _parse_comment_thing(
    thing: Tag, post_id: str, subreddit: str, parent_comment_id: Optional[str]
) -> dict:
    """Extract comment fields from a single comment <div class="thing"> element."""
    comment_id = _attr(thing, "data-fullname").replace("t1_", "")

    # --- Author ---
    author = _attr(thing, "data-author") or None

    # --- Timestamp ---
    time_elem = _find_tag(thing, "time")
    created_at = None
    if time_elem:
        created_at = _attr(time_elem, "datetime")

    # --- Score ---
    # Only look inside the entry div to avoid picking up scores from child comments
    entry_div = _find_tag(thing, "div", class_="entry", recursive=False)
    score: Optional[int] = None
    if entry_div:
        score_span = _find_tag(entry_div, "span", class_="score unvoted")
        if score_span:
            try:
                score = int(_attr(score_span, "title"))
            except (ValueError, TypeError):
                pass

    # --- Body ---
    body: Optional[str] = None
    if entry_div:
        usertext = _find_tag(entry_div, "div", class_="usertext-body")
        if usertext:
            md_div = _find_tag(usertext, "div", class_="md")
            if md_div:
                body = _md_body(md_div)

    # --- URL ---
    url = (
        f"https://reddit.com/r/{subreddit}/comments/{post_id}/comment/{comment_id}"
        if subreddit and post_id and comment_id
        else None
    )

    return {
        "comment_id": comment_id,
        "body": body,
        "url": url,
        "parent_comment_id": parent_comment_id,
        "author": author,
        "created_at": created_at if created_at else None,
        "score": score,
        "post_id": post_id,
        "subreddit": subreddit,
    }


def _extract_comments_recursive(
    container: Tag,
    post_id: str,
    subreddit: str,
    parent_comment_id: Optional[str],
    results: list[dict],
) -> None:
    """Recursively walk a siteTable container and extract every comment."""
    # Direct children that are comment things
    for thing in container.find_all(
        "div", attrs={"data-type": "comment"}, recursive=False
    ):
        comment = _parse_comment_thing(
            thing, post_id, subreddit, parent_comment_id
        )
        results.append(comment)

        # Recurse into children: old Reddit puts replies inside
        # <div class="child"><div id="siteTable_t1_{comment_id}">...</div></div>
        child_div = _find_tag(thing, "div", class_="child", recursive=False)
        if child_div:
            inner = _find_tag(
                child_div,
                "div",
                id=lambda v: isinstance(v, str) and v.startswith("siteTable_"),
            )
            if inner:
                _extract_comments_recursive(
                    inner,
                    post_id,
                    subreddit,
                    comment["comment_id"],
                    results,
                )


def parse_comments(html: str) -> list[dict] | None:
    """Parse a post comments page and return a list of comment dicts.

    The parent_comment_id is None for top-level comments, or the comment_id
    of the direct parent for replies.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Derive post_id and subreddit from the post thing on the page
    post_thing = _find_tag(soup, "div", attrs={"data-type": "link"})
    post_id = ""
    subreddit = ""
    if post_thing:
        post_id = _attr(post_thing, "data-fullname").replace("t3_", "")
        subreddit = _attr(post_thing, "data-subreddit")

    # The top-level comment listing lives in #siteTable_t3_{post_id}
    root_tables = []
    if post_id:
        root_tables = soup.find_all("div", id=f"siteTable_t3_{post_id}")
    if not root_tables:
        # Fallback: find any div whose id starts with siteTable_t3_
        root_tables = soup.find_all(
            "div",
            id=lambda v: isinstance(v, str) and v.startswith("siteTable_t3_"),
        )

    if not root_tables:
        return None

    comments: list[dict] = []
    for root_table in root_tables:
        _extract_comments_recursive(
            root_table, post_id, subreddit, None, comments
        )
    return comments


# ---------------------------------------------------------------------------
# "Load more comments" support  (/api/morechildren)
# ---------------------------------------------------------------------------

# Regex that matches the onclick of a morechildren anchor:
#   morechildren(this, 't3_LINK_ID', 'sort', 'children_str', 'False')
_MORECHILDREN_RE = re.compile(
    r"morechildren\(this,\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'\)"
)

# Regex to pull modhash out of the r.setup({...}) JS block
_MODHASH_RE = re.compile(r'["\']modhash["\']\s*:\s*["\']([a-f0-9]+)["\']')


def extract_modhash(html: str) -> Optional[str]:
    """Return the modhash (session token) from a comments or listing page.

    Old Reddit embeds it in both the ``r.setup({...})`` JS block and in the
    hidden ``uh`` field of the logout form.  We try both.
    """
    # 1. Try the r.setup JS block (most reliable)
    m = _MODHASH_RE.search(html)
    if m:
        return m.group(1)

    # 2. Fall back to the hidden input in the logout form
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", class_="logout")
    if isinstance(form, Tag):
        uh = form.find("input", attrs={"name": "uh"})
        if isinstance(uh, Tag):
            val = _attr(uh, "value")
            if val:
                return val
    return None


def parse_more_children_stub(html: str) -> Optional[dict[str, Any]]:
    """Find the single top-level "load more comments" placeholder in a comments-page HTML.

    Returns a parameter dict ready to POST to
    ``https://old.reddit.com/api/morechildren``.  The dict contains:

    ``link_id``
        Full-name of the post, e.g. ``t3_1v7q8yv``.
    ``sort``
        Sort order used on the page, e.g. ``confidence``.
    ``children``
        The raw children string from the onclick, e.g. ``c1:t1_abc,t1_def``.
    ``id``
        The ``t1_`` identifier of the anchor element.
    ``limit_children``
        Literal string ``'True'`` or ``'False'`` from the onclick.
    ``num_replies``
        How many hidden replies this stub represents (informational).

    **Stopping condition**: when this returns None there are no more
    top-level comments to load from the page you passed in.
    """
    soup = BeautifulSoup(html, "html.parser")

    for thing in soup.find_all(
        "div",
        attrs={"data-type": "morechildren"},
    ):
        if not isinstance(thing, Tag):
            continue

        # ONLY consider top-level continuation stubs.
        # A top-level stub is NOT inside any comment's siteTable (siteTable_t1_...).
        # It should only be inside the main post's siteTable (siteTable_t3_...).
        is_nested = False
        for parent in thing.parents:
            if not isinstance(parent, Tag):
                continue
            pid = parent.get("id")
            if isinstance(pid, str) and pid.startswith("siteTable_t1_"):
                is_nested = True
                break

        if is_nested:
            continue

        # The clickable anchor lives inside .morecomments
        anchor = _find_tag(thing, "a", class_="button")
        if anchor is None:
            continue

        onclick = _attr(anchor, "onclick")
        m = _MORECHILDREN_RE.search(onclick)
        if not m:
            continue

        link_id, sort, children_str, limit_children = m.groups()

        # The anchor id is "more_t1_XXXX"; strip the "more_" prefix
        anchor_id = _attr(anchor, "id").removeprefix("more_")

        # Count the hidden replies from the span text, e.g. "(162 replies)"
        num_replies = 0
        gray = anchor.find("span", class_="gray")
        if isinstance(gray, Tag):
            digits = re.search(r"(\d+)", gray.get_text())
            if digits:
                num_replies = int(digits.group(1))

        return {
            "link_id": link_id,
            "sort": sort,
            "children": children_str,
            "id": anchor_id,
            "limit_children": limit_children,
            "num_replies": num_replies,
        }

    return None


def parse_more_children_response(
    response_json: dict[str, Any],
    subreddit: str,
) -> dict[str, Any]:
    """Parse the JSON from ``POST /api/morechildren``.

    Returns a dict with two keys:

    ``comments``
        A flat list of comment dicts in the same schema as ``parse_comments``.

    ``stub``
        An ``Optional[dict]`` — the next morechildren stub found inside any
        of the returned content fragments, or ``None`` if all comments have
        been loaded.  Pass this stub directly to the next ``/api/morechildren``
        request to continue paginating.

    **Stopping condition**: keep calling ``/api/morechildren`` while
    ``result["stub"]`` is not ``None``.

    The endpoint returns a ``{"jquery": [...]}`` envelope containing an
    ``insert_things`` call.  Each item has ``kind="t1"`` and
    ``data.content`` (HTML-encoded comment HTML).  ``data.parent`` gives the
    parent fullname:

    * ``t3_XXXX``  →  top-level comment  (``parent_comment_id = None``)
    * ``t1_XXXX``  →  reply to that comment
    """
    import html as html_lib  # stdlib – avoid shadowing the outer 'html' param

    comments: list[dict[str, Any]] = []
    stub: Optional[dict[str, Any]] = None

    # Walk the jquery array looking for the insert_things payload
    jquery = response_json.get("jquery", [])
    for step in jquery:
        # Each step is [target_id, result_id, method, args]
        if len(step) < 4:
            continue
        _target, _result, method, args = step[:4]
        if method != "call":
            continue
        if not isinstance(args, list) or not args:
            continue
        payload = args[0]
        if not isinstance(payload, list):
            continue

        for thing_obj in payload:
            if not isinstance(thing_obj, dict):
                continue

            kind = thing_obj.get("kind")
            data = thing_obj.get("data", {})
            content_html = html_lib.unescape(data.get("content", ""))
            post_id = data.get("link", "").replace("t3_", "")

            if kind == "t1":
                # Regular comment — extract and store
                if not content_html:
                    continue

                parent_fullname: str = data.get("parent", "")
                if parent_fullname.startswith("t1_"):
                    parent_comment_id: Optional[str] = parent_fullname[3:]
                else:
                    parent_comment_id = None  # t3_ = top-level

                frag = BeautifulSoup(content_html, "html.parser")
                for thing in frag.find_all(
                    "div", attrs={"data-type": "comment"}
                ):
                    if not isinstance(thing, Tag):
                        continue
                    comment = _parse_comment_thing(
                        thing, post_id, subreddit, parent_comment_id
                    )
                    comments.append(comment)
                    break  # only the outermost; nested ones are separate items

            elif kind == "more":
                # Continuation stub — API provides a "parent" field.
                # If parent starts with "t3_", it's a top-level stub.
                # If parent starts with "t1_", it's a nested reply stub.
                parent_fullname: str = data.get("parent", "")
                if not parent_fullname.startswith("t3_"):
                    continue

                if stub is not None or not content_html:
                    continue

                m = _MORECHILDREN_RE.search(content_html)
                if not m:
                    continue
                link_id, sort, children_str, limit_children = m.groups()

                # Extract the anchor id (more_t1_XXXX → t1_XXXX)
                anchor_id_m = re.search(r'id="more_(t1_[^"]+)"', content_html)
                anchor_id = anchor_id_m.group(1) if anchor_id_m else ""

                num_replies = 0
                gray_m = re.search(r"\((\d+) repl", content_html)
                if gray_m:
                    num_replies = int(gray_m.group(1))

                stub = {
                    "link_id": link_id,
                    "sort": sort,
                    "children": children_str,
                    "id": anchor_id,
                    "limit_children": limit_children,
                    "num_replies": num_replies,
                }

    return {"comments": comments, "stub": stub}


def process_comment_json(node, post_id, subreddit, parent_comment_id=None):
    kind = node.get("kind")
    data = node.get("data", {})

    if kind == "t1":
        # It's a comment
        comment_id = data.get("id")
        if not comment_id:
            return

        content = data.get("body", "")

        # Recurse into replies if present
        replies = data.get("replies")
        if isinstance(replies, dict):
            children = replies.get("data", {}).get("children", [])
            for child in children:
                process_comment_json(
                    child,
                    post_id,
                    subreddit,
                    parent_comment_id=parent_comment_id,
                )

        return {
            "comment_id": comment_id,
            "post": post_id,
            "parent_id": parent_comment_id if parent_comment_id else None,
            "author": data.get("author", "[deleted]"),
            "created_at": data.get("created_at", None),
            "content": content,
            "score": data.get("score", 0),
            "subreddit": subreddit,
        }

    elif kind == "more":
        # 'more' contains additional comment IDs that would need extra API requests.
        # Skipping for now to keep this implementation simple.
        return
    else:
        # t3 (post), t2 (user), t4 (message) etc. - ignore
        return


def _pprint(obj: object) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    base = Path(__file__).parent

    # --- Subreddit listing ---
    subreddit_html = (base / "subreddit_page.html").read_text(encoding="utf-8")
    posts = parse_posts(subreddit_html)
    if posts:
        print(f"=== Posts from subreddit_page.html ({len(posts)} found) ===\n")
        for p in posts[:3]:
            _pprint(p)
            print()

    # --- Comments page ---
    comments_html = (base / "comments_page.html").read_text(encoding="utf-8")
    post = parse_post_from_comments_page(comments_html)
    print("=== Post from comments_page.html ===\n")
    _pprint(post)
    print()

    comments = parse_comments(comments_html)
    if comments is None:
        raise ValueError(
            "Could not find the top-level comment listing. "
            "Is this a comments page?"
        )

    print(f"=== Comments from comments_page.html ({len(comments)} found) ===\n")
    for c in comments[:5]:
        _pprint(c)
        print()

    # --- load_more_comments_page.html (morechildren stubs) ---
    load_more_path = base / "load_more_comments_page.html"
    if load_more_path.exists():
        lm_html = load_more_path.read_text(encoding="utf-8")

        modhash = extract_modhash(lm_html)
        print(f"=== Modhash extracted: {modhash} ===\n")

        stub = parse_more_children_stub(lm_html)
        if stub:
            print(
                f"=== Top-level morechildren stub ({stub['num_replies']} hidden replies) ===\n"
            )
            _pprint(stub)
        else:
            print("=== No top-level morechildren stub found ===")
        print()
        print(
            "(To load more comments POST the stub to https://old.reddit.com/api/morechildren)"
        )
        print(
            "(parse_more_children_response returns {'comments': [...], 'stub': ...})"
        )
        print("(Keep looping while result['stub'] is not None)")
