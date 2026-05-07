# Phase 3 설계 문서 — 품질 변경 헬퍼 메서드 추출

## 목표

`quality` 상한(50) / 하한(0) 체크가 `update_quality()` 전체에 흩어져 있다.
이를 `_increment_quality`, `_decrement_quality` 두 헬퍼 메서드로 캡슐화하여
중복 조건을 제거한다. 동작 변경 없음.

---

## 변경 범위

`python/gilded_rose.py` 만 수정. 테스트 파일은 건드리지 않음.

---

## 현재 상태 분석

현재 quality 변경 시 매번 상한/하한 조건을 직접 작성하고 있다.

```python
# 증가 패턴 — 상한 50 체크를 매번 직접 작성
if item.quality < 50:
    item.quality += 1          # 17번 줄
if item.quality < 50:
    item.quality += 1          # 21~22번 줄
if item.quality < 50:
    item.quality += 1          # 24~25번 줄
if item.quality < 50:
    item.quality += 1          # 37~38번 줄

# 감소 패턴 — 하한 0 체크를 매번 직접 작성
if item.quality > 0:
    item.quality -= 1          # 13~15번 줄
if item.quality > 0:
    item.quality -= 1          # 31~32번 줄
```

증가/감소 각각 동일한 패턴이 반복된다. 상한/하한 규칙이 바뀔 경우 여러 곳을 수정해야 한다.

---

## 추가할 헬퍼 메서드

```python
def _increment_quality(self, item, amount=1):
    item.quality = min(50, item.quality + amount)

def _decrement_quality(self, item, amount=1):
    item.quality = max(0, item.quality - amount)
```

- `min(50, ...)` 으로 상한 50을 한 곳에서만 관리
- `max(0, ...)` 으로 하한 0을 한 곳에서만 관리
- `amount` 파라미터는 Phase 5에서 만료 후 2배 감소 등을 단순하게 표현하기 위한 준비

---

## 변경 전 / 후 비교

### 변경 전 (현재, Phase 2 결과)

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue

        if item.name != AGED_BRIE and item.name != BACKSTAGE:
            if item.quality > 0:
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
        item.sell_in -= 1
        if item.sell_in < 0:
            if item.name != AGED_BRIE:
                if item.name != BACKSTAGE:
                    if item.quality > 0:
                        item.quality -= 1
                else:
                    item.quality = 0
            else:
                if item.quality < 50:
                    item.quality += 1
```

### 변경 후

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue

        if item.name != AGED_BRIE and item.name != BACKSTAGE:
            self._decrement_quality(item)
        else:
            self._increment_quality(item)
            if item.name == BACKSTAGE:
                if item.sell_in < 11:
                    self._increment_quality(item)
                if item.sell_in < 6:
                    self._increment_quality(item)
        item.sell_in -= 1
        if item.sell_in < 0:
            if item.name != AGED_BRIE:
                if item.name != BACKSTAGE:
                    self._decrement_quality(item)
                else:
                    item.quality = 0
            else:
                self._increment_quality(item)

def _increment_quality(self, item, amount=1):
    item.quality = min(50, item.quality + amount)

def _decrement_quality(self, item, amount=1):
    item.quality = max(0, item.quality - amount)
```

---

## 효과

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| `if item.quality < 50:` 등장 횟수 | 4회 | 0회 |
| `if item.quality > 0:` 등장 횟수 | 2회 | 0회 |
| 상한/하한 규칙 관리 위치 | 6곳 분산 | 헬퍼 2곳 |
| 중첩 깊이 감소 | Backstage 블록 4단계 → 3단계 |

---

## 주의 사항

### Backstage 보너스 로직 변경 포인트

현재 Backstage 보너스는 증가 후 quality를 체크하는 방식으로 상한을 처리한다.

```python
# 현재: +1 후 < 50 체크
item.quality += 1          # 첫 번째 증가
if item.sell_in < 11:
    if item.quality < 50:  # 증가된 값 기준으로 체크
        item.quality += 1
```

헬퍼 메서드로 교체하면 각 호출이 독립적으로 상한을 체크하므로 동작이 동일하다.

```python
# 변경 후: 각 호출이 독립적으로 min(50, ...) 적용
self._increment_quality(item)   # min(50, quality + 1)
if item.sell_in < 11:
    self._increment_quality(item)   # min(50, quality + 1)
if item.sell_in < 6:
    self._increment_quality(item)   # min(50, quality + 1)
```

기존 테스트(`test_backstage_pass_quality_capped_at_50_in_10_day_window`,
`test_backstage_pass_quality_capped_at_50_in_5_day_window`)가 이 동작을 검증하고 있다.

---

## 변경 위치 (Phase 2 결과 기준 줄 번호)

| 줄 | 변경 전 | 변경 후 |
|----|---------|---------|
| 13~15 | `if item.quality > 0: item.quality -= 1` | `self._decrement_quality(item)` |
| 17~18 | `if item.quality < 50: item.quality += 1` | `self._increment_quality(item)` |
| 20~22 | `if item.quality < 50: item.quality += 1` | `self._increment_quality(item)` |
| 23~25 | `if item.quality < 50: item.quality += 1` | `self._increment_quality(item)` |
| 31~32 | `if item.quality > 0: item.quality -= 1` | `self._decrement_quality(item)` |
| 37~38 | `if item.quality < 50: item.quality += 1` | `self._increment_quality(item)` |

---

## 리스크

| 리스크 | 수준 | 비고 |
|--------|------|------|
| 동작 변경 | 없음 | min/max는 기존 if 조건과 동치 |
| Backstage 상한 처리 | 없음 | 기존 테스트 2개가 경계값 검증 중 |

---

## 검증 방법

```
pytest test_gilded_rose.py --cov=gilded_rose --cov-report=term-missing
```

18개 통과, coverage 100% 유지 확인.
