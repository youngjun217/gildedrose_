# Phase 6 설계 문서 — Conjured 아이템 추가

## 목표

요구사항에 명시된 Conjured 아이템을 TDD 방식으로 추가한다.
Phase 5에서 갖춘 dispatch 구조 덕분에 기존 코드를 수정하지 않고
새 메서드 하나와 `elif` 한 줄만으로 기능을 확장한다 (OCP 준수 검증).

---

## 변경 범위

- `python/gilded_rose.py` — 상수, dispatch, 메서드 추가
- `python/test_gilded_rose.py` — Conjured 테스트 추가 (먼저 작성)

---

## Conjured 규칙 (요구사항)

> "Conjured" 아이템은 일반 아이템의 **2배 속도**로 quality가 저하된다.

| 상황 | quality 변화 |
|------|-------------|
| 만료 전 (`sell_in >= 0` after decrement) | -2 |
| 만료 후 (`sell_in < 0` after decrement) | -4 |
| quality 하한 | 0 (음수 불가) |

---

## 1단계 — 테스트 먼저 작성 (TDD)

`test_gilded_rose.py`에 Conjured 섹션을 추가한다.

```python
CONJURED = "Conjured Mana Cake"

# ---------------------------------------------------------------------------
# Conjured
# ---------------------------------------------------------------------------

def test_conjured_decreases_quality_by_2_before_sell_date():
    items = update([Item(CONJURED, 5, 10)])
    assert items[0].quality == 8
    assert items[0].sell_in == 4


def test_conjured_zero_quality_stays_zero():
    items = update([Item(CONJURED, 5, 0)])
    assert items[0].quality == 0
    assert items[0].sell_in == 4


def test_conjured_quality_does_not_go_below_zero():
    items = update([Item(CONJURED, 5, 1)])
    assert items[0].quality == 0
    assert items[0].sell_in == 4


def test_conjured_decreases_quality_by_4_after_sell_date():
    items = update([Item(CONJURED, 0, 10)])
    assert items[0].quality == 6
    assert items[0].sell_in == -1


def test_conjured_quality_does_not_go_below_zero_after_sell_date():
    items = update([Item(CONJURED, 0, 3)])
    assert items[0].quality == 0
    assert items[0].sell_in == -1
```

---

## 2단계 — 구현

### 상수 추가

```python
CONJURED = "Conjured Mana Cake"
```

### dispatch에 elif 한 줄 추가

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue
        elif item.name == BACKSTAGE:
            self._update_backstage(item)
        elif item.name == AGED_BRIE:
            self._update_aged_brie(item)
        elif item.name == CONJURED:          # 추가
            self._update_conjured(item)      # 추가
        else:
            self._update_normal(item)
```

### 메서드 추가

```python
def _update_conjured(self, item):
    item.sell_in -= 1
    amount = 4 if item.sell_in < 0 else 2
    self._decrement_quality(item, amount)
```

`_decrement_quality`의 `max(0, ...)` 덕분에 하한 처리는 별도 조건 없이 보장된다.

---

## 변경 후 전체 코드

```python
AGED_BRIE = "Aged Brie"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS  = "Sulfuras, Hand of Ragnaros"
CONJURED  = "Conjured Mana Cake"


class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name == SULFURAS:
                continue
            elif item.name == BACKSTAGE:
                self._update_backstage(item)
            elif item.name == AGED_BRIE:
                self._update_aged_brie(item)
            elif item.name == CONJURED:
                self._update_conjured(item)
            else:
                self._update_normal(item)

    def _update_normal(self, item):
        item.sell_in -= 1
        amount = 2 if item.sell_in < 0 else 1
        self._decrement_quality(item, amount)

    def _update_aged_brie(self, item):
        item.sell_in -= 1
        amount = 2 if item.sell_in < 0 else 1
        self._increment_quality(item, amount)

    def _update_backstage(self, item):
        item.sell_in -= 1
        if item.sell_in < 0:
            item.quality = 0
        elif item.sell_in < 5:
            self._increment_quality(item, 3)
        elif item.sell_in < 10:
            self._increment_quality(item, 2)
        else:
            self._increment_quality(item)

    def _update_conjured(self, item):
        item.sell_in -= 1
        amount = 4 if item.sell_in < 0 else 2
        self._decrement_quality(item, amount)

    def _increment_quality(self, item, amount=1):
        item.quality = min(50, item.quality + amount)

    def _decrement_quality(self, item, amount=1):
        item.quality = max(0, item.quality - amount)
```

---

## OCP 준수 확인

| 항목 | 내용 |
|------|------|
| 기존 메서드 수정 | 없음 (`update_quality` dispatch에 `elif` 한 줄만 추가) |
| 기존 테스트 영향 | 없음 |
| 추가 사항 | 상수 1개, 메서드 1개, 테스트 5개 |

---

## 검증 방법

```
pytest test_gilded_rose.py --cov=gilded_rose --cov-report=term-missing
```

23개 통과 (기존 18 + 신규 5), coverage 100% 유지 확인.
