# 第一階段：收集 (Collect)

## 觸發條件

- 使用者請求整理某個業務模組的邏輯
- 使用者需要瞭解資料實體關係
- 使用者請求評估需求變更的影響

## 階段目標

全面收集業務相關的資料實體資訊、程式碼實作和表格結構，為後續分析提供完整的資料基礎。

## 我的工作

### 1. 專案結構識別

快速定位關鍵目錄：

- Model 層目錄（如 `app/Models`）
- Service 層目錄（如 `app/Services`）
- Repository 層目錄（如 `app/Repositories`）
- 列舉類別目錄（如 `app/Enums`）
- 資料庫遷移目錄（如 `database/migrations`）

### 2. Model 檔案收集

**核心任務**：讀取相關業務模組的 Model 檔案

收集內容：

- 模型類別定義
- 表格名稱映射（`$table`）
- 可填充欄位（`$fillable`）
- 類型轉換（`$casts`）
- 關聯關係方法（`belongsTo`, `hasMany`, `belongsToMany` 等）
- 存取器和修改器
- 作用域方法

範例讀取指令：

```
讀取 app/Models/Order.php
讀取 app/Models/OrderItem.php
讀取 app/Models/OrderStatusLog.php
```

### 3. 資料庫表格結構獲取

**方式一：讀取遷移檔案**

```
讀取 database/migrations/*_create_orders_table.php
讀取 database/migrations/*_create_order_items_table.php
```

**方式二：使用資料庫 MCP（如可用）**

```
獲取 orders 表格結構
獲取 order_items 表格結構
```

收集內容：

- 欄位名稱和類型
- 欄位註解（業務含義）
- 索引定義
- 外鍵關係
- 預設值

### 4. 列舉類別收集

讀取相關的列舉類別，理解業務狀態：

```
讀取 app/Enums/OrderStatus.php
讀取 app/Enums/PaymentStatus.php
```

收集內容：

- 列舉值定義
- 列舉值的業務含義
- 多語言翻譯

### 5. Service 層程式碼收集

理解核心業務邏輯：

```
讀取 app/Services/OrderService.php
```

收集內容：

- 核心業務方法
- 業務規則和約束
- 狀態流轉邏輯
- 與其他模組的互動

### 6. Controller/介面定義收集

瞭解對外開放的介面：

```
讀取 app/Http/Controllers/Api/OrderController.php
讀取 routes/api.php 中的訂單相關路由
```

收集內容：

- 介面端點定義
- 請求參數
- 回應結構

## 收集清單範本

收集完成後，整理為以下格式：

```markdown
## 資料實體收集清單

### 1. Model 檔案

| 檔案路徑 | 模型名稱 | 對應表格 | 說明 |
|----------|----------|--------|------|
| app/Models/Order.php | Order | orders | 訂單主表 |
| app/Models/OrderItem.php | OrderItem | order_items | 訂單明細 |

### 2. 表格結構資訊

#### orders 表格

| 欄位名 | 類型 | 說明 |
|--------|------|------|
| id | bigint | 主鍵 |
| order_no | varchar | 訂單號 |
| ... | ... | ... |

### 3. 列舉類別

| 檔案路徑 | 列舉名稱 | 說明 |
|----------|----------|------|
| app/Enums/OrderStatus.php | OrderStatus | 訂單狀態 |

### 4. 關聯關係

| 主模型 | 關聯類型 | 關聯模型 | 說明 |
|--------|----------|----------|------|
| Order | hasMany | OrderItem | 一個訂單有多個明細 |

### 5. 業務邏輯檔案

| 檔案路徑 | 關鍵方法 | 說明 |
|----------|----------|------|
| app/Services/OrderService.php | createOrder | 建立訂單 |
```

## 重要約束

- **全面收集** - 不要遺漏相關的實體和程式碼
- **記錄來源** - 標註每項資訊的來源檔案
- **保持原樣** - 收集階段只收集，不做分析解讀
- **識別邊界** - 明確本次整理的範圍邊界

## 與使用者的互動

收集階段的互動範例：

**開始收集**：

- 「好的，讓我先收集訂單相關的資料實體資訊...」
- 「我會從 Model、資料庫、列舉、Service 等方面全面收集...」

**收集過程中**：

- 「我找到了訂單相關的 5 個 Model 檔案...」
- 「正在讀取資料庫表格結構...」
- 「發現了 3 個相關的列舉類別...」

**收集完成**：

- 「資料收集完成，我整理了一份收集清單，接下來進入分析階段...」

## 完成標誌

- Model 檔案全部讀取
- 表格結構資訊獲取完整
- 列舉類別收集完成
- 核心業務程式碼已讀取
- 收集清單整理完畢
- 準備進入分析階段

## 資料獲取優先順序

1. **首選**：Model 檔案（最準確的業務定義）
2. **次選**：資料庫遷移檔案（表格結構定義）
3. **補充**：資料庫 MCP 查詢（即時資料結構）
4. **參考**：Service 層程式碼（業務邏輯實作）

## 常見模組的收集範圍

### 訂單模組範例

```
Models: Order, OrderItem, OrderStatusLog, OrderPayment
Enums: OrderStatus, PaymentStatus, RefundStatus
Services: OrderService, PaymentService
```

### 使用者模組範例

```
Models: User, UserProfile, UserAddress, UserRole
Enums: UserStatus, UserType
Services: UserService, AuthService
```

### 商品模組範例

```
Models: Product, ProductCategory, ProductSku, ProductAttribute
Enums: ProductStatus, ProductType
Services: ProductService, InventoryService
```
