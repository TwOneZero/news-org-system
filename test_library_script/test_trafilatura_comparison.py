"""Compare newspaper4k vs trafilatura for content extraction."""

from newspaper import Article as NewspaperArticle
import trafilatura
from typing import Dict, Any


def test_newspaper4k(url: str) -> Dict[str, Any]:
    """Test content extraction with newspaper4k."""
    try:
        article = NewspaperArticle(url)
        article.config.language = 'ko' if 'mk.co.kr' in url else 'en'
        article.config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        article.config.request_timeout = 30
        article.download()
        article.parse()

        return {
            "method": "newspaper4k",
            "success": bool(article.text and len(article.text) > 100),
            "content_length": len(article.text) if article.text else 0,
            "preview": article.text[:200] if article.text else "",
        }
    except Exception as e:
        return {
            "method": "newspaper4k",
            "success": False,
            "error": str(e),
            "content_length": 0,
            "preview": ""
        }


def test_trafilatura(url: str) -> Dict[str, Any]:
    """Test content extraction with trafilatura."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {
                "method": "trafilatura",
                "success": False,
                "error": "Failed to download URL",
                "content_length": 0,
                "preview": ""
            }

        content = trafilatura.extract(
            downloaded,
            output_format="txt",  # Fixed: "txt" not "text"
            include_comments=False,
            include_tables=True,
            no_fallback=False
        )

        return {
            "method": "trafilatura",
            "success": bool(content and len(content) > 100),
            "content_length": len(content) if content else 0,
            "preview": content[:200] if content else "",
        }
    except Exception as e:
        return {
            "method": "trafilatura",
            "success": False,
            "error": str(e),
            "content_length": 0,
            "preview": ""
        }


def compare_methods(url: str, source_name: str):
    """Compare both extraction methods for a given URL."""
    print(f"\n{'='*80}")
    print(f"Testing: {source_name}")
    print(f"URL: {url}")
    print('='*80)

    newspaper_result = test_newspaper4k(url)
    trafilatura_result = test_trafilatura(url)

    print(f"\n📰 newspaper4k:")
    if newspaper_result["success"]:
        print(f"  ✅ Success: {newspaper_result['content_length']} chars")
        print(f"  Preview: {newspaper_result['preview'][:100]}...")
    else:
        print(f"  ❌ Failed: {newspaper_result.get('error', 'Content too short')}")

    print(f"\n🔍 trafilatura:")
    if trafilatura_result["success"]:
        print(f"  ✅ Success: {trafilatura_result['content_length']} chars")
        print(f"  Preview: {trafilatura_result['preview'][:100]}...")
    else:
        print(f"  ❌ Failed: {trafilatura_result.get('error', 'Content too short')}")

    # Compare
    print(f"\n📊 Comparison:")
    if trafilatura_result["content_length"] > newspaper_result["content_length"]:
        improvement = trafilatura_result["content_length"] - newspaper_result["content_length"]
        print(f"  → trafilatura extracted {improvement} more chars ({improvement/max(1, newspaper_result['content_length'])*100:.0f}% improvement)")
    elif newspaper_result["content_length"] > trafilatura_result["content_length"]:
        diff = newspaper_result["content_length"] - trafilatura_result["content_length"]
        print(f"  → newspaper4k extracted {diff} more chars")
    else:
        print(f"  → Both methods extracted similar content")

    return newspaper_result, trafilatura_result


if __name__ == "__main__":
    # Test URLs from recent articles
    test_cases = [
        ("Maeil Business News", "https://www.mk.co.kr/news/business/11989440"),
        ("BBC News", "https://www.bbc.com/news/articles/cd9g331v315o"),
        ("Yonhap News (baseline)", "https://www.yonhapnewstv.co.kr/news/AKR20260316183841nPy"),
    ]

    results = []

    for source_name, url in test_cases:
        newspaper_r, trafilatura_r = compare_methods(url, source_name)
        results.append((source_name, newspaper_r, trafilatura_r))

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)

    for source_name, newspaper_r, trafilatura_r in results:
        np_len = newspaper_r["content_length"]
        tf_len = trafilatura_r["content_length"]

        print(f"\n{source_name}:")
        print(f"  newspaper4k: {np_len} chars {'✅' if np_len > 500 else '❌'}")
        print(f"  trafilatura: {tf_len} chars {'✅' if tf_len > 500 else '❌'}")

        if tf_len > np_len:
            print(f"  🏆 Winner: trafilatura (+{tf_len - np_len} chars)")
        elif np_len > tf_len:
            print(f"  🏆 Winner: newspaper4k (+{np_len - tf_len} chars)")
        else:
            print(f"  🤝 Tie")

    print(f"\n{'='*80}")
