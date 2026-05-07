# Phase 1 설계 문서 — 표현 정리 (Cosmetic)

## 목표

동작 변경 없이 코드의 **가독성과 안전성**을 높인다.
이후 Phase에서 구조를 변경할 때 혼선이 없도록 표현을 통일하는 사전 작업.

---

## 변경 범위

`python/gilded_rose.py` 만 수정. 테스트 파일은 건드리지 않음.

---

## 변경 1. 매직 스트링 → 모듈 수준 상수

### 현재 상태

아이템 이름이 문자열 리터럴로 메서드 내에 총 7회 등장한다.

```python
# gilded_rose.py — update_quality() 내부
if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":
    ...
    if item.name != "Sulfuras, Hand of Ragnaros":
        ...
    if item.name == "Backstage passes to a TAFKAL80ETC concert":
        ...
if item.name != "Sulfuras, Hand of Ragnaros":
    ...
if item.name != "Aged Brie":
    if item.name != "Backstage passes to a TAFKAL80ETC concert":
        ...
        if item.name != "Sulfuras, Hand of Ragnaros":
```

### 문제점

- 오탈자가 있어도 런타임까지 발견되지 않는다.
- 문자열 수정 시 변경 위치를 모두 찾아야 한다.

### 변경 후

파일 최상단(클래스 정의 위)에 상수를 선언한다.

```python
AGED_BRIE = "Aged Brie"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS  = "Sulfuras, Hand of Ragnaros"
```

`update_quality()` 내부의 모든 문자열 리터럴을 해당 상수로 교체한다.

```python
if item.name != AGED_BRIE and item.name != BACKSTAGE:
    ...
    if item.name != SULFURAS:
        ...
    if item.name == BACKSTAGE:
        ...
if item.name != SULFURAS:
    ...
if item.name != AGED_BRIE:
    if item.name != BACKSTAGE:
        ...
        if item.name != SULFURAS:
```

### 변경 위치 (현재 파일 기준 줄 번호)

| 줄 | 교체 대상 |
|----|-----------|
| 7  | `"Aged Brie"`, `"Backstage passes to a TAFKAL80ETC concert"` |
| 9  | `"Sulfuras, Hand of Ragnaros"` |
| 14 | `"Backstage passes to a TAFKAL80ETC concert"` |
| 21 | `"Sulfuras, Hand of Ragnaros"` |
| 24 | `"Aged Brie"` |
| 25 | `"Backstage passes to a TAFKAL80ETC concert"` |
| 27 | `"Sulfuras, Hand of Ragnaros"` |

---

## 변경 2. 산술 표현 단순화

### 현재 상태

```python
item.quality = item.quality - 1   # 10번 줄
item.quality = item.quality + 1   # 13, 17, 20, 33번 줄
item.sell_in = item.sell_in - 1   # 22번 줄
item.quality = item.quality - item.quality  # 30번 줄
```

### 문제점

- `item.quality = item.quality - 1` 형태는 불필요하게 장황하다.
- `item.quality - item.quality`는 `0`이지만 독자가 의도를 즉시 파악하기 어렵다.

### 변경 후

```python
item.quality -= 1                 # 10번 줄
item.quality += 1                 # 13, 17, 20, 33번 줄
item.sell_in -= 1                 # 22번 줄
item.quality = 0                  # 30번 줄
```

### 변경 위치

| 줄  | 변경 전                               | 변경 후           |
|-----|---------------------------------------|-------------------|
| 10  | `item.quality = item.quality - 1`     | `item.quality -= 1` |
| 13  | `item.quality = item.quality + 1`     | `item.quality += 1` |
| 17  | `item.quality = item.quality + 1`     | `item.quality += 1` |
| 20  | `item.quality = item.quality + 1`     | `item.quality += 1` |
| 22  | `item.sell_in = item.sell_in - 1`     | `item.sell_in -= 1` |
| 30  | `item.quality = item.quality - item.quality` | `item.quality = 0` |
| 33  | `item.quality = item.quality + 1`     | `item.quality += 1` |

---

## 예상 결과 (변경 후 전체 코드)

```python
AGED_BRIE = "Aged Brie"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS  = "Sulfuras, Hand of Ragnaros"


class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name != AGED_BRIE and item.name != BACKSTAGE:
                if item.quality > 0:
                    if item.name != SULFURAS:
                        item.quality -= 1
            else:
                if item.quality < 50:
                    item.quality += 1
                    if item.name == BACKSTAGE:
                        if item.sell_in < 11:
                            if item.quality < 50:
                                item.quality += 1
                        if item.sell_in < 6:
                            if item.quality < 50:
                                item.quality += 1
            if item.name != SULFURAS:
                item.sell_in -= 1
            if item.sell_in < 0:
                if item.name != AGED_BRIE:
                    if item.name != BACKSTAGE:
                        if item.quality > 0:
                            if item.name != SULFURAS:
                                item.quality -= 1
                    else:
                        item.quality = 0
                else:
                    if item.quality < 50:
                        item.quality += 1


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
```

---

## 리스크

| 리스크 | 수준 | 비고 |
|--------|------|------|
| 동작 변경 | 없음 | 순수 표현 교체 |
| 상수명 충돌 | 낮음 | 모듈 수준 선언, 기존 심볼 없음 |
| 테스트 파일 영향 | 없음 | `test_gilded_rose.py`는 이미 상수를 사용 중 |

---

## 검증 방법

```
pytest test_gilded_rose.py --cov=gilded_rose --cov-report=term-missing
```

18개 통과, coverage 100% 유지 확인.
