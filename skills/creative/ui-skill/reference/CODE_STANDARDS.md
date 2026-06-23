# HTML/CSS/JS 程式碼規範

## HTML規範

### 基本規則
- 使用語义化標籤
- 標籤必須正确闭合
- 屬性使用双引號
- 合理的缩進（2空格或4空格）

### 示例
```html
<div class="container">
    <header class="page-header">
        <h1>頁面標題</h1>
    </header>
    <main class="content">
        <!-- 主要內容 -->
    </main>
</div>
```

## CSS規範

### 基本規則
- 使用class選擇器，避免过度使用ID選擇器
- 遵循BEM命名規範（可选）
- 按功能模組組織CSS
- 合理使用CSS變量

### 示例
```css
/* 基础樣式 */
.container {
    max-width: 1200px;
    margin: 0 auto;
}

/* 組件樣式 */
.btn-primary {
    background: #E94609;
    color: white;
    padding: 8px 16px;
}
```

## JavaScript規範

### 基本規則
- 使用const/let，避免使用var
- 函數命名使用驼峰命名法
- 添加必要的註解
- 避免全域變量污染

### 示例
```javascript
// 資料定義
const mockData = [];

// 功能函數
function loadData() {
    // 實作邏輯
}
```

## 註解規範

### HTML註解
```html
<!-- 篩選区域 -->
<div class="filter-section">
    <!-- 內容 -->
</div>
```

### JavaScript註解
```javascript
/**
 * 搜尋清單格
 * @description 根据篩選條件搜尋資料
 */
function searchList() {
    // 實作
}
```
