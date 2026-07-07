# 积分平台业务系统 DESIGN.md

## 1. Visual Theme & Atmosphere

后台业务管理系统，视觉关键词为清晰、高密度、可扫描、稳定。整体采用浅色工作台风格，重点服务表格录入、筛选、状态判断和批量操作，不做营销页和大幅装饰。

## 2. Color Palette & Roles

```css
:root {
  --bg: #f5f7fb;
  --surface: #ffffff;
  --surface-muted: #eef3f8;
  --text: #172033;
  --text-muted: #667085;
  --line: #d9e2ec;
  --primary: #2364d2;
  --primary-rgb: 35, 100, 210;
  --success: #188a42;
  --warning: #b7791f;
  --danger: #c2413b;
  --accent: #0f766e;
}
```

## 3. Typography Rules

Use system sans-serif: `-apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", Arial, sans-serif`. Page titles 24px, section titles 18px, table text 14px, helper text 12px. No decorative fonts.

## 4. Component Stylings

Buttons use 6px radius, 36px height, clear focus ring, disabled opacity 0.55. Cards use 8px radius, 1px border, no nested cards. Tables use sticky headers where possible, compact row height, status tags with semantic colors.

## 5. Layout Principles

Left sidebar width 232px, top content header, main content max width unrestricted for tables. Forms use two-column grid on desktop and single column on mobile. Data pages place filters above tables.

## 6. Depth & Elevation

Use restrained shadows only for navigation and pop panels: `0 8px 24px rgba(23,32,51,.08)`. Avoid floating decorative cards.

## 7. Animation & Interaction

Interaction level L1/L2. Use 120ms hover transitions, subtle row hover, and non-blocking flash messages. No scroll-jacking or heavy animation.

## 8. Do's and Don'ts

Do use dense tables, clear labels, visible empty states, semantic status chips, and predictable forms. Do not use hero sections, large marketing copy, nested cards, decorative gradient blobs, hidden primary actions, or chart-only navigation.

## 9. Responsive Behavior

Below 860px, sidebar becomes horizontal nav, forms collapse to one column, tables use horizontal overflow, and primary actions remain above the fold.
