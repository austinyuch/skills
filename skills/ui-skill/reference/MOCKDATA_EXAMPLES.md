# 模擬資料示例

## 採購订單資料
```javascript
const purchaseOrders = [
    {
        id: 1,
        order_no: "PO20241225001",
        supplier: "科技创新有限公司",
        total_amount: 156000.00,
        status: "pending",
        apply_date: "2024-12-25"
    }
];
```

## 供應商資料
```javascript
const suppliers = [
    {
        id: 1,
        name: "科技创新有限公司",
        contact: "张經理",
        phone: "13800138000",
        status: "active"
    }
];
```

## 狀態枚举
```javascript
const statusEnum = {
    draft: "草稿",
    pending: "待审批",
    approved: "审批透過",
    rejected: "审批拒绝"
};
```
