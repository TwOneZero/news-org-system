"""Debug RSS feed structure to understand content extraction."""

import feedparser


def debug_feed_structure(feed_url: str, source_name: str):
    """Debug RSS feed to see what content is available."""
    print(f"\n{'=' * 80}")
    print(f"Debugging: {source_name}")
    print(f"Feed URL: {feed_url}")
    print("=" * 80)

    feed = feedparser.parse(feed_url)

    if not feed.entries:
        print("❌ No entries found in feed")
        return

    # Check first entry
    entry = feed.entries[0]

    print("\n📰 Entry fields available:")
    print(f"  Title: {entry.get('title', 'N/A')[:80]}")
    print(f"  Link: {entry.get('link', 'N/A')}")

    # Check for different content fields
    print("\n📦 Content fields:")

    if hasattr(entry, "content"):
        print("  ✅ content field exists")
        print(f"     Type: {type(entry.content)}")
        print(f"     Length: {len(entry.content)}")
        if entry.content:
            print(f"     First item type: {type(entry.content[0])}")
            print(f"     First item value type: {type(entry.content[0].value)}")
            print(f"     First 200 chars: {entry.content[0].value[:200]}...")
    else:
        print("  ❌ No content field")

    if hasattr(entry, "summary"):
        print("  ✅ summary field exists")
        print(f"     Length: {len(entry.summary)}")
        print(f"     Content (first 200 chars): {entry.summary[:200]}...")
    else:
        print("  ❌ No summary field")

    if hasattr(entry, "description"):
        print("  ✅ description field exists")
        print(f"     Length: {len(entry.description)}")
        print(f"     Content (first 200 chars): {entry.description[:200]}...")
    else:
        print("  ❌ No description field")

    # Check what would be used by current implementation
    print("\n🔍 Current implementation would use:")

    # This mimics the _extract_content logic
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].value
        print(f"  1. content:encoded ({len(content)} chars)")
    elif hasattr(entry, "summary") and entry.summary:
        content = entry.summary
        print(f"  2. summary ({len(content)} chars)")
    elif hasattr(entry, "description") and entry.description:
        content = entry.description
        print(f"  3. description ({len(content)} chars)")
    else:
        print("  Would fallback to newspaper4k")

    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    feeds = [
        ("Maeil Business News", "https://www.mk.co.kr/rss/50100032/"),
        ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
        ("Yonhap News", "https://www.yonhapnewstv.co.kr/category/news/economy/feed"),
    ]

    for source_name, feed_url in feeds:
        debug_feed_structure(feed_url, source_name)
