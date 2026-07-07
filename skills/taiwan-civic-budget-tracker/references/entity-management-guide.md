# Named Entity 管理技術指南

如何避免重複實體與確保數據來源單一性

---

## 問題定義

### 核心挑戰

1. **同名異人（Name Ambiguity）**
   - 台灣前10大姓氏占總人口55%，常見姓名組合重複率高
   - 範例：「陳怡君」可能是法官、律師、或NPO理事
   - 挑戰：如何區分「司法院陳怡君」vs「廢死聯盟陳怡君」

2. **數據來源多樣性（Source Diversity）**
   - 同一人在不同來源中的記錄不一致
   - 商工登記（繁體）vs 大陸媒體（簡體）
   - 職務變化：去年是檢察官，今年轉任律師

3. **數據衝突（Data Conflict）**
   - 來源A說出生年1975，來源B說1976
   - 來源A說代表人是甲，來源B說已變更為乙

---

## 解決方案架構

### 1. 分層ID架構（Layered ID Architecture）

```
┌─────────────────────────────────────────────────────┐
│                  Canonical ID                        │
│         (全局唯一標識符 - UUID/GUID)                  │
│                  e.g., "ent_a1b2c3d4"               │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌────────────────┐ ┌──────────────┐ ┌──────────────┐
│   Source ID    │ │  Source ID   │ │  Source ID   │
│  (商工登記)     │ │  (PCC標案)   │ │  (新聞媒體)   │
│   "12345678"   │ │"A111111111"  │ │  "王大明"     │
└────────────────┘ └──────────────┘ └──────────────┘
```

**核心原則**：
- 每個真實世界的實體只對應**一個**Canonical ID
- 不同來源使用各自的Source ID，通過Mapping表關聯到Canonical ID
- Canonical ID永不重複，永不刪除（僅標記deprecated）

### 2. 屬性指紋（Attribute Fingerprinting）

```python
entity_fingerprint = {
    "name": "王婉諭",           # 姓名
    "birth_year": 1975,        # 出生年（關鍵區分屬性）
    "primary_title": "立法委員", # 主要職務
    "organizations": [          # 所屬組織
        "時代力量",
        "立法院"
    ],
    "identifiers": {           # 識別碼
        "national_id": "A123456789",  # 身份證（如有）
        "moea_director_id": "dir_001" # 商工登記董監事ID
    }
}

# 生成唯一鍵
unique_key = f"{name}_{birth_year}_{primary_title}"
# e.g., "王婉諭_1975_立法委員"
```

**強制要求**：
- **人員**：姓名 + 出生年（至少這兩項才能創建實體）
- **公司**：統一編號（唯一且穩定）
- **組織**：登記字號或名稱+成立年

### 3. 數據來源追蹤（Source Attribution）

```sql
-- 實體來源映射表
CREATE TABLE Entity_Source_Mapping (
    mapping_id UUID PRIMARY KEY,
    canonical_id UUID REFERENCES Entity(canonical_id),
    
    -- 來源信息
    source_system VARCHAR(50),      -- pcc / moea / news / manual
    source_entity_id VARCHAR(100),  -- 源系統內部ID
    source_url TEXT,                -- 數據URL
    source_date DATE,               -- 數據日期
    
    -- 匹配信息
    match_confidence DECIMAL(3,2),  -- 0.00-1.00
    match_method VARCHAR(20),       -- exact / fuzzy / manual / inferred
    
    -- 時間戳
    created_at TIMESTAMP DEFAULT NOW(),
    last_sync TIMESTAMP,
    
    -- 驗證狀態
    verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verified_at TIMESTAMP
);
```

**數據來源可靠性評級**：

| 數據來源 | 可靠性 | 更新頻率 | 說明 |
|---------|--------|---------|------|
| 商工登記 (MOEA) | 0.95 | 每日 | 官方登記，法律效力 |
| 政府標案 (PCC) | 0.90 | 每日 | 政府公開，較準確 |
| 公職人員財產申報 | 0.88 | 年度 | 法定申報，但可能延遲 |
| 新聞媒體報導 | 0.75 | 即時 | 需交叉驗證 |
| 人工驗證 | 0.85 | 即時 | 基於多方證據 |
| 社群媒體 | 0.60 | 即時 | 僅供參考 |

---

## 實體消歧（Entity Disambiguation）

### 消歧流程

```python
def disambiguate_entity(new_entity, existing_entities):
    """
    實體消歧主函數
    返回: {'type': 'existing'/'new'/'ambiguous', 'id': canonical_id}
    """
    
    # Step 1: 精確匹配（姓名 + 出生年）
    exact_matches = find_exact_matches(
        name=new_entity['name'],
        birth_year=new_entity.get('birth_year'),
        existing_entities=existing_entities
    )
    
    if len(exact_matches) == 1:
        return {
            'type': 'existing',
            'id': exact_matches[0]['canonical_id'],
            'confidence': 1.0,
            'method': 'exact_match'
        }
    
    # Step 2: 模糊匹配（Jaro-Winkler相似度）
    if len(exact_matches) == 0:
        fuzzy_matches = find_fuzzy_matches(
            name=new_entity['name'],
            existing_entities=existing_entities,
            threshold=0.85
        )
        
        # 進一步用屬性驗證
        if fuzzy_matches:
            verified = verify_with_attributes(
                candidates=fuzzy_matches,
                new_attributes=new_entity
            )
            
            if len(verified) == 1:
                return {
                    'type': 'existing',
                    'id': verified[0]['canonical_id'],
                    'confidence': verified[0]['similarity_score'],
                    'method': 'fuzzy_match'
                }
            elif len(verified) > 1:
                return {
                    'type': 'ambiguous',
                    'candidates': verified,
                    'requires_manual_review': True
                }
    
    # Step 3: 多個精確匹配（同名同出生年）
    if len(exact_matches) > 1:
        # 用額外屬性區分
        for candidate in exact_matches:
            if is_same_person(
                candidate['attributes'],
                new_entity['attributes']
            ):
                return {
                    'type': 'existing',
                    'id': candidate['canonical_id'],
                    'confidence': 0.9,
                    'method': 'attribute_verification'
                }
        
        # 仍無法區分，標記為待審核
        return {
            'type': 'ambiguous',
            'candidates': exact_matches,
            'reason': 'same_name_same_birth_year',
            'requires_manual_review': True
        }
    
    # Step 4: 創建新實體
    return {
        'type': 'new',
        'id': generate_canonical_id(),
        'method': 'new_entity'
    }
```

### 相似度計算

```python
def calculate_similarity_score(entity1, entity2):
    """
    計算兩個實體的綜合相似度分數
    使用多屬性加權平均
    """
    
    weights = {
        'name': 0.35,
        'birth_year': 0.25,
        'title': 0.20,
        'organization': 0.15,
        'location': 0.05
    }
    
    scores = {}
    
    # 1. 姓名相似度 (Jaro-Winkler)
    scores['name'] = jaro_winkler_similarity(
        entity1['name'], 
        entity2['name']
    )
    
    # 2. 出生年匹配 (二值)
    if entity1.get('birth_year') and entity2.get('birth_year'):
        scores['birth_year'] = 1.0 if entity1['birth_year'] == entity2['birth_year'] else 0.0
    else:
        scores['birth_year'] = 0.5  # 未知，給予中等分數
    
    # 3. 職務相似度 (餘弦相似度)
    if entity1.get('title') and entity2.get('title'):
        scores['title'] = cosine_similarity(
            entity1['title'],
            entity2['title']
        )
    else:
        scores['title'] = 0.5
    
    # 4. 組織重疊度 (Jaccard)
    orgs1 = set(entity1.get('organizations', []))
    orgs2 = set(entity2.get('organizations', []))
    if orgs1 and orgs2:
        scores['organization'] = len(orgs1 & orgs2) / len(orgs1 | orgs2)
    else:
        scores['organization'] = 0.0
    
    # 5. 地點相似度
    if entity1.get('location') and entity2.get('location'):
        scores['location'] = 1.0 if entity1['location'] == entity2['location'] else 0.0
    else:
        scores['location'] = 0.5
    
    # 加權總和
    total_weight = sum(
        weights[attr] for attr in scores.keys()
    )
    
    weighted_score = sum(
        scores[attr] * weights[attr] 
        for attr in scores.keys()
    ) / total_weight
    
    return {
        'total_score': weighted_score,
        'component_scores': scores,
        'confidence': 'high' if weighted_score > 0.85 else 'medium' if weighted_score > 0.70 else 'low'
    }
```

---

## 數據衝突解決

### 衝突類型

1. **值衝突（Value Conflict）**
   - 來源A：出生年1975
   - 來源B：出生年1976

2. **關係衝突（Relationship Conflict）**
   - 來源A：甲是A公司董事
   - 來源B：甲已辭去A公司董事（時間差）

3. **存在性衝突（Existence Conflict）**
   - 來源A：公司仍在營業
   - 來源B：公司已解散

### 衝突解決策略

```python
def resolve_attribute_conflict(canonical_id, attribute_name, values_with_sources):
    """
    解決屬性值的來源衝突
    
    values_with_sources: [
        {'value': '1975', 'source': 'moea', 'confidence': 0.95, 'date': '2024-01-15'},
        {'value': '1976', 'source': 'news', 'confidence': 0.75, 'date': '2024-02-20'}
    ]
    """
    
    # 策略1: 值一致，直接採用
    unique_values = set(v['value'] for v in values_with_sources)
    if len(unique_values) == 1:
        return {
            'resolved_value': values_with_sources[0]['value'],
            'strategy': 'unanimous',
            'confidence': max(v['confidence'] for v in values_with_sources)
        }
    
    # 策略2: 按來源可靠性加權投票
    source_reliability = {
        'moea': 0.95,
        'pcc': 0.90,
        'property_disclosure': 0.88,
        'manual': 0.85,
        'news': 0.75,
        'social_media': 0.60
    }
    
    value_scores = {}
    for v in values_with_sources:
        reliability = source_reliability.get(v['source'], 0.5)
        composite_score = reliability * v['confidence']
        
        if v['value'] not in value_scores:
            value_scores[v['value']] = []
        value_scores[v['value']].append(composite_score)
    
    # 計算每個值的總分
    ranked_values = sorted(
        [(val, sum(scores)/len(scores)) for val, scores in value_scores.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    best_value, best_score = ranked_values[0]
    second_score = ranked_values[1][1] if len(ranked_values) > 1 else 0
    
    # 策略3: 最佳值明顯領先(>0.3差距)
    if best_score - second_score > 0.3:
        return {
            'resolved_value': best_value,
            'strategy': 'weighted_majority',
            'confidence': best_score,
            'alternatives': [v for v, _ in ranked_values[1:]]
        }
    
    # 策略4: 接近或平手，標記為衝突待審核
    return {
        'resolved_value': best_value,
        'strategy': 'uncertain',
        'confidence': best_score,
        'conflict': True,
        'alternatives': [v for v, _ in ranked_values],
        'requires_manual_verification': True,
        'suggested_action': '請人工確認正確值'
    }
```

### 時間維度處理

```python
def resolve_temporal_conflict(entity_id, relationship_type, timed_relationships):
    """
    處理有時間維度的關係衝突
    
    例如：董監事任期變化
    """
    
    # 按時間排序
    sorted_rels = sorted(
        timed_relationships,
        key=lambda x: x['start_date']
    )
    
    # 檢查時間重疊
    for i in range(len(sorted_rels) - 1):
        current = sorted_rels[i]
        next_rel = sorted_rels[i + 1]
        
        # 如果沒有結束日期，假設持續到下一個開始
        current_end = current.get('end_date') or next_rel['start_date']
        
        # 檢查是否有時間重疊
        if current_end > next_rel['start_date']:
            # 時間重疊，標記衝突
            return {
                'conflict': True,
                'type': 'temporal_overlap',
                'overlap_period': {
                    'start': next_rel['start_date'],
                    'end': current_end
                },
                'conflicting_records': [current, next_rel]
            }
    
    # 無衝突，返回時間線
    return {
        'conflict': False,
        'timeline': sorted_rels
    }
```

---

## 台灣情境特殊處理

### 1. 簡繁體轉換

```python
import opencc

# 創建轉換器
converter = opencc.OpenCC('s2t')  # 簡體轉繁體

def normalize_name(name):
    """標準化姓名（統一轉為繁體）"""
    # 轉換為繁體
    traditional = converter.convert(name)
    
    # 移除常見稱謂後綴
    suffixes = ['先生', '女士', '博士', '教授', '律師', '法官']
    for suffix in suffixes:
        if traditional.endswith(suffix):
            traditional = traditional[:-len(suffix)]
    
    return traditional.strip()

# 在Entity_Alias表中記錄變體
aliases = [
    {'name': '王大明', 'type': 'traditional'},
    {'name': '王大明', 'type': 'simplified'},
    {'name': '王大明律師', 'type': 'with_title'}
]
```

### 2. 姓名重複率統計

```python
# 台灣常見高重複率姓名（需要額外區分屬性）
HIGH_COLLISION_NAMES = [
    '陳怡君', '林雅婷', '張家豪', '王柏翰',
    '李思涵', '黃詩涵', '劉佳琪', '楊承恩'
]

def requires_additional_identifiers(name):
    """判斷是否需要額外識別屬性"""
    
    # 高重複率姓名必須提供出生年
    if name in HIGH_COLLISION_NAMES:
        return {
            'required': True,
            'required_attributes': ['birth_year', 'primary_title'],
            'reason': 'high_collision_name'
        }
    
    # 單名通常需要額外識別
    if len(name) <= 2:
        return {
            'required': True,
            'required_attributes': ['birth_year'],
            'reason': 'single_character_name'
        }
    
    return {'required': False}
```

### 3. 職務變化追蹤

```python
class CareerTracker:
    """追蹤人物職業生涯變化"""
    
    def track_position_changes(self, person_id):
        """追蹤某人的職務變化歷史"""
        
        positions = self.db.query("""
            SELECT 
                p.organization,
                p.title,
                p.start_date,
                p.end_date,
                p.source_system
            FROM Positions p
            WHERE p.person_id = %s
            ORDER BY p.start_date
        """, (person_id,))
        
        # 建立時間線
        timeline = []
        for pos in positions:
            timeline.append({
                'period': f"{pos['start_date']} ~ {pos['end_date'] or '現任'}",
                'organization': pos['organization'],
                'title': pos['title'],
                'source': pos['source_system']
            })
        
        return timeline
    
    def detect_conflicting_positions(self, person_id):
        """檢測時間重疊的職務（可能錯誤或身兼多職）"""
        
        positions = self.get_active_positions(person_id)
        
        conflicts = []
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                if self._periods_overlap(pos1, pos2):
                    conflicts.append({
                        'position1': pos1,
                        'position2': pos2,
                        'overlap_type': 'simultaneous'  # 同時擔任
                    })
        
        return conflicts
```

---

## 最小可行方案（MVP）

### 核心數據表

```sql
-- 規範實體表
CREATE TABLE canonical_entities (
    canonical_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(20) CHECK (entity_type IN ('person', 'company', 'organization')),
    display_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 屬性表（支持多來源）
CREATE TABLE entity_attributes (
    attribute_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_id UUID REFERENCES canonical_entities(canonical_id),
    attribute_name VARCHAR(50) NOT NULL,
    attribute_value TEXT NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    source_date DATE,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 來源映射表
CREATE TABLE entity_source_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_id UUID REFERENCES canonical_entities(canonical_id),
    source_system VARCHAR(50) NOT NULL,
    source_entity_id VARCHAR(100) NOT NULL,
    match_confidence DECIMAL(3,2),
    match_method VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 審核隊列表
CREATE TABLE entity_review_queue (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    new_entity_data JSONB NOT NULL,
    candidate_matches JSONB,
    review_status VARCHAR(20) DEFAULT 'pending',
    assigned_reviewer VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    reviewed_at TIMESTAMP
);
```

### 簡化版消歧函數

```python
class SimpleEntityManager:
    """簡化版實體管理器（MVP）"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_or_create_entity(self, entity_data):
        """
        獲取或創建實體（核心函數）
        
        entity_data: {
            'name': '王大明',
            'birth_year': 1975,
            'title': '律師',
            'source': 'moea',
            'source_id': '12345678'
        }
        """
        
        # 1. 嘗試精確匹配
        existing = self._find_exact_match(entity_data)
        if existing:
            self._add_source_mapping(existing['canonical_id'], entity_data)
            return existing['canonical_id']
        
        # 2. 創建新實體
        canonical_id = self._create_entity(entity_data)
        self._add_source_mapping(canonical_id, entity_data)
        
        return canonical_id
    
    def _find_exact_match(self, entity_data):
        """精確匹配查詢"""
        
        query = """
            SELECT ce.canonical_id
            FROM canonical_entities ce
            JOIN entity_attributes ea_birth 
                ON ce.canonical_id = ea_birth.canonical_id
                AND ea_birth.attribute_name = 'birth_year'
            WHERE ce.display_name = %s
            AND ea_birth.attribute_value = %s
            LIMIT 1
        """
        
        result = self.db.execute(
            query, 
            (entity_data['name'], str(entity_data.get('birth_year', '')))
        )
        
        return result[0] if result else None
    
    def _create_entity(self, entity_data):
        """創建新實體"""
        
        # 判斷實體類型
        entity_type = self._detect_entity_type(entity_data)
        
        # 插入規範實體
        canonical_id = self.db.execute("""
            INSERT INTO canonical_entities (entity_type, display_name)
            VALUES (%s, %s)
            RETURNING canonical_id
        """, (entity_type, entity_data['name']))[0]['canonical_id']
        
        # 插入屬性
        for attr_name, attr_value in entity_data.items():
            if attr_name not in ['name', 'source', 'source_id']:
                self.db.execute("""
                    INSERT INTO entity_attributes 
                        (canonical_id, attribute_name, attribute_value, source_system)
                    VALUES (%s, %s, %s, %s)
                """, (canonical_id, attr_name, str(attr_value), entity_data['source']))
        
        return canonical_id
```

---

## 去重策略總結

### 1. 預防性措施（Prevention）

| 階段 | 措施 | 說明 |
|------|------|------|
| **數據輸入** | 強制檢查 | 所有新數據必須經過消歧流程 |
| **屬性驗證** | 必填欄位 | 人員必須有姓名+出生年 |
| **名稱標準化** | 簡繁轉換 | 統一轉為繁體入庫 |
| **ID生成** | UUID | 使用隨機UUID避免碰撞 |

### 2. 檢測性措施（Detection）

| 頻率 | 檢測項目 | 方法 |
|------|---------|------|
| **即時** | 精確匹配 | 入庫前查詢同名+同年 |
| **每日** | 模糊匹配 | 掃描相似度>0.85的潛在重複 |
| **每週** | 衝突檢測 | 檢查同一實體的屬性衝突 |
| **每月** | 數據質量報告 | 統計未驗證、衝突記錄數 |

### 3. 修正性措施（Correction）

| 情況 | 處理方式 | 責任人 |
|------|---------|--------|
| **自動解決** | 系統自動合併 | 自動化 |
| **低置信度** | 放入審核隊列 | 數據管理員 |
| **高衝突** | 標記需專家審核 | 領域專家 |
| **已確認重複** | 合併實體，保留別名 | 管理員 |

---

## 關鍵原則

1. **先查後建**：任何新實體必須先經過消歧查詢
2. **多源驗證**：重要屬性需要至少2個來源交叉驗證
3. **永不刪除**：重複實體標記為merged而非刪除，保持可追溯
4. **持續審核**：建立定期審核機制，保持數據質量
5. **透明溯源**：每個屬性都標記來源和置信度

---

*本指南適用於台灣公民科技專案的人員、組織、公司實體管理*