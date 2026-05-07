# Phase 5 설계 문서 — 아이템 타입별 메서드 분리

## 목표

`update_quality()`가 dispatch(분기) 역할만 담당하고,
각 아이템 타입의 업데이트 로직은 전용 메서드로 분리한다.
SRP를 만족시키고 Phase 6의 Conjured 추가를 OCP 방식으로 가능하게 한다.
동작 변경 없음.

---

## 변경 범위

`python/gilded_rose.py` 만 수정. 테스트 파일은 건드리지 않음.

---

## 현재 상태 (Phase 4 결과)

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue

        item.sell_in -= 1

        if item.name == BACKSTAGE:
            if item.sell_in < 0:
                item.quality = 0
            elif item.sell_in < 5:
                self._increment_quality(item, 3)
            elif item.sell_in < 10:
                self._increment_quality(item, 2)
            else:
                self._increment_quality(item)
        elif item.name == AGED_BRIE:
            amount = 2 if item.sell_in < 0 else 1
            self._increment_quality(item, amount)
        else:
            amount = 2 if item.sell_in < 0 else 1
            self._decrement_quality(item, amount)
```

`update_quality()` 한 메서드 안에 세 가지 타입의 로직이 혼재한다.
새 타입이 추가될 때마다 이 메서드를 직접 수정해야 한다.

---

## 변경 내용

### 추출할 메서드

| 메서드 | 처리 대상 |
|--------|-----------|
| `_update_normal(item)` | 일반 아이템 |
| `_update_aged_brie(item)` | Aged Brie |
| `_update_backstage(item)` | Backstage passes |

각 메서드는 `sell_in` 감소와 quality 변경을 모두 자체 처리한다.

### 변경 후 전체 코드

```python
AGED_BRIE = "Aged Brie"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS  = "Sulfuras, Hand of Ragnaros"


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

    def _increment_quality(self, item, amount=1):
        item.quality = min(50, item.quality + amount)

    def _decrement_quality(self, item, amount=1):
        item.quality = max(0, item.quality - amount)
```

---

## 변경 전 / 후 비교

### `update_quality()` 역할

| | 변경 전 | 변경 후 |
|---|---------|---------|
| 역할 | dispatch + 각 타입 로직 | dispatch 전용 |
| 줄 수 | 18줄 | 8줄 |
| 새 타입 추가 시 | 이 메서드 수정 필요 | `elif` 한 줄 + 새 메서드 추가 |

### 각 타입 메서드

- 독립적으로 읽고 이해 가능
- 타입별 테스트를 추후 메서드 단위로도 작성 가능
- Phase 6에서 `_update_conjured(item)` 추가 시 `update_quality()` 내부 로직은 건드리지 않음

---

## 리스크

| 리스크 | 수준 | 비고 |
|--------|------|------|
| 동작 변경 | 없음 | 로직 이동만, 내용 변경 없음 |
| `sell_in` 감소 위치 | 없음 | 각 메서드 내 첫 줄로 동일하게 유지 |

---

## 검증 방법

```
pytest test_gilded_rose.py --cov=gilded_rose --cov-report=term-missing
```

18개 통과, coverage 100% 유지 확인.
