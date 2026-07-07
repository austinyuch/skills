#!/usr/bin/env python3
"""
Tag 命名標準檢查工具 (Tag Naming Standards Validator)

確保 Tag 命名的一致性，減少 FMEA 中的 "Tag 不一致" 風險。
"""

import re
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class TagValidationResult:
    tag: str
    is_valid: bool
    issues: List[str]
    suggestions: List[str]


class TagValidator:
    """Tag 命名驗證器"""

    # 標準 Tag 詞典
    STANDARD_TAGS = {
        # 主題分類
        "司法不公",
        "家屬權益",
        "人權活動",
        "案件追蹤",
        "國際案例",
        "修法倡議",
        "賠償爭議",
        "立法倡議",
        "司法改善",
        # 立法司法專屬
        "法案進展",
        "司改進展",
        "制度建立",
        "修法通過",
        "修法審查中",
        "政策倡議",
        "國際公約",
        # 角色立場
        "NPO發聲",
        "政黨立場",
        "法界觀點",
        # 狀態標籤
        "進行中",
        "待開庭",
        "上訴中",
        "已判決",
        "已結案",
        "持續關注",
        # 重要性
        "重大案件",
        "社會關注",
        "人權侵害",
        "制度缺陷",
        # 關係類型
        "同盟",
        "對立",
        "聯合聲明",
        "公開辯論",
        "上下級",
    }

    # 角色類型前綴
    ROLE_PREFIXES = {"@組織", "@政黨", "@立委", "@法官", "@檢察官", "@律師", "@官員"}

    def __init__(self):
        self.rules = [
            (self._check_hash_prefix, "必須以 # 或 @ 開頭"),
            (self._check_no_spaces, "不得包含空格"),
            (self._check_no_special_chars, "不得包含特殊字元（除 # @ 外）"),
            (self._check_length, "長度應在 2-15 字之間"),
            (self._check_not_empty, "不得為空"),
        ]

    def validate(self, tag: str) -> TagValidationResult:
        """驗證單個 Tag"""
        issues = []
        suggestions = []

        for rule_func, rule_desc in self.rules:
            result, message = rule_func(tag)
            if not result:
                issues.append(f"❌ {rule_desc}: {message}")

        # 提供建議
        suggestions.extend(self._suggest_improvements(tag))

        # 檢查是否為標準 Tag
        if tag.startswith("#") and tag[1:] in self.STANDARD_TAGS:
            suggestions.append("✅ 此為標準 Tag，建議優先使用")

        is_valid = len(issues) == 0

        return TagValidationResult(
            tag=tag, is_valid=is_valid, issues=issues, suggestions=suggestions
        )

    def validate_batch(self, tags: List[str]) -> List[TagValidationResult]:
        """批次驗證多個 Tag"""
        return [self.validate(tag) for tag in tags]

    def _check_hash_prefix(self, tag: str) -> Tuple[bool, str]:
        """檢查前綴"""
        if not tag.startswith("#") and not tag.startswith("@"):
            return False, f"Tag '{tag}' 必須以 # 或 @ 開頭"
        return True, ""

    def _check_no_spaces(self, tag: str) -> Tuple[bool, str]:
        """檢查空格"""
        if " " in tag or "　" in tag:
            return (
                False,
                f"包含空格，建議改為: {tag.replace(' ', '').replace('　', '')}",
            )
        return True, ""

    def _check_no_special_chars(self, tag: str) -> Tuple[bool, str]:
        """檢查特殊字元"""
        # 允許的中文字元、英文字母、數字
        allowed_pattern = r"^[@#\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\w]+$"

        if not re.match(allowed_pattern, tag):
            invalid_chars = re.findall(
                r"[^@#\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\w]", tag
            )
            return False, f"包含特殊字元: {set(invalid_chars)}"
        return True, ""

    def _check_length(self, tag: str) -> Tuple[bool, str]:
        """檢查長度"""
        # 移除前綴後計算
        content = tag[1:] if tag.startswith("#") or tag.startswith("@") else tag

        if len(content) < 2:
            return False, f"過短（{len(content)} 字），建議增加描述性"
        if len(content) > 15:
            return False, f"過長（{len(content)} 字），建議縮短為 2-6 字"
        return True, ""

    def _check_not_empty(self, tag: str) -> Tuple[bool, str]:
        """檢查非空"""
        if not tag or len(tag) <= 1:
            return False, "Tag 內容為空"
        return True, ""

    def _suggest_improvements(self, tag: str) -> List[str]:
        """提供改善建議"""
        suggestions = []

        # 檢查是否為變體
        content = tag[1:] if tag.startswith("#") or tag.startswith("@") else tag

        # 檢查相似標準 Tag
        for std_tag in self.STANDARD_TAGS:
            if std_tag in content or content in std_tag:
                if content != std_tag:
                    suggestions.append(f"💡 是否意指標準 Tag: #{std_tag}？")

        # 檢查常見錯誤
        if "案件" in content and "案件追蹤" not in content:
            suggestions.append(f"💡 案件相關建議使用: #案件追蹤 + #[案件名稱]")

        if "司法" in content and content not in ["司法不公", "司法改善", "司法改革"]:
            suggestions.append(f"💡 司法相關建議使用: #司法不公 或 #司法改善")

        # 檢查角色 Tag
        if tag.startswith("@"):
            prefix = tag.split("_")[0] if "_" in tag else tag
            if prefix not in self.ROLE_PREFIXES:
                suggestions.append(
                    f"💡 角色 Tag 建議使用標準前綴: @組織、@政黨、@立委、@法官、@檢察官、@律師、@官員"
                )

        return suggestions

    def get_standard_tags(self) -> Dict[str, List[str]]:
        """取得標準 Tag 分類清單"""
        return {
            "主題分類": [
                "司法不公",
                "家屬權益",
                "人權活動",
                "案件追蹤",
                "國際案例",
                "修法倡議",
                "賠償爭議",
                "立法倡議",
                "司法改善",
            ],
            "立法司法": [
                "法案進展",
                "司改進展",
                "制度建立",
                "修法通過",
                "修法審查中",
                "政策倡議",
                "國際公約",
            ],
            "角色立場": ["NPO發聲", "政黨立場", "法界觀點"],
            "案件狀態": ["進行中", "待開庭", "上訴中", "已判決", "已結案", "持續關注"],
            "重要性": ["重大案件", "社會關注", "人權侵害", "制度缺陷"],
            "關係類型": ["同盟", "對立", "聯合聲明", "公開辯論", "上下級"],
        }

    def suggest_tag(self, description: str) -> List[str]:
        """根據描述建議 Tag"""
        suggestions = []
        desc_lower = description.lower()

        # 關鍵詞映射
        keyword_mapping = {
            "司法不公": ["司法", "不公", "偏向", "輕判"],
            "家屬權益": ["家屬", "權益", "權利", "聲音"],
            "人權活動": ["活動", "記者會", "遊行", "倡議"],
            "案件追蹤": ["案件", "追蹤", "進展", "後續"],
            "修法倡議": ["修法", "立法", "法案", "草案"],
            "司法改善": ["改革", "改善", "制度"],
        }

        for tag, keywords in keyword_mapping.items():
            if any(kw in desc_lower for kw in keywords):
                suggestions.append(f"#{tag}")

        return list(set(suggestions))  # 去重


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tag 命名標準檢查工具")
    parser.add_argument("--validate", type=str, help="驗證單個 Tag")
    parser.add_argument("--batch", type=str, nargs="+", help="批次驗證多個 Tag")
    parser.add_argument("--suggest", type=str, help="根據描述建議 Tag")
    parser.add_argument(
        "--list-standards", action="store_true", help="列出標準 Tag 清單"
    )

    args = parser.parse_args()

    validator = TagValidator()

    if args.validate:
        result = validator.validate(args.validate)
        print(f"\n檢查結果: {result.tag}")
        print(f"狀態: {'✅ 有效' if result.is_valid else '❌ 無效'}")

        if result.issues:
            print("\n問題:")
            for issue in result.issues:
                print(f"  {issue}")

        if result.suggestions:
            print("\n建議:")
            for suggestion in result.suggestions:
                print(f"  {suggestion}")

    elif args.batch:
        results = validator.validate_batch(args.batch)
        print("\n批次驗證結果:")
        for result in results:
            status = "✅" if result.is_valid else "❌"
            print(f"\n{status} {result.tag}")
            if result.issues:
                for issue in result.issues[:2]:  # 只顯示前2個問題
                    print(f"   {issue}")

    elif args.suggest:
        suggestions = validator.suggest_tag(args.suggest)
        print(f"\n針對描述 '{args.suggest}' 的建議 Tag:")
        for tag in suggestions:
            print(f"  {tag}")

    elif args.list_standards:
        standards = validator.get_standard_tags()
        print("\n標準 Tag 清單:")
        for category, tags in standards.items():
            print(f"\n【{category}】")
            for tag in tags:
                print(f"  #{tag}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
