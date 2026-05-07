# Phase 4 설계 문서 — 만료 전/후 로직 통합

## 목표

현재 `update_quality()`는 `item.sell_in -= 1`을 기준으로 quality 업데이트가
앞뒤 두 블록으로 쪼개져 있다. `sell_in`을 먼저 감소시킨 뒤 quality를 한 번만
처리하는 구조로 통합한다. 동작 변경 없음.

---

## 변경 범위

`python/gilded_rose.py` 만 수정. 테스트 파일은 건드리지 않음.

---

## 현재 구조의 문제점

`sell_in=0`인 일반 아이템을 예로 들면, 한 번의 `update_quality()` 호출에서
quality가 **두 번** 변경된다.

```
[블록 1] quality -= 1   (만료 전 처리, 15~16번 줄)
         sell_in 0 → -1 (24번 줄)
[블록 2] quality -= 1   (만료 후 처리, 25~28번 줄)
```

블록 1과 블록 2가 `sell_in` 감소를 사이에 두고 분리되어 있어
각 아이템 타입의 전체 동작을 한눈에 파악하기 어렵다.

---

## 핵심 아이디어

`sell_in`을 먼저 감소시킨 후, **감소된 sell_in** 기준으로 quality를 한 번만 처리한다.

```
sell_in 0 → -1 (먼저 감소)
quality 처리: sell_in < 0 이므로 amount=2 적용 → quality -= 2
```

두 블록이 하나로 합쳐지면서 아이템 타입별 로직이 연속된 단일 블록이 된다.

---

## 임계값 변환 (Backstage)

현재 Backstage 보너스 임계값은 `sell_in` **감소 전** 기준이다.
`sell_in`을 먼저 감소시키면 임계값을 1씩 낮춰야 동일한 동작이 유지된다.

| 조건 (감소 전) | 조건 (감소 후) | 동작 |
|---|---|---|
| `sell_in < 0` (만료 후) | `sell_in < 0` | quality = 0 |
| `sell_in < 6` | `sell_in < 5` | quality += 3 |
| `sell_in < 11` | `sell_in < 10` | quality += 2 |
| 그 외 | 그 외 | quality += 1 |

**검증 예시 (sell_in=5, 감소 전 기준):**

현재:
- quality += 1 (base)
- sell_in(5) < 11? Yes → quality += 1
- sell_in(5) < 6? Yes → quality += 1
- sell_in → 4
- 결과: quality += 3

변경 후:
- sell_in → 4
- 4 < 5? Yes → quality += 3
- 결과: quality += 3 ✓

**검증 예시 (sell_in=6, 감소 전 기준):**

현재:
- quality += 1
- sell_in(6) < 11? Yes → quality += 1
- sell_in(6) < 6? No
- sell_in → 5
- 결과: quality += 2

변경 후:
- sell_in → 5
- 5 < 5? No → 5 < 10? Yes → quality += 2
- 결과: quality += 2 ✓

---

## 변경 전 / 후 비교

### 변경 전 (현재, Phase 3 결과)

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue

        if item.name != AGED_BRIE and item.name != BACKSTAGE:
            self._decrement_quality(item)           # 블록 1
        else:
            self._increment_quality(item)           # 블록 1
            if item.name == BACKSTAGE:
                if item.sell_in < 11:
                    self._increment_quality(item)   # 블록 1
                if item.sell_in < 6:
                    self._increment_quality(item)   # 블록 1
        item.sell_in -= 1                           # sell_in 감소
        if item.sell_in < 0:
            if item.name != AGED_BRIE:
                if item.name != BACKSTAGE:
                    self._decrement_quality(item)   # 블록 2
                else:
                    item.quality = 0               # 블록 2
            else:
                self._increment_quality(item)       # 블록 2
```

### 변경 후

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue

        item.sell_in -= 1                           # 먼저 감소

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

---

## 효과

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| quality 업데이트 블록 수 | 2개 (블록1 + 블록2) | 1개 |
| 아이템 타입 분기 구조 | `if not AGED_BRIE and not BACKSTAGE ... else` | `if BACKSTAGE ... elif AGED_BRIE ... else` |
| 중첩 깊이 | 4단계 | 3단계 |
| Phase 5 준비 | 각 타입 로직이 단일 블록으로 정리됨 |

---

## 리스크

| 리스크 | 수준 | 비고 |
|--------|------|------|
| Backstage 임계값 오계산 | 중간 | 설계 문서 내 검증 완료, 테스트로 추가 확인 |
| 동작 변경 | 없음 | 기존 테스트 18개가 전 경계값을 커버 |

---

## 검증 방법

```
pytest test_gilded_rose.py --cov=gilded_rose --cov-report=term-missing
```

18개 통과, coverage 100% 유지 확인.
