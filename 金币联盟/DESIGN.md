# 金币联盟复刻系统 DESIGN.md

## 1. Visual Theme & Atmosphere

现代响应式商城复刻，保留原金币联盟识别：棕色顶部导航、紫色背景氛围、黄色金币商品区、JBI logo、ZS 横幅、商品九宫格和频道图区。整体比原 ASP.NET 页面更整齐、更轻盈。

## 2. Color Palette & Roles

```css
:root {
  --bg: #635c85;
  --nav: #b87442;
  --coin: #dbb400;
  --surface: #fffaf0;
  --text: #351f14;
  --muted: #7c5d4a;
  --purple: #67497d;
  --purple-rgb: 103, 73, 125;
  --line: #e4c56b;
  --danger: #d92d20;
}
```

## 3. Typography Rules

Use `"Microsoft YaHei", "Segoe UI", Arial, sans-serif`. Product titles 15px, navigation 14px, page headings 28px. Keep original Chinese copy where available.

## 4. Component Stylings

Product cards use 8px radius, warm surface, image aspect ratio 1:1, coin price in purple. Buttons use yellow fill with purple text, clear hover elevation, active pressed state, disabled muted style.

## 5. Layout Principles

Header, banner, action buttons, tab nav, product grid, channel strip, footer. Product grid is 3 columns desktop, 2 tablet, 1 mobile. Channel cards are 5 columns desktop and scroll horizontally on mobile.

## 6. Depth & Elevation

Use warm shadows: `0 12px 28px rgba(53,31,20,.16)`. Avoid dark overlays on product images.

## 7. Animation & Interaction

Interaction level L2. Use soft hover lift on products, nav underline movement, cart count feedback, and fade-in page sections. No heavy JS framework.

## 8. Do's and Don'ts

Do preserve original colors and assets. Do keep商品九宫格 prominent. Do make forms clean and usable. Do not turn it into a generic SaaS page, hide the original logo, crop product assets aggressively, add marketing hero copy, or use unrelated stock images.

## 9. Responsive Behavior

Below 760px, nav wraps, banner keeps full width, action buttons stay touch-friendly, and product/card text remains within containers.
