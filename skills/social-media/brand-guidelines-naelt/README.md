# NAELT Brand Guidelines Skill

## 概述

這是 NAELT（台灣生命權平等協會）的官方品牌指南 skill，提供完整的品牌識別系統、設計規範和應用範例。

## 結構

```
brand-guidelines-naelt/
├── SKILL.md                              # 主要 skill 文件
├── README.md                             # 本文件
└── code/                                 # 程式碼和參考資料
    ├── colors-primary.json               # 主色調定義
    ├── colors-secondary.json             # 次要色調定義
    ├── colors-accent.json                # 強調色調定義
    ├── colors-status.json                # 狀態顏色定義
    ├── typography-fonts.json             # 字體配置
    ├── typography-scale.json             # 字級系統
    ├── spacing-system.json               # 間距系統
    ├── border-radius.json                # 圓角系統
    ├── shadows.json                      # 陰影系統
    ├── breakpoints.json                  # 斷點系統
    ├── responsive-typography.md          # 響應式字級指南
    ├── css-variables.css                 # CSS 變數定義
    ├── tailwind.config.js                # Tailwind 配置
    ├── react-button-component.tsx        # React 按鈕元件
    ├── example-homepage.html             # 首頁範例
    ├── example-advocacy-poster.md        # 倡議文宣設計指南
    └── example-social-media.md           # 社群媒體素材規範
```

## 使用方式

### 1. 查看品牌顏色

```bash
# 查看主色調
cat code/colors-primary.json

# 查看次要色調
cat code/colors-secondary.json

# 查看強調色調
cat code/colors-accent.json
```

### 2. 使用 CSS 變數

```html
<link rel="stylesheet" href="code/css-variables.css">

<button class="naelt-button-primary">立即捐款</button>
```

### 3. 配置 Tailwind CSS

```javascript
// 複製 tailwind.config.js 到專案根目錄
cp code/tailwind.config.js ./tailwind.config.js
```

### 4. 使用 React 元件

```tsx
import { NAELTButton } from './code/react-button-component';

<NAELTButton variant="primary" size="lg">
  立即捐款
</NAELTButton>
```

### 5. 參考設計範例

- **首頁設計**: `code/example-homepage.html`
- **倡議文宣**: `code/example-advocacy-poster.md`
- **社群媒體**: `code/example-social-media.md`

## 核心品牌元素

### 顏色系統
- **主色調**: 紅色系（象徵生命與正義）
- **次要色調**: 灰色系（專業與穩重）
- **強調色調**: 橙色系（溫暖與希望）

### 字體系統
- **標題**: Noto Sans TC（黑體）
- **內文**: Noto Serif TC（明體）
- **程式碼**: Fira Code（等寬）

### 設計原則
1. **莊重**: 尊重生命，傳達嚴肅議題的重要性
2. **專業**: 展現組織的專業性與可信度
3. **溫暖**: 提供支持與希望，避免過度冰冷
4. **清晰**: 資訊傳達直接明確，易於理解

## 無障礙設計

所有設計元素符合 WCAG 2.1 AA 標準：
- 色彩對比度 ≥ 4.5:1
- 最小字級 14px
- 鍵盤導覽支援
- 螢幕閱讀器友善

## 相關資源

- **官方網站**: https://www.naelt.org
- **Facebook**: https://www.facebook.com/profile.php?id=61576194712668
- **Instagram**: https://www.instagram.com/naelt_org
- **Email**: equalityforlife.tw@gmail.com

## 維護

- **版本**: 1.0.0
- **最後更新**: 2026-03-07
- **維護者**: NAELT Development Team

## 授權

MIT License
