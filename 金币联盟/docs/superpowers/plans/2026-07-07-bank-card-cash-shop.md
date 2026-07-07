# Bank Card Cash Shop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bank card recharge, cash product purchases that reward coins, and a separate points mall for coin redemption.

**Architecture:** Keep the existing SQL Server business schema stable. Store bank cards, wallet balance, recharge records, and cash purchase orders in local JSON files under `docs/`, while continuing to update `Account.ValidCoin` when purchases reward coins. Existing `GiftInfo` and `AddOrder` remain the source for points redemption.

**Tech Stack:** Flask, Jinja2, CSS, SQL Server via pyodbc, local JSON files.

## Global Constraints

- Keep existing user login and merchant login behavior.
- Do not change the SQL Server physical schema.
- Cash purchases must increase the current user's coin balance.
- Points mall must use existing gift redemption logic.
- UI copy must clearly separate cash purchase from coin redemption.

---

### Task 1: Service Layer

**Files:**
- Modify: `services/mall_service.py`

**Interfaces:**
- Produces: `payment_data(customer_id)`, `bind_bank_card(form, customer_id)`, `recharge_wallet(form, customer_id)`, `cash_shop_data(customer_id)`, `buy_cash_product(form, customer_id, account_id)`, `grant_coin(account_id, coin, reason)`

- [ ] Add local JSON helpers for wallet data.
- [ ] Add static cash product catalog with price and reward coin values.
- [ ] Add card binding validation and masked card display.
- [ ] Add wallet recharge validation and balance update.
- [ ] Add cash product purchase validation, balance deduction, order record, and coin reward.

### Task 2: Routes

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: service functions from Task 1.
- Produces: `/wallet`, `/shop`, `/points-mall`.

- [ ] Add user-only wallet route for card binding and recharge.
- [ ] Add user-only cash shop route for purchases.
- [ ] Add user-only points mall route for coin redemption.
- [ ] Keep `/gifts` available by redirecting or rendering the points mall.

### Task 3: Templates and Styles

**Files:**
- Create: `templates/wallet.html`
- Create: `templates/shop.html`
- Create: `templates/points_mall.html`
- Modify: `templates/base.html`
- Modify: `templates/index.html`
- Modify: `static/css/mall.css`

**Interfaces:**
- Consumes: route context dictionaries.
- Produces: usable wallet, cash shop, and points mall screens.

- [ ] Add role-specific nav items: 现金商城, 银行卡充值, 积分商城.
- [ ] Update home hero CTAs to cash purchase and coin redemption.
- [ ] Build wallet cards, recharge form, and transaction history.
- [ ] Build cash product grid with price and reward coin.
- [ ] Build points product grid with coin price and stock.
- [ ] Add responsive CSS without breaking existing pages.

### Task 4: Documentation and Verification

**Files:**
- Modify: `README.md`
- Modify: `../README.md`

- [ ] Document the new business flow.
- [ ] Run Python compilation.
- [ ] Restart port 5102.
- [ ] Verify `/`, `/shop`, `/wallet`, and `/points-mall` over HTTP.
