# Phase 2 설계 문서 — Guard Clause로 중첩 제거

## 목표

Sulfuras는 아무 처리도 하지 않는 아이템이므로 루프 최상단에서 `continue`로 조기 탈출한다.
이를 통해 나머지 코드 전체에 흩어진 `if item.name != SULFURAS` 조건 3곳을 제거하고
중첩 깊이를 줄인다. 동작 변경 없음.

---

## 변경 범위

`python/gilded_rose.py` 만 수정. 테스트 파일은 건드리지 않음.

---

## 현재 상태 분석

현재 Sulfuras는 코드 세 군데에서 개별적으로 차단된다.

```python
# (A) 14번 줄 — quality 감소 차단
if item.name != SULFURAS:
    item.quality -= 1

# (B) 26번 줄 — sell_in 감소 차단
if item.name != SULFURAS:
    item.sell_in -= 1

# (C) 32번 줄 — 만료 후 quality 감소 차단
if item.name != SULFURAS:
    item.quality -= 1
```

Sulfuras는 "아무것도 하지 않는다"는 단일 규칙인데, 그 표현이 코드 전체에 분산되어 있다.

---

## 변경 내용

루프 시작 직후 Sulfuras를 `continue`로 건너뛴다.

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue
        ...
```

`continue` 이후의 코드는 Sulfuras가 절대 도달하지 않으므로,
(A)(B)(C) 세 곳의 `if item.name != SULFURAS:` 조건을 모두 제거할 수 있다.

---

## 변경 전 / 후 비교

### 변경 전 (현재, Phase 1 결과)

```python
def update_quality(self):
    for item in self.items:
        if item.name != AGED_BRIE and item.name != BACKSTAGE:
            if item.quality > 0:
                if item.name != SULFURAS:        # (A) 제거 대상
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
        if item.name != SULFURAS:                # (B) 제거 대상
            item.sell_in -= 1
        if item.sell_in < 0:
            if item.name != AGED_BRIE:
                if item.name != BACKSTAGE:
                    if item.quality > 0:
                        if item.name != SULFURAS: # (C) 제거 대상
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

---

## 효과

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| SULFURAS 조건 등장 횟수 | 4회 (상수 포함) | 1회 (guard clause) |
| 최대 중첩 깊이 | 5단계 | 4단계 |
| Sulfuras 규칙 표현 위치 | 코드 전체에 분산 | 루프 최상단 한 곳 |

---

## 변경 위치 (Phase 1 결과 기준 줄 번호)

| 줄 | 변경 내용 |
|----|-----------|
| 11 (루프 시작 직후) | `if item.name == SULFURAS: continue` 추가 |
| 14~15 | `if item.name != SULFURAS:` 래퍼 제거, `item.quality -= 1` 한 단계 올림 |
| 26~27 | `if item.name != SULFURAS:` 래퍼 제거, `item.sell_in -= 1` 한 단계 올림 |
| 32~33 | `if item.name != SULFURAS:` 래퍼 제거, `item.quality -= 1` 한 단계 올림 |

---

## 리스크

| 리스크 | 수준 | 비고 |
|--------|------|------|
| 동작 변경 | 없음 | Sulfuras의 three 가드가 one 가드로 통합될 뿐 |
| Sulfuras sell_in < 0 케이스 | 없음 | `continue`로 sell_in 감소 자체가 발생하지 않으므로 기존과 동일 |
| 테스트 파일 영향 | 없음 | |

---

## 검증 방법

```
pytest test_gilded_rose.py --cov=gilded_rose --cov-report=term-missing
```

18개 통과, coverage 100% 유지 확인.
