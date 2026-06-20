# Toolbox Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增工具箱首页 + 税点计算器 + 人民币大写转换器，共 3 个静态 HTML 页面，用 Playwright TDD 验证，最终推送到 GitHub Pages。

**Architecture:** 扁平结构 — 所有 HTML 文件放在仓库根目录，通过相对路径互相链接。每个页面独立自包含（内联 CSS + JS），零外部依赖。现有 index.html 重命名为 lung-marker.html。

**Tech Stack:** Plain HTML/CSS/JS, Playwright (Python) for testing, GitHub Pages for deployment.

---

### Task 1: 重命名现有 index.html → lung-marker.html 并更新测试

**Files:**
- Rename: `index.html` → `lung-marker.html`
- Modify: `test_lung_marker.py:5`

- [ ] **Step 1: 重命名文件**

```powershell
Move-Item index.html lung-marker.html
```

- [ ] **Step 2: 更新测试中的文件路径引用**

在 `test_lung_marker.py` 第 5 行，将：
```python
FILE_URL = "file:///C:/Users/unpyp/Desktop/work/temp/lung-segment-marker.html"
```
改为：
```python
FILE_URL = "file:///C:/Users/unpyp/Desktop/work/temp/lung_marker/lung-marker.html"
```

- [ ] **Step 3: 运行测试确认无回归**

```powershell
uv run python test_lung_marker.py
```
Expected: ALL TESTS PASSED

- [ ] **Step 4: Commit**

```bash
git add lung-marker.html index.html test_lung_marker.py
git commit -m "Rename index.html to lung-marker.html, fix test path"
```

---

### Task 2: 编写税点计算器测试 (TDD — RED)

**Files:**
- Create: `test_tax_calc.py`

- [ ] **Step 1: 写入失败测试**

```python
"""Test the tax point calculator page."""
from playwright.sync_api import sync_playwright

FILE_URL = "file:///C:/Users/unpyp/Desktop/work/temp/lung_marker/tax-calc.html"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
        )
        page = context.new_page()
        page.goto(FILE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        errors = []

        # Test 1: Page loads with title
        title = page.title()
        if not title:
            errors.append("Page title is empty")
        else:
            print(f"[OK] Page title: {title}")

        # Test 2: Amount input exists
        amount_input = page.locator("#amountInput")
        if amount_input.count() != 1:
            errors.append("Amount input #amountInput not found")
        else:
            print("[OK] Amount input found")

        # Test 3: Tax rate dropdown exists with options including custom
        rate_select = page.locator("#rateSelect")
        if rate_select.count() != 1:
            errors.append("Rate select #rateSelect not found")
        else:
            options = rate_select.locator("option")
            count = options.count()
            if count < 6:
                errors.append(f"Expected at least 6 options (5 rates + custom), got {count}")
            else:
                print(f"[OK] Rate select has {count} options")

        # Test 4: Custom rate input hidden by default
        custom_input = page.locator("#customRateInput")
        if custom_input.count() != 1:
            errors.append("Custom rate input #customRateInput not found")
        elif custom_input.is_visible():
            errors.append("Custom rate input should be hidden by default")
        else:
            print("[OK] Custom rate input hidden by default")

        # Test 5: Select "custom" shows custom input
        rate_select.select_option("custom")
        page.wait_for_timeout(200)
        if not custom_input.is_visible():
            errors.append("Custom rate input should be visible after selecting custom")
        else:
            print("[OK] Custom rate input shown when custom selected")

        # Test 6: Calculation correctness — 含税 11300, 税率 13%
        rate_select.select_option("0.13")
        page.wait_for_timeout(100)
        amount_input.fill("11300")
        page.wait_for_timeout(200)

        pre_tax = page.locator("#preTaxAmount")
        tax_amount = page.locator("#taxAmount")
        if pre_tax.count() != 1:
            errors.append("Pre-tax amount element #preTaxAmount not found")
        if tax_amount.count() != 1:
            errors.append("Tax amount element #taxAmount not found")
        else:
            pre_tax_text = pre_tax.inner_text()
            tax_amount_text = tax_amount.inner_text()
            # 11300 / 1.13 = 10000
            if "10000" not in pre_tax_text:
                errors.append(f"Expected pre-tax ~10000, got '{pre_tax_text}'")
            else:
                print(f"[OK] Pre-tax amount: {pre_tax_text}")
            if "1300" not in tax_amount_text:
                errors.append(f"Expected tax ~1300, got '{tax_amount_text}'")
            else:
                print(f"[OK] Tax amount: {tax_amount_text}")

        # Test 7: Calculation with 5% rate — 含税 10500
        rate_select.select_option("0.05")
        page.wait_for_timeout(100)
        amount_input.fill("10500")
        page.wait_for_timeout(200)
        pre_tax_text = pre_tax.inner_text()
        tax_amount_text = tax_amount.inner_text()
        # 10500 / 1.05 = 10000
        if "10000" not in pre_tax_text:
            errors.append(f"5% test: Expected pre-tax ~10000, got '{pre_tax_text}'")
        else:
            print(f"[OK] 5% Pre-tax: {pre_tax_text}")
        if "500" not in tax_amount_text:
            errors.append(f"5% test: Expected tax ~500, got '{tax_amount_text}'")
        else:
            print(f"[OK] 5% Tax: {tax_amount_text}")

        # Test 8: Copy buttons exist
        copy_btns = page.locator(".copy-btn")
        if copy_btns.count() < 2:
            errors.append(f"Expected at least 2 copy buttons, got {copy_btns.count()}")
        else:
            print(f"[OK] {copy_btns.count()} copy buttons found")

        # Test 9: Back link exists
        back_link = page.locator("a.back-link")
        if back_link.count() != 1:
            errors.append("Back link a.back-link not found")
        else:
            href = back_link.get_attribute("href")
            if href != "./index.html":
                errors.append(f"Back link href expected './index.html', got '{href}'")
            else:
                print(f"[OK] Back link: {href}")

        if errors:
            print(f"\n=== {len(errors)} ERROR(S) ===")
            for e in errors:
                print(f"  FAIL: {e}")
            browser.close()
            raise SystemExit(1)
        else:
            print("\n=== ALL TESTS PASSED ===")
            browser.close()


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run python test_tax_calc.py
```
Expected: FAIL (file missing or elements not found)

- [ ] **Step 3: Commit**

```bash
git add test_tax_calc.py
git commit -m "Add failing tax calculator tests (TDD RED)"
```

---

### Task 3: 实现税点计算器 (TDD — GREEN)

**Files:**
- Create: `tax-calc.html`

- [ ] **Step 1: 创建 tax-calc.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>税点计算器</title>
<style>
  :root {
    --bg: #f5f2ed;
    --card: #ffffff;
    --text: #2c2826;
    --text-secondary: #7a736d;
    --teal: #0d9488;
    --teal-light: #ccfbf1;
    --gold: #d97706;
    --gold-bg: #fef3c7;
    --danger: #dc2626;
    --danger-light: #fee2e2;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);
    --radius: 20px;
    --radius-sm: 12px;
    --font-display: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
    --font-body: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-body);
    background: var(--bg);
    background-image:
      radial-gradient(ellipse at 50% 0%, rgba(13,148,136,0.04) 0%, transparent 60%),
      radial-gradient(ellipse at 85% 100%, rgba(124,58,237,0.03) 0%, transparent 50%);
    min-height: 100dvh;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 16px;
    -webkit-tap-highlight-color: transparent;
  }

  .container {
    width: 100%;
    max-width: 420px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    animation: fadeIn 0.4s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  a.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    width: fit-content;
    transition: color 0.2s;
  }
  a.back-link:active { color: var(--teal); }

  .card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card h2 {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .input-group label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .input-group input, .input-group select {
    padding: 12px 14px;
    border-radius: var(--radius-sm);
    border: 2px solid #e5e0da;
    font-size: 1rem;
    font-family: var(--font-body);
    background: #faf9f7;
    outline: none;
    transition: border-color 0.2s;
    width: 100%;
  }
  .input-group input:focus, .input-group select:focus {
    border-color: var(--teal);
    background: #fff;
  }

  #customRateInput {
    display: none;
    margin-top: 8px;
  }
  #customRateInput.show {
    display: block;
  }

  .result-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    background: #f8f6f3;
    border-radius: var(--radius-sm);
    gap: 10px;
  }

  .result-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
    white-space: nowrap;
  }

  .result-value {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--text);
    flex: 1;
    text-align: right;
    letter-spacing: 0.02em;
  }

  .copy-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 20px;
    border: 1.5px solid #e5e0da;
    background: #fff;
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
    flex-shrink: 0;
  }
  .copy-btn:active { transform: scale(0.95); }
  .copy-btn.copied {
    background: var(--teal-light);
    border-color: var(--teal);
    color: var(--teal);
  }

  .invoice-preview {
    text-align: center;
    padding: 12px;
  }

  .invoice-preview .sep {
    color: #ccc;
    margin: 0 8px;
  }
</style>
</head>
<body>

<div class="container">
  <a class="back-link" href="./index.html">&#x2190; 返回工具箱</a>

  <div class="card">
    <h2>税点计算器</h2>

    <div class="input-group">
      <label for="amountInput">合同金额（含税）</label>
      <input type="number" id="amountInput" placeholder="输入含税总金额" inputmode="decimal">
    </div>

    <div class="input-group">
      <label for="rateSelect">税率</label>
      <select id="rateSelect">
        <option value="0.13">13%</option>
        <option value="0.09">9%</option>
        <option value="0.06">6%</option>
        <option value="0.05">5%</option>
        <option value="0.01">1%</option>
        <option value="custom">自定义</option>
      </select>
      <input type="number" id="customRateInput" placeholder="输入自定义税率 (%)" inputmode="decimal" step="0.01">
    </div>

    <div class="result-row">
      <span class="result-label">税前金额</span>
      <span class="result-value" id="preTaxAmount">—</span>
      <button class="copy-btn" data-target="preTaxAmount">复制</button>
    </div>

    <div class="result-row">
      <span class="result-label">税点金额</span>
      <span class="result-value" id="taxAmount">—</span>
      <button class="copy-btn" data-target="taxAmount">复制</button>
    </div>
  </div>
</div>

<script>
(function() {
  const amountInput = document.getElementById('amountInput');
  const rateSelect = document.getElementById('rateSelect');
  const customRateInput = document.getElementById('customRateInput');
  const preTaxEl = document.getElementById('preTaxAmount');
  const taxEl = document.getElementById('taxAmount');

  function formatMoney(n) {
    return n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  function calc() {
    const amount = parseFloat(amountInput.value);
    if (isNaN(amount) || amount <= 0) {
      preTaxEl.textContent = '—';
      taxEl.textContent = '—';
      return;
    }

    let rate;
    if (rateSelect.value === 'custom') {
      const customVal = parseFloat(customRateInput.value);
      if (isNaN(customVal) || customVal < 0) {
        preTaxEl.textContent = '—';
        taxEl.textContent = '—';
        return;
      }
      rate = customVal / 100;
    } else {
      rate = parseFloat(rateSelect.value);
    }

    const preTax = amount / (1 + rate);
    const tax = amount - preTax;

    preTaxEl.textContent = formatMoney(preTax);
    taxEl.textContent = formatMoney(tax);
  }

  rateSelect.addEventListener('change', function() {
    if (this.value === 'custom') {
      customRateInput.classList.add('show');
    } else {
      customRateInput.classList.remove('show');
    }
    calc();
  });

  amountInput.addEventListener('input', calc);
  customRateInput.addEventListener('input', calc);

  // Copy buttons
  document.querySelectorAll('.copy-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var targetId = this.dataset.target;
      var el = document.getElementById(targetId);
      var text = el.textContent;
      if (text === '—') return;

      navigator.clipboard.writeText(text).then(function() {
        btn.textContent = '已复制';
        btn.classList.add('copied');
        setTimeout(function() {
          btn.textContent = '复制';
          btn.classList.remove('copied');
        }, 1500);
      }).catch(function() {
        // Fallback
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        btn.textContent = '已复制';
        btn.classList.add('copied');
        setTimeout(function() {
          btn.textContent = '复制';
          btn.classList.remove('copied');
        }, 1500);
      });
    });
  });
})();
</script>
</body>
</html>
```

- [ ] **Step 2: 运行测试确认通过**

```powershell
uv run python test_tax_calc.py
```
Expected: ALL TESTS PASSED

- [ ] **Step 3: Commit**

```bash
git add tax-calc.html
git commit -m "Add tax calculator page"
```

---

### Task 4: 编写人民币大写转换器测试 (TDD — RED)

**Files:**
- Create: `test_rmb_upper.py`

- [ ] **Step 1: 写入失败测试**

```python
"""Test the RMB uppercase converter page."""
from playwright.sync_api import sync_playwright

FILE_URL = "file:///C:/Users/unpyp/Desktop/work/temp/lung_marker/rmb-upper.html"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
        )
        page = context.new_page()
        page.goto(FILE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        errors = []

        # Test 1: Page loads with title
        title = page.title()
        if not title:
            errors.append("Page title is empty")
        else:
            print(f"[OK] Page title: {title}")

        # Test 2: Amount input exists
        amount_input = page.locator("#amountInput")
        if amount_input.count() != 1:
            errors.append("Amount input #amountInput not found")
        else:
            print("[OK] Amount input found")

        # Test 3: Result element exists
        result_el = page.locator("#result")
        if result_el.count() != 1:
            errors.append("Result element #result not found")
        else:
            print("[OK] Result element found")

        # Test 4: Input 100 → 壹佰元整
        amount_input.fill("100")
        page.wait_for_timeout(200)
        result_text = result_el.inner_text()
        if "壹佰元整" not in result_text:
            errors.append(f"Expected '壹佰元整' for input 100, got '{result_text}'")
        else:
            print(f"[OK] 100 → {result_text}")

        # Test 5: Input 12000 → 壹万贰仟元整
        amount_input.fill("12000")
        page.wait_for_timeout(200)
        result_text = result_el.inner_text()
        if "壹万贰仟元整" not in result_text:
            errors.append(f"Expected '壹万贰仟元整' for input 12000, got '{result_text}'")
        else:
            print(f"[OK] 12000 → {result_text}")

        # Test 6: Input 100.50 → 壹佰元伍角
        amount_input.fill("100.50")
        page.wait_for_timeout(200)
        result_text = result_el.inner_text()
        if "壹佰元" not in result_text:
            errors.append(f"Expected '壹佰元...' for input 100.50, got '{result_text}'")
        elif "伍角" not in result_text:
            errors.append(f"Expected '伍角' in result for 100.50, got '{result_text}'")
        else:
            print(f"[OK] 100.50 → {result_text}")

        # Test 7: Input 0.01 → 壹分
        amount_input.fill("0.01")
        page.wait_for_timeout(200)
        result_text = result_el.inner_text()
        if "壹分" not in result_text:
            errors.append(f"Expected '壹分' for 0.01, got '{result_text}'")
        else:
            print(f"[OK] 0.01 → {result_text}")

        # Test 8: Input 123456789.00 → includes 亿 and 万 and 整
        amount_input.fill("123456789")
        page.wait_for_timeout(200)
        result_text = result_el.inner_text()
        if "亿" not in result_text:
            errors.append(f"Expected '亿' for large number, got '{result_text}'")
        elif "万" not in result_text:
            errors.append(f"Expected '万' for large number, got '{result_text}'")
        else:
            print(f"[OK] 123456789 → {result_text}")

        # Test 9: Copy button exists
        copy_btn = page.locator("#copyBtn")
        if copy_btn.count() != 1:
            errors.append("Copy button #copyBtn not found")
        else:
            print("[OK] Copy button found")

        # Test 10: Back link exists
        back_link = page.locator("a.back-link")
        if back_link.count() != 1:
            errors.append("Back link a.back-link not found")
        else:
            href = back_link.get_attribute("href")
            if href != "./index.html":
                errors.append(f"Back link href expected './index.html', got '{href}'")
            else:
                print(f"[OK] Back link: {href}")

        if errors:
            print(f"\n=== {len(errors)} ERROR(S) ===")
            for e in errors:
                print(f"  FAIL: {e}")
            browser.close()
            raise SystemExit(1)
        else:
            print("\n=== ALL TESTS PASSED ===")
            browser.close()


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run python test_rmb_upper.py
```
Expected: FAIL (file missing or elements not found)

- [ ] **Step 3: Commit**

```bash
git add test_rmb_upper.py
git commit -m "Add failing RMB uppercase converter tests (TDD RED)"
```

---

### Task 5: 实现人民币大写转换器 (TDD — GREEN)

**Files:**
- Create: `rmb-upper.html`

- [ ] **Step 1: 创建 rmb-upper.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>人民币大写转换</title>
<style>
  :root {
    --bg: #f5f2ed;
    --card: #ffffff;
    --text: #2c2826;
    --text-secondary: #7a736d;
    --teal: #0d9488;
    --teal-light: #ccfbf1;
    --gold: #d97706;
    --gold-bg: #fef3c7;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);
    --radius: 20px;
    --radius-sm: 12px;
    --font-display: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
    --font-body: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-body);
    background: var(--bg);
    background-image:
      radial-gradient(ellipse at 50% 0%, rgba(13,148,136,0.04) 0%, transparent 60%),
      radial-gradient(ellipse at 85% 100%, rgba(124,58,237,0.03) 0%, transparent 50%);
    min-height: 100dvh;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 16px;
    -webkit-tap-highlight-color: transparent;
  }

  .container {
    width: 100%;
    max-width: 420px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    animation: fadeIn 0.4s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  a.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    width: fit-content;
    transition: color 0.2s;
  }
  a.back-link:active { color: var(--teal); }

  .card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .card h2 {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .input-group label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .input-group input {
    padding: 12px 14px;
    border-radius: var(--radius-sm);
    border: 2px solid #e5e0da;
    font-size: 1rem;
    font-family: var(--font-body);
    background: #faf9f7;
    outline: none;
    transition: border-color 0.2s;
  }
  .input-group input:focus {
    border-color: var(--teal);
    background: #fff;
  }

  .result-box {
    background: #f8f6f3;
    border-radius: var(--radius-sm);
    padding: 18px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: center;
    min-height: 80px;
    justify-content: center;
  }

  .result-text {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--text);
    letter-spacing: 0.04em;
    word-break: break-all;
    text-align: center;
  }

  .copy-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 8px 18px;
    border-radius: 20px;
    border: 1.5px solid #e5e0da;
    background: #fff;
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }
  .copy-btn:active { transform: scale(0.95); }
  .copy-btn.copied {
    background: var(--teal-light);
    border-color: var(--teal);
    color: var(--teal);
  }
</style>
</head>
<body>

<div class="container">
  <a class="back-link" href="./index.html">&#x2190; 返回工具箱</a>

  <div class="card">
    <h2>人民币大写转换</h2>

    <div class="input-group">
      <label for="amountInput">金额</label>
      <input type="number" id="amountInput" placeholder="输入金额" inputmode="decimal" step="0.01">
    </div>

    <div class="result-box">
      <span class="result-text" id="result">请输入金额</span>
      <button class="copy-btn" id="copyBtn">复制</button>
    </div>
  </div>
</div>

<script>
(function() {
  const DIGITS_CN = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
  const UNITS_INT = ['', '拾', '佰', '仟'];
  const BIG_UNITS = ['', '万', '亿', '兆'];
  const UNITS_DEC = ['角', '分'];

  function convertIntegerPart(n) {
    if (n === '0') return '零';
    var str = '';
    var len = n.length;
    var groups = [];
    // Split into groups of 4 from right
    for (var i = len; i > 0; i -= 4) {
      groups.push(n.substring(Math.max(0, i - 4), i));
    }

    for (var g = groups.length - 1; g >= 0; g--) {
      var group = groups[g];
      var groupStr = '';
      var hasValue = false;
      for (var j = 0; j < group.length; j++) {
        var d = parseInt(group[j]);
        var pos = group.length - 1 - j;
        if (d !== 0) {
          if (groupStr === '' && g < groups.length - 1 && j === 0 && group.length === 4 && str !== '' && str[str.length - 1] !== '零') {
            groupStr += '零';
          }
          groupStr += DIGITS_CN[d] + UNITS_INT[pos];
          hasValue = true;
        } else {
          if (j < group.length - 1 && parseInt(group[j + 1]) !== 0) {
            groupStr += '零';
          }
        }
      }
      if (hasValue) {
        str += groupStr + BIG_UNITS[g];
      }
    }
    // Clean up trailing 零 at big unit boundaries already handled above
    str = str.replace(/零+/g, '零');
    if (str.endsWith('零')) str = str.slice(0, -1);
    return str + '元';
  }

  function convertDecimalPart(d) {
    if (!d || d === '00') return '整';
    var str = '';
    var jiao = parseInt(d[0] || '0');
    var fen = parseInt(d[1] || '0');
    if (jiao > 0) str += DIGITS_CN[jiao] + '角';
    if (fen > 0) str += DIGITS_CN[fen] + '分';
    return str;
  }

  function convert(amount) {
    var parts = amount.toFixed(2).split('.');
    var intPart = parts[0];
    var decPart = parts[1];
    var intStr = convertIntegerPart(intPart);
    var decStr = convertDecimalPart(decPart);

    if (intStr === '零元' && decStr === '整') return '零元整';
    if (intStr === '零元' && decStr !== '整') return decStr;
    return intStr + decStr;
  }

  var amountInput = document.getElementById('amountInput');
  var resultEl = document.getElementById('result');

  amountInput.addEventListener('input', function() {
    var val = parseFloat(this.value);
    if (isNaN(val) || val < 0) {
      resultEl.textContent = '请输入金额';
      return;
    }
    resultEl.textContent = convert(val);
  });

  // Copy button
  document.getElementById('copyBtn').addEventListener('click', function() {
    var text = resultEl.textContent;
    if (text === '请输入金额') return;
    navigator.clipboard.writeText(text).then(function() {
      var btn = document.getElementById('copyBtn');
      btn.textContent = '已复制';
      btn.classList.add('copied');
      setTimeout(function() {
        btn.textContent = '复制';
        btn.classList.remove('copied');
      }, 1500);
    }).catch(function() {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      var btn = document.getElementById('copyBtn');
      btn.textContent = '已复制';
      btn.classList.add('copied');
      setTimeout(function() {
        btn.textContent = '复制';
        btn.classList.remove('copied');
      }, 1500);
    });
  });
})();
</script>
</body>
</html>
```

- [ ] **Step 2: 运行测试确认通过**

```powershell
uv run python test_rmb_upper.py
```
Expected: ALL TESTS PASSED

- [ ] **Step 3: Commit**

```bash
git add rmb-upper.html
git commit -m "Add RMB uppercase converter page"
```

---

### Task 6: 编写工具箱首页测试 (TDD — RED)

**Files:**
- Create: `test_toolbox.py`

- [ ] **Step 1: 写入失败测试**

```python
"""Test the toolbox homepage."""
from playwright.sync_api import sync_playwright

FILE_URL = "file:///C:/Users/unpyp/Desktop/work/temp/lung_marker/index.html"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
        )
        page = context.new_page()
        page.goto(FILE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        errors = []

        # Test 1: Page loads with title
        title = page.title()
        if not title:
            errors.append("Page title is empty")
        else:
            print(f"[OK] Page title: {title}")

        # Test 2: Three tool cards exist
        cards = page.locator(".tool-card")
        card_count = cards.count()
        if card_count != 3:
            errors.append(f"Expected 3 tool cards, got {card_count}")
        else:
            print(f"[OK] {card_count} tool cards found")

        # Test 3: First card links to lung marker
        first_link = cards.nth(0).get_attribute("href")
        if first_link != "./lung-marker.html":
            errors.append(f"Card 0: expected href './lung-marker.html', got '{first_link}'")
        else:
            print(f"[OK] Card 0 → lung-marker.html")

        # Test 4: Second card links to tax calc
        second_link = cards.nth(1).get_attribute("href")
        if second_link != "./tax-calc.html":
            errors.append(f"Card 1: expected href './tax-calc.html', got '{second_link}'")
        else:
            print(f"[OK] Card 1 → tax-calc.html")

        # Test 5: Third card links to RMB converter
        third_link = cards.nth(2).get_attribute("href")
        if third_link != "./rmb-upper.html":
            errors.append(f"Card 2: expected href './rmb-upper.html', got '{third_link}'")
        else:
            print(f"[OK] Card 2 → rmb-upper.html")

        # Test 6: Navigate to lung marker and back
        cards.nth(0).click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        if "右下叶基底段" not in page.title() and "右下叶基底段" not in (page.locator("h1").inner_text() if page.locator("h1").count() > 0 else ""):
            errors.append("Navigation to lung marker page failed or title mismatch")
        else:
            print("[OK] Navigated to lung marker page")

        page.go_back()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        cards2 = page.locator(".tool-card")
        if cards2.count() != 3:
            errors.append("Back navigation to homepage failed")
        else:
            print("[OK] Back navigation to homepage works")

        # Test 7: Navigate to tax calc and back via back link
        cards2.nth(1).click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        back_link = page.locator("a.back-link")
        if back_link.count() != 1:
            errors.append("Tax calc page missing back link after navigation")
        else:
            print("[OK] Tax calc page has back link")
        back_link.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        if page.locator(".tool-card").count() != 3:
            errors.append("Back link to homepage failed")
        else:
            print("[OK] Back link returns to homepage")

        # Test 8: Navigate to RMB converter and back
        cards3 = page.locator(".tool-card")
        cards3.nth(2).click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        back_link2 = page.locator("a.back-link")
        if back_link2.count() != 1:
            errors.append("RMB converter page missing back link after navigation")
        else:
            print("[OK] RMB converter page has back link")
        back_link2.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)
        if page.locator(".tool-card").count() != 3:
            errors.append("Back link from RMB converter to homepage failed")
        else:
            print("[OK] Full navigation cycle works")

        if errors:
            print(f"\n=== {len(errors)} ERROR(S) ===")
            for e in errors:
                print(f"  FAIL: {e}")
            browser.close()
            raise SystemExit(1)
        else:
            print("\n=== ALL TESTS PASSED ===")
            browser.close()


if __name__ == "__main__":
    run()
```

- [ ] **Step 2: 运行测试确认失败**

```powershell
uv run python test_toolbox.py
```
Expected: FAIL (index.html not yet created as toolbox homepage)

- [ ] **Step 3: Commit**

```bash
git add test_toolbox.py
git commit -m "Add failing toolbox homepage tests (TDD RED)"
```

---

### Task 7: 实现工具箱首页 (TDD — GREEN)

**Files:**
- Create: `index.html`

- [ ] **Step 1: 创建 index.html（工具箱首页）**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>工具箱</title>
<style>
  :root {
    --bg: #f5f2ed;
    --card: #ffffff;
    --text: #2c2826;
    --text-secondary: #7a736d;
    --teal: #0d9488;
    --teal-light: #ccfbf1;
    --blue: #2563eb;
    --blue-light: #dbeafe;
    --violet: #7c3aed;
    --violet-light: #ede9fe;
    --gold: #d97706;
    --gold-bg: #fef3c7;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);
    --shadow-lg: 0 10px 30px rgba(0,0,0,0.10), 0 4px 8px rgba(0,0,0,0.05);
    --radius: 20px;
    --radius-sm: 12px;
    --font-display: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
    --font-body: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: var(--font-body);
    background: var(--bg);
    background-image:
      radial-gradient(ellipse at 50% 0%, rgba(13,148,136,0.04) 0%, transparent 60%),
      radial-gradient(ellipse at 85% 100%, rgba(124,58,237,0.03) 0%, transparent 50%);
    min-height: 100dvh;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 16px;
    -webkit-tap-highlight-color: transparent;
    -webkit-user-select: none;
    user-select: none;
  }

  .container {
    width: 100%;
    max-width: 420px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    animation: fadeIn 0.5s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .header {
    background: var(--card);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .header h1 {
    font-family: var(--font-display);
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.02em;
  }

  .header .subtitle {
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
  }

  .tools-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  a.tool-card {
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 18px;
    background: var(--card);
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
    transition: all 0.25s ease;
    -webkit-tap-highlight-color: transparent;
  }
  a.tool-card:active {
    transform: scale(0.98);
    box-shadow: var(--shadow-md);
  }

  .tool-icon {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    flex-shrink: 0;
    font-weight: 900;
  }

  .icon-lung { background: var(--teal-light); color: var(--teal); }
  .icon-tax { background: var(--blue-light); color: var(--blue); }
  .icon-rmb { background: var(--gold-bg); color: var(--gold); }

  .tool-info {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  .tool-info .tool-name {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.02em;
  }

  .tool-info .tool-desc {
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
    line-height: 1.4;
  }

  .tool-arrow {
    margin-left: auto;
    color: #ccc;
    font-size: 1.1rem;
  }

  .footer {
    text-align: center;
    padding: 8px 0 20px;
    font-size: 0.7rem;
    color: #c4bfb8;
  }
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <h1>工具箱</h1>
    <span class="subtitle">实用小工具集合</span>
  </div>

  <div class="tools-grid">
    <a class="tool-card" href="./lung-marker.html">
      <div class="tool-icon icon-lung">&#x1F6AC;</div>
      <div class="tool-info">
        <span class="tool-name">支气管分段标记</span>
        <span class="tool-desc">右下叶基底段顺序标记，支持后悔模式</span>
      </div>
      <span class="tool-arrow">&#x203A;</span>
    </a>

    <a class="tool-card" href="./tax-calc.html">
      <div class="tool-icon icon-tax">&#x1F4B0;</div>
      <div class="tool-info">
        <span class="tool-name">税点计算器</span>
        <span class="tool-desc">含税金额 ÷ 税率，一键算税前与税额</span>
      </div>
      <span class="tool-arrow">&#x203A;</span>
    </a>

    <a class="tool-card" href="./rmb-upper.html">
      <div class="tool-icon icon-rmb">&#x00A5;</div>
      <div class="tool-info">
        <span class="tool-name">人民币大写转换</span>
        <span class="tool-desc">数字金额转大写，符合央行规范</span>
      </div>
      <span class="tool-arrow">&#x203A;</span>
    </a>
  </div>

  <div class="footer">更多工具即将上线</div>
</div>

</body>
</html>
```

- [ ] **Step 2: 运行测试确认通过**

```powershell
uv run python test_toolbox.py
```
Expected: ALL TESTS PASSED

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "Add toolbox homepage"
```

---

### Task 8: 运行全部测试套件

- [ ] **Step 1: 依次运行所有测试**

```powershell
uv run python test_lung_marker.py && uv run python test_tax_calc.py && uv run python test_rmb_upper.py && uv run python test_toolbox.py
```
Expected: ALL TESTS PASSED for each

- [ ] **Step 2: 截图保存（可选冒烟测试留档）**

手动用 Playwright 拍一遍所有页面的截图作为参考。

---

### Task 9: 推送到 GitHub 并配置 Pages

- [ ] **Step 1: 检查 .gitignore 忽略 .venv 和测试产物**

确保 `.gitignore` 包含：
```
.venv/
*.png
__pycache__/
```

- [ ] **Step 2: 推送代码**

```bash
git push origin master
```

- [ ] **Step 3: 确认 GitHub Pages 已启用**

在 GitHub 仓库 Settings → Pages 中：
- Source: Deploy from a branch
- Branch: master, / (root)

- [ ] **Step 4: 访问验证**

URL: `https://<username>.github.io/lung_marker/`

确认三个工具页面均可正常导航和使用。
