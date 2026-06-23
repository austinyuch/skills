#!/usr/bin/env python3
"""
新聞差異比對工具

用於比較新舊新聞清單，找出新增的報導。
適用於受害者家屬權益新聞追蹤器的每日增量更新。

Usage:
    python diff_checker.py --old old_report.md --new new_report.md
    python diff_checker.py --old old_report.md --urls "url1,url2,url3"
    python diff_checker.py --check-duplicates report.md
"""

import argparse
import re
import sys
from datetime import datetime
from typing import List, Set, Dict, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class NewsItem:
    """新聞項目資料類別"""

    title: str
    url: str
    source: str
    date: str
    tags: List[str]

    def __hash__(self):
        # 使用 URL 作為唯一識別
        return hash(self.url)

    def __eq__(self, other):
        if not isinstance(other, NewsItem):
            return False
        return self.url == other.url


def extract_urls_from_markdown(content: str) -> Set[str]:
    """
    從 Markdown 內容中提取所有 URL

    Args:
        content: Markdown 文字內容

    Returns:
        URL 集合
    """
    # Markdown 連結格式: [文字](URL)
    url_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(url_pattern, content)

    urls = set()
    for text, url in matches:
        # 過濾圖片連結（以圖片副檔名結尾）
        if not any(
            url.lower().endswith(ext)
            for ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]
        ):
            # 過濾錨點連結
            if not url.startswith("#"):
                urls.add(url.strip())

    return urls


def extract_news_items_from_markdown(content: str) -> List[NewsItem]:
    """
    從 Markdown 內容中提取結構化新聞項目

    Args:
        content: Markdown 文字內容

    Returns:
        NewsItem 清單
    """
    items = []

    # 分割成各個報導區塊（以 #### 或 ### 開頭）
    sections = re.split(r"\n(?=#{2,4}\s)", content)

    for section in sections:
        # 提取標題
        title_match = re.search(r"^#{2,4}\s+(.+)$", section, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        # 提取 URL
        url_match = re.search(r"\[([^\]]+)\]\(([^\)]+)\)", section)
        if not url_match:
            continue
        url = url_match.group(2).strip()

        # 提取來源
        source = "未知"
        source_match = re.search(r"\*\*來源\*\*：\s*\[([^\]]+)\]", section)
        if source_match:
            source = source_match.group(1)

        # 提取日期
        date = "未知"
        date_match = re.search(r"\*\*日期\*\*：\s*(\d{4}-\d{2}-\d{2})", section)
        if date_match:
            date = date_match.group(1)

        # 提取標籤
        tags = []
        tag_match = re.search(r"\*\*標籤\*\*：\s*(.+)", section)
        if tag_match:
            tag_text = tag_match.group(1)
            # 提取 #tag 格式
            tags = re.findall(r"#\w+", tag_text)

        item = NewsItem(title=title, url=url, source=source, date=date, tags=tags)
        items.append(item)

    return items


def normalize_url(url: str) -> str:
    """
    標準化 URL，移除追蹤參數和常見變體

    Args:
        url: 原始 URL

    Returns:
        標準化後的 URL
    """
    # 移除常見追蹤參數
    tracking_params = ["utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid"]

    parsed = urlparse(url)

    # 重建 URL（不含追蹤參數）
    if parsed.query:
        params = parsed.query.split("&")
        filtered_params = [
            p for p in params if not any(tp in p for tp in tracking_params)
        ]
        query = "&".join(filtered_params)
    else:
        query = ""

    # 移除末尾的斜線
    path = parsed.path.rstrip("/")

    # 重建 URL
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    if query:
        normalized += f"?{query}"

    return normalized.lower()


def compare_news_sets(
    old_items: List[NewsItem], new_items: List[NewsItem]
) -> Tuple[List[NewsItem], List[NewsItem]]:
    """
    比較新舊新聞集合，找出新增和移除的項目

    Args:
        old_items: 舊新聞清單
        new_items: 新新聞清單

    Returns:
        (新增項目清單, 移除項目清單)
    """
    old_set = set(old_items)
    new_set = set(new_items)

    added = list(new_set - old_set)
    removed = list(old_set - new_set)

    return added, removed


def find_duplicate_urls(items: List[NewsItem]) -> Dict[str, List[NewsItem]]:
    """
    找出重複的 URL（可能有不同標題）

    Args:
        items: 新聞項目清單

    Returns:
        重複 URL 的字典，key 為 URL，value 為相關項目清單
    """
    url_groups: Dict[str, List[NewsItem]] = {}

    for item in items:
        normalized = normalize_url(item.url)
        if normalized not in url_groups:
            url_groups[normalized] = []
        url_groups[normalized].append(item)

    # 只保留有重複的
    duplicates = {url: items for url, items in url_groups.items() if len(items) > 1}

    return duplicates


def calculate_similarity(str1: str, str2: str) -> float:
    """
    計算兩個字串的相似度（簡易版）

    Args:
        str1: 第一個字串
        str2: 第二個字串

    Returns:
        相似度比例 (0.0 - 1.0)
    """
    if str1 == str2:
        return 1.0

    # 簡易實作：計算共同子字串比例
    str1, str2 = str1.lower(), str2.lower()
    len1, len2 = len(str1), len(str2)

    if len1 == 0 or len2 == 0:
        return 0.0

    # 計算最長共同子序列（簡易版）
    matches = 0
    for i in range(min(len1, len2)):
        if i < len1 and i < len2 and str1[i] == str2[i]:
            matches += 1

    return matches / max(len1, len2)


def find_similar_titles(
    items: List[NewsItem], threshold: float = 0.8
) -> List[Tuple[NewsItem, NewsItem, float]]:
    """
    找出標題相似的項目（可能是同一新聞的不同報導）

    Args:
        items: 新聞項目清單
        threshold: 相似度門檻 (預設 0.8)

    Returns:
        相似項目組合清單，每個元素為 (項目1, 項目2, 相似度)
    """
    similar_pairs = []

    for i, item1 in enumerate(items):
        for item2 in items[i + 1 :]:
            similarity = calculate_similarity(item1.title, item2.title)
            if similarity >= threshold:
                similar_pairs.append((item1, item2, similarity))

    # 依相似度排序
    similar_pairs.sort(key=lambda x: x[2], reverse=True)

    return similar_pairs


def format_diff_report(
    added: List[NewsItem],
    removed: List[NewsItem],
    duplicates: Dict[str, List[NewsItem]],
) -> str:
    """
    格式化差異報告

    Args:
        added: 新增項目
        removed: 移除項目
        duplicates: 重複項目

    Returns:
        Markdown 格式的報告
    """
    report = []
    report.append("# 新聞差異比對報告")
    report.append(f"\n**產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    # 新增項目
    report.append(f"## 新增報導（共 {len(added)} 篇）\n")
    if added:
        for i, item in enumerate(added, 1):
            report.append(f"### {i}. {item.title}")
            report.append(f"- **來源**：{item.source}")
            report.append(f"- **日期**：{item.date}")
            report.append(f"- **URL**：[連結]({item.url})")
            if item.tags:
                report.append(f"- **標籤**：{' '.join(item.tags)}")
            report.append("")
    else:
        report.append("_無新增報導_\n")

    report.append("---\n")

    # 移除項目
    report.append(f"## 移除報導（共 {len(removed)} 篇）\n")
    if removed:
        for i, item in enumerate(removed, 1):
            report.append(f"### {i}. {item.title}")
            report.append(f"- **來源**：{item.source}")
            report.append(f"- **URL**：[連結]({item.url})")
            report.append("")
    else:
        report.append("_無移除報導_\n")

    report.append("---\n")

    # 重複項目
    report.append(f"## 重複報導檢查\n")
    if duplicates:
        report.append(f"發現 {len(duplicates)} 組重複 URL：\n")
        for url, items in duplicates.items():
            report.append(f"### URL: {url[:80]}...")
            for item in items:
                report.append(f"- {item.title}（{item.source}）")
            report.append("")
    else:
        report.append("_未發現重複報導_\n")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="新聞差異比對工具 - 比較新舊新聞報告，找出差異",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # 比較兩份報告
    python diff_checker.py --old report_20240114.md --new report_20240115.md
    
    # 檢查報告中的重複項目
    python diff_checker.py --check-duplicates report.md
    
    # 比較報告與 URL 清單
    python diff_checker.py --old report.md --urls "http://example.com/1,http://example.com/2"
        """,
    )

    parser.add_argument("--old", type=str, help="舊報告檔案路徑")
    parser.add_argument("--new", type=str, help="新報告檔案路徑")
    parser.add_argument("--urls", type=str, help="URL 清單（以逗號分隔）")
    parser.add_argument("--check-duplicates", type=str, help="檢查指定報告中的重複項目")
    parser.add_argument(
        "--output", "-o", type=str, help="輸出檔案路徑（預設輸出到 stdout）"
    )
    parser.add_argument(
        "--threshold", "-t", type=float, default=0.8, help="標題相似度門檻（預設 0.8）"
    )

    args = parser.parse_args()

    # 檢查重複項目模式
    if args.check_duplicates:
        try:
            with open(args.check_duplicates, "r", encoding="utf-8") as f:
                content = f.read()

            items = extract_news_items_from_markdown(content)
            duplicates = find_duplicate_urls(items)
            similar = find_similar_titles(items, args.threshold)

            report = []
            report.append(f"# 重複項目檢查報告")
            report.append(f"\n**檔案**：{args.check_duplicates}")
            report.append(f"**總項目數**：{len(items)}")
            report.append(f"\n---\n")

            # URL 重複
            report.append(f"## URL 重複檢查\n")
            if duplicates:
                report.append(f"發現 {len(duplicates)} 組重複 URL\n")
                for url, items in duplicates.items():
                    report.append(f"### {url[:60]}...")
                    for item in items:
                        report.append(f"- {item.title}")
                    report.append("")
            else:
                report.append("_未發現 URL 重複_\n")

            # 標題相似
            report.append(f"\n## 相似標題檢查（門檻：{args.threshold}）\n")
            if similar:
                report.append(f"發現 {len(similar)} 組相似標題\n")
                for item1, item2, sim in similar[:10]:  # 只顯示前 10
                    report.append(f"### 相似度：{sim:.2%}")
                    report.append(f"- A：{item1.title}")
                    report.append(f"- B：{item2.title}")
                    report.append("")
            else:
                report.append("_未發現相似標題_\n")

            output = "\n".join(report)

        except FileNotFoundError:
            print(f"錯誤：找不到檔案 {args.check_duplicates}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"錯誤：{e}", file=sys.stderr)
            sys.exit(1)

    # 比較模式
    elif args.old:
        try:
            # 讀取舊報告
            with open(args.old, "r", encoding="utf-8") as f:
                old_content = f.read()
            old_items = extract_news_items_from_markdown(old_content)

            # 讀取新報告或 URL 清單
            if args.new:
                with open(args.new, "r", encoding="utf-8") as f:
                    new_content = f.read()
                new_items = extract_news_items_from_markdown(new_content)
            elif args.urls:
                urls = [u.strip() for u in args.urls.split(",")]
                new_items = [
                    NewsItem(
                        title=f"URL_{i}", url=u, source="未知", date="未知", tags=[]
                    )
                    for i, u in enumerate(urls)
                ]
            else:
                print("錯誤：請提供 --new 或 --urls 參數", file=sys.stderr)
                sys.exit(1)

            # 比較
            added, removed = compare_news_sets(old_items, new_items)
            duplicates = find_duplicate_urls(new_items)

            output = format_diff_report(added, removed, duplicates)

        except FileNotFoundError as e:
            print(f"錯誤：找不到檔案 {e.filename}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"錯誤：{e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)

    # 輸出結果
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"報告已儲存至：{args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
