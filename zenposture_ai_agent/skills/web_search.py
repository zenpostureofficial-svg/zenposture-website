"""
Web Search Skill
Uses DuckDuckGo (free, no API key) to search and read web pages.
"""

import urllib.request, urllib.parse, json, re, html


def ddg_search(query, max_results=5):
    """Search DuckDuckGo and return list of {title, url, snippet}."""
    params = urllib.parse.urlencode({
        "q": query, "format": "json", "no_html": "1",
        "skip_disambig": "1", "no_redirect": "1"
    })
    url = f"https://api.duckduckgo.com/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "ZenBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
    except Exception as e:
        return [], f"Search error: {e}"

    results = []
    # Instant answer
    if data.get("AbstractText"):
        results.append({
            "title": data.get("Heading", ""),
            "url":   data.get("AbstractURL", ""),
            "snippet": data["AbstractText"][:500]
        })
    # Related topics
    for topic in data.get("RelatedTopics", [])[:max_results]:
        if isinstance(topic, dict) and "Text" in topic:
            results.append({
                "title":   topic.get("Text", "")[:80],
                "url":     topic.get("FirstURL", ""),
                "snippet": topic.get("Text", "")[:300]
            })
    return results[:max_results], None


def read_page(url, max_chars=3000):
    """Fetch a webpage and return clean text (strips HTML tags)."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ZenBot/1.0",
                "Accept": "text/html,application/xhtml+xml"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[Could not read page: {e}]"

    # Strip scripts/styles
    raw = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', raw, flags=re.DOTALL|re.I)
    # Strip tags
    text = re.sub(r'<[^>]+>', ' ', raw)
    # Decode HTML entities
    text = html.unescape(text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def search_and_summarize(query, ollama_chat_fn, model, max_results=3):
    """
    Search web, read top pages, ask Ollama to summarize findings.
    Returns (summary_str, sources_list)
    """
    results, err = ddg_search(query, max_results=max_results)
    if err or not results:
        return f"Could not search: {err or 'No results'}", []

    # Build context from snippets
    context_parts = []
    sources = []
    for i, r in enumerate(results, 1):
        snippet = r.get("snippet", "")
        if not snippet and r.get("url"):
            snippet = read_page(r["url"], max_chars=1000)
        context_parts.append(f"[Source {i}] {r['title']}\n{snippet}")
        if r.get("url"):
            sources.append(r["url"])

    context = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": (
            "You are ZenBot, an AI assistant for ZenPosture (India). "
            "Summarize the web search results below to answer the user's question. "
            "Be concise, practical, and focused on what's useful for ZenPosture's business."
        )},
        {"role": "user", "content": f"Question: {query}\n\nSearch results:\n{context}"}
    ]

    try:
        summary = ollama_chat_fn(messages, model, temperature=0.4)
    except Exception as e:
        summary = f"Search found results but summarization failed: {e}\n\nRaw:\n{context[:1000]}"

    return summary, sources
