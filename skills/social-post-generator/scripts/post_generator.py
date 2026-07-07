#!/usr/bin/env python3
"""
社群發文生成工具 (Social Post Generator)

讀取 victim-rights-news-tracker 報告，生成3個風格的社群發文選項。

Usage:
    python post_generator.py --input victim-news-daily-20240115.md
    python post_generator.py --input report.md --focus "#小燈泡案"
    python post_generator.py --input report.md --platform instagram
    python post_generator.py --input report.md --output social-posts-20240115.md
"""

import argparse
import re
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NewsItem:
    """新聞素材項目"""

    title: str
    source: str
    date: str
    summary: str
    tags: List[str]
    importance: int  # 1-5
    content_type: str  # legislation, case_activity, case_tracking, international
    image_urls: List[str]
    urls: List[str]


@dataclass
class PostOption:
    """發文選項"""

    style: str  # formal, emotional, action
    title: str
    content: str
    hashtags: Dict[str, str]  # full, medium, minimal
    suggested_images: List[str]
    posting_time: str
    platform_tips: str


class PostGenerator:
    """社群發文生成器"""

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / "posts"
        self.output_dir.mkdir(exist_ok=True)

    def parse_report(self, report_path: str) -> List[NewsItem]:
        """解析新聞報告，擷取素材"""
        items = []

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ 找不到報告檔案: {report_path}")
            return items

        # 使用正則表達式解析 Markdown 結構
        # 識別新聞標題（通常以 ### 開頭，包含 [NEW] 標記）
        news_pattern = r"###\s+(?:\[NEW\]\s*)?(.+?)\n.*?-\s*\*\*來源\*\*：\s*\[([^\]]+)\]\(([^)]+)\).*?-\s*\*\*日期\*\*：\s*(\d{4}-\d{2}-\d{2})"

        matches = re.findall(news_pattern, content, re.DOTALL)

        for match in matches[:5]:  # 取前5則重要新聞
            title, source, url, date = match

            # 判斷內容類型
            content_type = self._classify_content(title + content)

            # 評估重要性
            importance = self._assess_importance(title, content)

            # 擷取摘要
            summary = self._extract_summary(content, title)

            # 識別標籤
            tags = re.findall(r"#\w+", content)

            # 擷取圖片URL
            image_urls = re.findall(r"\[圖片.*\]\(([^)]+)\)", content)

            items.append(
                NewsItem(
                    title=title.strip(),
                    source=source.strip(),
                    date=date.strip(),
                    summary=summary[:200] + "..." if len(summary) > 200 else summary,
                    tags=list(set(tags)),
                    importance=importance,
                    content_type=content_type,
                    image_urls=image_urls[:3],  # 最多取3張
                    urls=[url.strip()],
                )
            )

        # 按重要性排序
        items.sort(key=lambda x: x.importance, reverse=True)

        return items

    def _classify_content(self, text: str) -> str:
        """分類內容類型"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["修法", "法案", "立法", "三讀", "審查"]):
            return "legislation"
        elif any(
            word in text_lower for word in ["記者會", "活動", "遊行", "抗議", "聲明"]
        ):
            return "case_activity"
        elif any(word in text_lower for word in ["判決", "宣判", "定讞", "上訴"]):
            return "case_tracking"
        elif any(word in text_lower for word in ["國際", "國外", "他國"]):
            return "international"
        else:
            return "general"

    def _assess_importance(self, title: str, content: str) -> int:
        """評估新聞重要性（1-5）"""
        score = 3  # 基礎分

        # 高重要性指標
        if "[NEW]" in content:
            score += 1
        if any(word in title for word in ["修法通過", "三讀", "重大進展", "突破"]):
            score += 1
        if "⭐⭐⭐⭐⭐" in content:
            score += 1

        return min(score, 5)

    def _extract_summary(self, content: str, title: str) -> str:
        """擷取新聞摘要"""
        # 尋找摘要段落
        summary_match = re.search(
            r"\*\*摘要\*\*：\s*(.+?)(?:\n\n|\n-|\Z)", content, re.DOTALL
        )
        if summary_match:
            return summary_match.group(1).strip()

        # 如果沒有摘要標記，取前100字
        clean_text = re.sub(r"#.*?\n|\*\*.*?\*\*|\[.*?\]\(.*?\)", "", content)
        return clean_text[:100].strip()

    def generate_formal_post(self, items: List[NewsItem]) -> Optional[PostOption]:
        """生成嚴肅正式風格發文"""
        if not items:
            return None

        top_item = items[0]

        # 選擇修法或重大案件新聞
        legislation_items = [i for i in items if i.content_type == "legislation"]
        if legislation_items:
            main_item = legislation_items[0]
        else:
            main_item = top_item

        title = f"司法改革的關鍵時刻：{main_item.title}"

        content = f"""{main_item.title}

{main_item.summary}

根據相關統計與研究，現行制度下被害人往往在司法程序中面臨{self._get_issue_description(main_item.content_type)}。

{self._get_expert_quote(main_item.content_type)}

司法正義不應僅停留在口號。讓我們一起關注被害人權益保障，為制度正義發聲。

📰 新聞來源：{main_item.source}
📅 報導日期：{main_item.date}
"""

        hashtags = {
            "full": "#司法改革 #被害人權益 #制度正義 #生命權平等協會 #修法倡議 #司法正義 #"
            + " #".join(main_item.tags[:3]),
            "medium": "#司法改革 #被害人權益 #制度正義 #生命權平等 #"
            + " #".join(main_item.tags[:2]),
            "minimal": "#司法改革 #被害人權益 #生命權平等",
        }

        return PostOption(
            style="formal",
            title=title,
            content=content.strip(),
            hashtags=hashtags,
            suggested_images=main_item.image_urls[:2],
            posting_time="週二至週四 10:00-12:00 或 19:00-21:00",
            platform_tips="適合Facebook深度討論，可附上修法提案連結",
        )

    def generate_emotional_post(self, items: List[NewsItem]) -> Optional[PostOption]:
        """生成情感訴求風格發文"""
        # 尋找有家屬元素的內容
        family_items = [
            i
            for i in items
            if any(tag in i.tags for tag in ["#家屬權益", "#司法不公", "#案件追蹤"])
        ]

        if family_items:
            main_item = family_items[0]
        else:
            main_item = items[0] if items else None

        if not main_item:
            return None

        title = f"「{self._get_emotional_quote()}」"

        content = f"""{title}

這是{main_item.title}相關案件家屬的心聲。

{main_item.summary}

每一個案件背後，都是一個需要被聽見的故事。被害人及其家屬在司法程序中不僅要面對創傷，更要獨自面對制度的種種挑戰。

「很多人問為什麼要站出來？因為我知道，還有很多在黑暗中孤軍奮戰的人。如果可以，我希望成為他們的光。」

讓我們一起關注 #被害人權益，用行動支持他們的勇氣與堅持。

因為正義不應該讓人等待太久。
"""

        hashtags = {
            "full": "#家屬的聲音 #正義不缺席 #陪伴 #生命權平等協會 #司法溫暖 #"
            + " #".join(main_item.tags[:3])
            + " #不孤單",
            "medium": "#家屬的聲音 #正義不缺席 #陪伴 #生命權平等 #"
            + " #".join(main_item.tags[:2]),
            "minimal": "#家屬的聲音 #正義不缺席 #陪伴",
        }

        return PostOption(
            style="emotional",
            title=title,
            content=content.strip(),
            hashtags=hashtags,
            suggested_images=main_item.image_urls[:2]
            if main_item.image_urls
            else ["建議使用家屬溫馨照片或紀念活動照片"],
            posting_time="週五至週日 20:00-22:00",
            platform_tips="Instagram適合，前2行必須抓住眼球，建議搭配溫馨圖片",
        )

    def generate_action_post(self, items: List[NewsItem]) -> Optional[PostOption]:
        """生成行動呼籲風格發文"""
        # 尋找有行動元素的內容
        action_items = [
            i for i in items if i.content_type in ["legislation", "case_activity"]
        ]

        if action_items:
            main_item = action_items[0]
        else:
            main_item = items[0] if items else None

        if not main_item:
            return None

        title = "🚨 緊急行動呼籲 🚨"

        content = f"""{main_item.title} 需要你的聲音！

{main_item.summary}

但阻力仍然存在。我們需要你的行動！

✅ 現在就做這3件事：

1️⃣ 【分享擴散】
將此貼文分享到你的動態，讓更多人知道
📢 每1次分享 = 多10個人看見

2️⃣ 【留言聲援】
在下方留言 "+1" 表示支持
💬 讓我們看見你的力量

3️⃣ 【關注追蹤】
追蹤我們的帳號，獲取最新進展
🔔 開啟通知，不錯過重要消息

📊 目標：1000次分享
⏰ 目前：持續進行中

🔥 改變，從你開始！🔥

現在就分享支持 👆
"""

        hashtags = {
            "full": "#一起行動 #支持修法 #改變從你開始 #立即分享 #生命權平等協會 #行動改變 #"
            + " #".join(main_item.tags[:2]),
            "medium": "#一起行動 #改變從你開始 #立即分享 #生命權平等 #"
            + " #".join(main_item.tags[:1]),
            "minimal": "#一起行動 #改變從你開始 #立即分享",
        }

        return PostOption(
            style="action",
            title=title,
            content=content.strip(),
            hashtags=hashtags,
            suggested_images=main_item.image_urls[:2]
            if main_item.image_urls
            else ["建議使用活動海報或視覺圖表"],
            posting_time="週一至週三 12:00-13:00（午餐時間）或 17:00-18:00（下班前）",
            platform_tips="所有平台適合，重點是清晰的CTA（Call-to-Action）",
        )

    def _get_issue_description(self, content_type: str) -> str:
        """根據內容類型返回問題描述"""
        descriptions = {
            "legislation": "程序繁瑣與權益保障的不足",
            "case_activity": "參與管道的欠缺",
            "case_tracking": "資訊不對等與心理壓力",
            "international": "與國際標準的差距",
            "general": "種種挑戰與困難",
        }
        return descriptions.get(content_type, "種種挑戰與困難")

    def _get_expert_quote(self, content_type: str) -> str:
        """根據內容類型返回專家引言範本"""
        quotes = {
            "legislation": "相關團體表示：「現行制度亟需改革，被害人的權益保障不應只是空談。」",
            "case_activity": "專家指出：「被害人的聲音需要被聽見，社會支持對於他們的復原至關重要。」",
            "case_tracking": "法界人士認為：「司法程序應該更加透明，讓家屬能夠參與其中。」",
            "international": "根據國際人權標準，被害人的權利應獲得充分保障。",
            "general": "相關專家呼籲：「社會應該給予被害人及其家屬更多支持與關懷。」",
        }
        return quotes.get(content_type, quotes["general"])

    def _get_emotional_quote(self) -> str:
        """返回情感引言範本"""
        import random

        quotes = [
            "我只是想為孩子討一個公道",
            "每天醒來，我都希望這是一場夢",
            "正義也許遲到，但我不會放棄",
            "我知道我不是孤單的",
            "這條路很難走，但我必須走下去",
        ]
        return random.choice(quotes)

    def generate_output(
        self, items: List[NewsItem], options: List[PostOption], report_path: str
    ) -> str:
        """生成最終輸出文件"""

        date_str = datetime.now().strftime("%Y%m%d")
        output_filename = f"social-posts-{date_str}.md"
        output_path = self.output_dir / output_filename

        content = f"""# 社群發文選項 - {datetime.now().strftime("%Y年%m月%d日")}

**來源報告**：{Path(report_path).name}  
**產生時間**：{datetime.now().strftime("%Y-%m-%d %H:%M")}  
**適用平台**：Facebook、Instagram、Threads

---

## 📊 本日精選素材摘要

| 新聞標題 | 類別 | 重要性 | 適用風格 |
|----------|------|--------|----------|
"""

        for item in items[:5]:
            importance_stars = "⭐" * item.importance
            content += f"| {item.title[:30]}... | {item.content_type} | {importance_stars} | {', '.join(item.tags[:2])} |\n"

        # 三個選項
        style_names = {
            "formal": ("A", "嚴肅正式"),
            "emotional": ("B", "情感訴求"),
            "action": ("C", "行動呼籲"),
        }

        for i, option in enumerate(options):
            if not option:
                continue
            letter, style_name = style_names.get(
                option.style, (str(i + 1), option.style)
            )

            content += f"""
---

## 選項 {letter}：{style_name}風格

### 標題
{option.title}

### 文案內容

{option.content}

### 配套建議

**建議配圖**：
"""
            for img in option.suggested_images:
                content += f"- {img}\n"

            content += f"""
**Hashtag組合**：
- 完整版（Facebook）：{option.hashtags["full"]}
- 簡潔版（Instagram）：{option.hashtags["medium"]}
- 極簡版（Threads）：{option.hashtags["minimal"]}

**發布建議**：
- 最佳時間：{option.posting_time}
- 平台提示：{option.platform_tips}

---
"""

        content += f"""
## 📋 快速決策指南

**選擇選項A（嚴肅正式）如果**：
- 今天有新聞媒體報導或修法進展
- 需要強調制度問題或專業分析
- 目標受眾是關注司法改革的理性族群
- 適合週間工作日發布

**選擇選項B（情感訴求）如果**：
- 有家屬訪談或感人故事可以分享
- 週末或節日發布，適合深度閱讀時段
- 希望引發情感共鳴與同理心
- Instagram 視覺導向適合

**選擇選項C（行動呼籲）如果**：
- 有具體行動機會或需要動員
- 時間緊迫需要快速擴散
- 目標是增加互動與參與度
- 希望提升追蹤與分享數

---

## 🖼️ 圖片素材總清單

| 圖片 | 描述 | 適用選項 | URL |
|------|------|----------|-----|
"""

        for i, item in enumerate(items[:3]):
            for j, img in enumerate(item.image_urls):
                content += (
                    f"| 圖{i + 1}-{j + 1} | {item.title[:20]}... | A,B,C | {img} |\n"
                )

        content += f"""
---

*產生工具：social-post-generator skill*  
*新聞來源：victim-rights-news-tracker*
"""

        # 寫入檔案
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(output_path)

    def generate(
        self,
        report_path: str,
        focus_tag: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> Optional[str]:
        """主生成函數"""

        print(f"📖 正在讀取報告: {report_path}")
        items = self.parse_report(report_path)

        if not items:
            print("❌ 無法從報告中擷取新聞素材")
            return None

        print(f"✅ 成功擷取 {len(items)} 則新聞素材")

        # 如果有指定標籤，篩選相關新聞
        if focus_tag:
            items = [i for i in items if focus_tag in i.tags or focus_tag in i.title]
            print(f"🔍 篩選標籤 '{focus_tag}' 後剩餘 {len(items)} 則")

        # 生成三個選項
        print("📝 正在生成發文選項...")

        option_a = self.generate_formal_post(items)
        option_b = self.generate_emotional_post(items)
        option_c = self.generate_action_post(items)

        options = [opt for opt in [option_a, option_b, option_c] if opt]

        if not options:
            print("❌ 無法生成發文選項")
            return None

        # 生成輸出文件
        output_path = self.generate_output(items, options, report_path)

        print(f"\n✅ 發文選項已生成！")
        print(f"📄 檔案位置: {output_path}")
        print(f"\n📊 生成摘要：")
        print(f"   - 素材數量: {len(items)} 則")
        print(f"   - 選項數量: {len(options)} 個")
        print(f"   - 建議平台: {platform or 'Facebook/Instagram/Threads'}")

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="社群發文生成工具 - 基於新聞報告生成3個風格的發文選項"
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="輸入的新聞報告檔案路徑（Markdown格式）",
    )
    parser.add_argument(
        "--focus", "-f", type=str, help="專注於特定標籤（如: #小燈泡案）"
    )
    parser.add_argument(
        "--platform",
        "-p",
        type=str,
        choices=["facebook", "instagram", "threads"],
        help="主要目標平台",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="輸出檔案路徑（預設: posts/social-posts-YYYYMMDD.md）",
    )

    args = parser.parse_args()

    # 檢查輸入檔案
    if not os.path.exists(args.input):
        print(f"❌ 錯誤：找不到輸入檔案 {args.input}")
        return 1

    # 生成發文
    generator = PostGenerator()
    output_path = generator.generate(
        report_path=args.input, focus_tag=args.focus, platform=args.platform
    )

    if output_path:
        print(f"\n💡 使用建議：")
        print(f"   1. 開啟生成的檔案檢視三個選項")
        print(f"   2. 選擇最適合當日社群策略的選項")
        print(f"   3. 根據平台調整文案與圖片")
        print(f"   4. 發布前進行事實與法律檢查")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
