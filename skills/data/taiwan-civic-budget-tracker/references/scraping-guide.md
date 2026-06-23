# 爬蟲技術指南

## 概觀

本指南說明如何自動化收集台灣政府預算、標案、公司資料，包含技術選擇、實作範例、與反爬蟲應對策略。

## 爬蟲工具選擇矩陣

| 工具 | 適用情境 | 優點 | 缺點 | 推薦度 |
|-----|---------|------|------|-------|
| **Scrapy** | 大規模、結構化爬取 | 高效能、內建排程、自動重試 | 學習曲線陡峭 | ★★★★★ |
| **Playwright** | 需 JS 渲染、驗證碼 | 真實瀏覽器、可處理複雜互動 | 較耗資源、較慢 | ★★★★★ |
| **Requests + BeautifulSoup** | 簡單靜態頁面 | 輕量、快速、簡單 | 無法處理動態內容 | ★★★★☆ |
| **Selenium** | 需複雜互動 | 功能完整、社群大 | 較慢、資源消耗大 | ★★★☆☆ |
| **httpx** | 非同步大量請求 | 高效能、支援 HTTP/2 | 僅適合 API/靜態頁 | ★★★★☆ |

## 各資料來源爬蟲策略

### 1. 政府電子採購網（PCC）

**建議優先使用公開資料而非爬蟲**

#### 1.1 公開 CSV 下載（推薦）

```python
import pandas as pd
import requests
from datetime import datetime

def download_pcc_opendata(data_type='award', start_date=None, end_date=None):
    """
    下載 PCC 公開資料
    
    data_type: 'tender' (招標) / 'award' (決標)
    """
    base_url = "https://web.pcc.gov.tw/pis/openData/"
    
    if data_type == 'award':
        url = f"{base_url}awardCSV"
    else:
        url = f"{base_url}tenderCSV"
    
    try:
        response = requests.get(url, timeout=60)
        response.encoding = 'utf-8'
        
        # 儲存檔案
        filename = f"pcc_{data_type}_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ 已下載: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return None

# 使用範例
csv_file = download_pcc_opendata('award')
if csv_file:
    df = pd.read_csv(csv_file, encoding='utf-8')
    print(f"共 {len(df)} 筆決標資料")
```

#### 1.2 網頁搜尋爬蟲（備用）

當需要查詢歷史資料或特定關鍵字時：

```python
from playwright.sync_api import sync_playwright
import time

def search_pcc_keywords(keywords, start_date=None, end_date=None):
    """
    搜尋 PCC 特定關鍵字的標案
    
    keywords: 關鍵字列表，如 ['司法改革', '修復式司法']
    """
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        for keyword in keywords:
            try:
                # 進入搜尋頁面
                page.goto('https://web.pcc.gov.tw/pis/')
                
                # 填入關鍵字
                page.fill('input[name="q"] ', keyword)
                
                # 設定日期範圍（如果有）
                if start_date:
                    page.fill('input[name="startDate"]', start_date)
                if end_date:
                    page.fill('input[name="endDate"]', end_date)
                
                # 點擊搜尋
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
                
                # 等待結果載入
                time.sleep(2)
                
                # 提取結果
                rows = page.query_selector_all('table tr')
                for row in rows[1:]:  # 跳過標題
                    cells = row.query_selector_all('td')
                    if len(cells) >= 4:
                        result = {
                            'keyword': keyword,
                            'case_no': cells[0].inner_text(),
                            'case_name': cells[1].inner_text(),
                            'agency': cells[2].inner_text(),
                            'award_date': cells[3].inner_text()
                        }
                        results.append(result)
                
                print(f"✅ 關鍵字 '{keyword}' 找到 {len(rows)-1} 筆")
                
                # 禮貌性延遲
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ 搜尋 '{keyword}' 失敗: {e}")
                continue
        
        browser.close()
    
    return results
```

---

### 2. 商工登記公示資料

**建議使用經濟部開放資料 + 有限爬蟲**

#### 2.1 開放資料批次處理

```python
import pandas as pd

def load_company_opendata(filepath):
    """
    讀取經濟部公司登記開放資料
    """
    df = pd.read_csv(filepath, encoding='utf-8')
    
    # 資料清洗
    df['公司名稱'] = df['公司名稱'].str.strip()
    df['統一編號'] = df['統一編號'].astype(str).str.strip()
    
    # 去除後綴取得簡稱
    df['公司簡稱'] = df['公司名稱'].str.replace('股份有限公司$', '', regex=True)
    df['公司簡稱'] = df['公司簡稱'].str.replace('有限公司$', '', regex=True)
    
    return df

# 查詢特定公司
def find_company_by_taxid(df, tax_id):
    """依統編查詢"""
    return df[df['統一編號'] == str(tax_id)]

def find_company_by_name(df, name):
    """依名稱查詢（模糊比對）"""
    return df[df['公司名稱'].str.contains(name, na=False) | 
              df['公司簡稱'].str.contains(name, na=False)]
```

#### 2.2 商工登記網站爬蟲（需董監事資料時）

```python
from playwright.sync_api import sync_playwright
import re

def scrape_company_detail(tax_id):
    """
    爬取商工登記詳細資料（含董監事）
    
    注意：此網站有驗證碼，需要額外處理
    """
    url = f"https://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 需要可見瀏覽器處理驗證碼
        page = browser.new_page()
        
        # 進入查詢頁面
        page.goto(url)
        
        # 選擇統一編號查詢
        page.click('input[value="2"]')  # 統一編號選項
        
        # 填入統編
        page.fill('input[name="queryKey"] ', str(tax_id))
        
        # 點擊查詢
        page.click('button[type="submit"]')
        
        print("⚠️  請手動完成驗證碼")
        input("完成後請按 Enter 繼續...")
        
        # 等待結果
        page.wait_for_selector('.company-data', timeout=10000)
        
        # 提取資料
        company_data = {
            'tax_id': tax_id,
            'name': page.inner_text('.company-name'),
            'representative': page.inner_text('.representative'),
            'capital': page.inner_text('.capital'),
            'address': page.inner_text('.address'),
            'status': page.inner_text('.status')
        }
        
        # 提取董監事
        directors = []
        director_rows = page.query_selector_all('.director-list tr')
        for row in director_rows:
            cells = row.query_selector_all('td')
            if len(cells) >= 2:
                directors.append({
                    'name': cells[0].inner_text().strip(),
                    'title': cells[1].inner_text().strip(),
                    'shares': cells[2].inner_text().strip() if len(cells) > 2 else None
                })
        
        company_data['directors'] = directors
        
        browser.close()
        return company_data
```

---

### 3. 公職人員利益迴避平台

**難度最高，需要驗證碼破解**

```python
from playwright.sync_api import sync_playwright
from PIL import Image
import io

def scrape_subsidy_data(official_name=None, agency=None, keyword=None):
    """
    爬取公職人員補助資料
    
    注意：此網站有較強的反爬蟲機制
    """
    url = "https://published-info.mof.gov.tw/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 進入補助交易查詢頁面
        page.goto(url)
        page.click('a[href*="subsidy"]')  # 進入補助查詢
        
        # 填入查詢條件
        if official_name:
            page.fill('input[name="officialName"]', official_name)
        if agency:
            page.select_option('select[name="agency"]', agency)
        if keyword:
            page.fill('input[name="keyword"]', keyword)
        
        # 處理驗證碼
        captcha_img = page.query_selector('img[id="captchaImage"]')
        if captcha_img:
            # 截圖並保存
            screenshot = captcha_img.screenshot()
            captcha_image = Image.open(io.BytesIO(screenshot))
            captcha_image.save('captcha.png')
            
            print("⚠️  驗證碼已保存為 captcha.png")
            captcha_code = input("請輸入驗證碼: ")
            page.fill('input[name="captchaCode"]', captcha_code)
        
        # 送出查詢
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        # 提取結果
        results = []
        rows = page.query_selector_all('.result-table tr')
        
        for row in rows[1:]:
            cells = row.query_selector_all('td')
            if len(cells) >= 5:
                results.append({
                    'official': cells[0].inner_text(),
                    'agency': cells[1].inner_text(),
                    'recipient': cells[2].inner_text(),
                    'amount': cells[3].inner_text(),
                    'project': cells[4].inner_text()
                })
        
        browser.close()
        return results
```

**驗證碼處理策略**：

1. **2Captcha 服務**（付費但可靠）
```python
import requests

def solve_captcha_2captcha(api_key, image_path):
    """使用 2Captcha 服務破解驗證碼"""
    
    # 上傳圖片
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://2captcha.com/in.php',
            files={'file': f},
            data={'key': api_key, 'method': 'post'}
        )
    
    captcha_id = response.text.split('|')[1]
    
    # 等待結果
    for _ in range(30):  # 最多等待 30 秒
        time.sleep(1)
        result = requests.get(
            f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}'
        )
        if 'OK' in result.text:
            return result.text.split('|')[1]
    
    return None
```

2. **本地 OCR**（免費但準確率較低）
```python
import pytesseract
from PIL import Image

def solve_captcha_local(image_path):
    """使用 Tesseract OCR 辨識驗證碼"""
    image = Image.open(image_path)
    
    # 影像預處理
    image = image.convert('L')  # 轉灰階
    image = image.point(lambda x: 0 if x < 128 else 255)  # 二值化
    
    # OCR 辨識
    captcha_code = pytesseract.image_to_string(
        image, 
        config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
    
    return captcha_code.strip()
```

---

## 反爬蟲應對策略

### 1. 請求頻率控制

```python
import time
import random

class RateLimiter:
    def __init__(self, min_delay=2, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    
    def wait(self):
        """等待隨機時間，避免規律請求"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay - elapsed)
        
        self.last_request_time = time.time()

# 使用
limiter = RateLimiter(min_delay=3, max_delay=7)

for url in urls:
    limiter.wait()  # 每次請求前等待
    response = requests.get(url)
```

### 2. User-Agent 輪替

```python
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
]

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

# 使用
response = requests.get(url, headers=get_random_headers())
```

### 3. Proxy 輪替

```python
from itertools import cycle

class ProxyRotator:
    def __init__(self, proxy_list):
        self.proxy_pool = cycle(proxy_list)
    
    def get_proxy(self):
        return next(self.proxy_pool)

# Proxy 列表（需自行準備）
proxies = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    'http://proxy3.example.com:8080'
]

rotator = ProxyRotator(proxies)

# 使用
for url in urls:
    proxy = rotator.get_proxy()
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy})
    except Exception as e:
        print(f"Proxy 失敗: {proxy}, 錯誤: {e}")
        continue
```

### 4. 錯誤處理與重試

```python
from functools import wraps
import time

def retry_on_failure(max_retries=3, delay=5):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"嘗試 {attempt + 1}/{max_retries} 失敗: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # 指數退避
                    else:
                        raise
            return None
        return wrapper
    return decorator

# 使用
@retry_on_failure(max_retries=3, delay=5)
def fetch_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

### 5. Session 管理與 Cookies

```python
import requests

class PersistentSession:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_random_headers())
    
    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)
    
    def close(self):
        self.session.close()

# 使用（保持 cookies）
session = PersistentSession()

# 第一次請求（取得 cookies）
session.get('https://example.com/login')

# 後續請求自動帶上 cookies
response = session.get('https://example.com/data')
```

---

## 資料儲存建議

### 1. 結構化資料（PostgreSQL）

適合：標案、公司、人員基本資料

```python
import psycopg2
from psycopg2.extras import execute_values

def save_procurement_batch(conn, data_list):
    """批次儲存標案資料"""
    query = """
        INSERT INTO procurement_cases 
        (case_id, case_name, agency_id, award_date, award_amount, status)
        VALUES %s
        ON CONFLICT (case_id) DO UPDATE SET
            award_amount = EXCLUDED.award_amount,
            status = EXCLUDED.status
    """
    
    values = [
        (d['case_id'], d['case_name'], d['agency_id'], 
         d['award_date'], d['award_amount'], d['status'])
        for d in data_list
    ]
    
    with conn.cursor() as cur:
        execute_values(cur, query, values)
    conn.commit()
```

### 2. 圖形資料（Neo4j）

適合：公司關係、人員網絡

```python
from neo4j import GraphDatabase

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_company(self, company_data):
        query = """
        MERGE (c:Company {tax_id: $tax_id})
        SET c.name = $name,
            c.representative = $representative,
            c.capital = $capital
        """
        with self.driver.session() as session:
            session.run(query, **company_data)
    
    def create_investment_relationship(self, investor_id, investee_id, share_pct):
        query = """
        MATCH (investor:Company {tax_id: $investor_id})
        MATCH (investee:Company {tax_id: $investee_id})
        MERGE (investor)-[r:INVESTS_IN]->(investee)
        SET r.share_percentage = $share_pct
        """
        with self.driver.session() as session:
            session.run(query, investor_id=investor_id, 
                       investee_id=investee_id, share_pct=share_pct)
```

### 3. 原始資料備份（本地檔案）

```python
import json
import gzip
from datetime import datetime

def backup_raw_data(data, source_name):
    """壓縮備份原始資料"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/raw/{source_name}_{timestamp}.json.gz"
    
    with gzip.open(filename, 'wt', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已備份至: {filename}")
```

---

## 排程執行

### 使用 cron（Linux/macOS）

```bash
# 編輯 crontab
crontab -e

# 每日凌晨 3 點執行標案更新
0 3 * * * cd /path/to/project && python scripts/update_procurement.py >> logs/cron.log 2>&1

# 每週一凌晨 4 點執行公司資料更新
0 4 * * 1 cd /path/to/project && python scripts/update_company.py >> logs/cron.log 2>&1
```

### 使用 Airflow（大規模）

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def scrape_pcc_data():
    # 爬蟲邏輯
    pass

def process_data():
    # 資料處理邏輯
    pass

with DAG(
    'taiwan_procurement_etl',
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 3 * * *',  # 每日凌晨 3 點
    catchup=False
) as dag:
    
    scrape_task = PythonOperator(
        task_id='scrape_pcc',
        python_callable=scrape_pcc_data
    )
    
    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data
    )
    
    scrape_task >> process_task
```

---

## 監控與日誌

```python
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/scraper_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 使用
logger.info("開始爬取標案資料")
logger.warning("發現驗證碼，需要處理")
logger.error("爬取失敗: %s", error_message)
```

---

## 法律與倫理注意事項

### 合法使用

1. **遵守 Robots.txt**
```python
from urllib.robotparser import RobotFileParser

def check_robots_txt(url):
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    rp.read()
    return rp.can_fetch('*', url)
```

2. **請求頻率限制**
   - 不造成伺服器負擔
   - 避開尖峰時段（上班時間）
   - 建議延遲 2-5 秒/請求

3. **資料使用範圍**
   - 僅用於監督公務
   - 不營利用途
   - 注意個資保護

### 倫理準則

- 資料公開透明，來源可追溯
- 分析結果應有證據支持，避免誹謗
- 尊重被查詢對象的隱私權
- 發現疑似不法應通報主管機關，而非公開指控
