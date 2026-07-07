# 響應式字級建議

## 字級調整策略

### Mobile (< 640px)
- Hero Title: 3xl (1.875rem / 30px)
- Page Title: 2xl (1.5rem / 24px)
- Section Title: xl (1.25rem / 20px)
- Body: base (1rem / 16px)
- Small: sm (0.875rem / 14px)

### Tablet (640px - 1024px)
- Hero Title: 4xl (2.25rem / 36px)
- Page Title: 3xl (1.875rem / 30px)
- Section Title: 2xl (1.5rem / 24px)
- Body: base (1rem / 16px)
- Small: sm (0.875rem / 14px)

### Desktop (> 1024px)
- Hero Title: 6xl (3.75rem / 60px)
- Page Title: 4xl (2.25rem / 36px)
- Section Title: 2xl (1.5rem / 24px)
- Body: lg (1.125rem / 18px)
- Small: base (1rem / 16px)

## Tailwind CSS 實作

```css
/* Hero Title */
.hero-title {
  @apply text-3xl md:text-4xl lg:text-6xl;
  @apply font-bold font-sans;
  @apply leading-tight;
}

/* Page Title */
.page-title {
  @apply text-2xl md:text-3xl lg:text-4xl;
  @apply font-bold font-sans;
  @apply leading-tight;
}

/* Section Title */
.section-title {
  @apply text-xl md:text-2xl;
  @apply font-semibold font-sans;
  @apply leading-normal;
}

/* Body Text */
.body-text {
  @apply text-base lg:text-lg;
  @apply font-normal font-serif;
  @apply leading-relaxed;
}

/* Small Text */
.small-text {
  @apply text-sm lg:text-base;
  @apply font-normal font-sans;
  @apply leading-normal;
}
```

## 行高調整

- **標題**: 使用 `leading-tight` (1.25) 保持緊湊
- **內文**: 使用 `leading-relaxed` (1.75) 提升可讀性
- **引言**: 使用 `leading-loose` (2) 增加呼吸感

## 字重調整

- **Mobile**: 標題使用 `font-semibold` (600) 避免過重
- **Desktop**: 標題可使用 `font-bold` (700) 增強視覺衝擊

## 最佳實踐

1. **漸進增強**: 從 mobile 開始，逐步增大字級
2. **可讀性優先**: 確保最小字級 ≥ 14px (0.875rem)
3. **對比度**: 標題與內文字級差異 ≥ 1.5 倍
4. **一致性**: 同層級標題使用相同字級
