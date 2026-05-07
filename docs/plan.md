# GildedRose Python Refactoring Plan

## 원칙

- 각 단계 완료 후 테스트 전체 통과 확인 (18개, coverage 100%)
- 작은 변경 → 구조 개선 → 설계 변경 순서로 진행
- `Item` 클래스는 수정 금지 (카타 규칙)

---

## Step 0. UnitTest 확보 (완료)

**목표**: 리팩토링 안전망 확보

- `test_gilded_rose.py` 작성 완료
- 18개 테스트, coverage 100%
- 이후 모든 단계에서 테스트가 계속 통과해야 함

---

## Step 1. 표현 정리 (Cosmetic)

**목표**: 의도를 더 명확하게 드러내는 표현으로 교체. 동작 변경 없음.

### 1-1. 매직 스트링 → 상수

```python
# Before
if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":

# After
AGED_BRIE = "Aged Brie"
BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS  = "Sulfuras, Hand of Ragnaros"
```

- 오탈자를 컴파일 타임(이름 오류)에 발견 가능
- 변경 위치: `gilded_rose.py` 상단

### 1-2. 산술 표현 단순화

```python
# Before
item.quality = item.quality - 1
item.quality = item.quality + 1
item.sell_in = item.sell_in - 1
item.quality = item.quality - item.quality

# After
item.quality -= 1
item.quality += 1
item.sell_in -= 1
item.quality = 0
```

**검증**: 테스트 전체 통과

---

## Step 2. Guard Clause로 중첩 제거

**목표**: Sulfuras는 아무것도 안 하므로 루프 최상단에서 조기 처리. 나머지 코드의 중첩 깊이 감소.

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            continue                    # 이후 로직 전체 건너뜀

        # Sulfuras 아닌 경우만 아래 실행
        ...
        item.sell_in -= 1
        ...
```

- Sulfuras 관련 `if name != SULFURAS` 조건 3곳이 제거됨 (9, 21, 27번 줄)
- 중첩 최대 깊이 4 → 3으로 감소

**검증**: 테스트 전체 통과

---

## Step 3. 품질 변경 헬퍼 메서드 추출

**목표**: quality 상한(50)/하한(0) 체크가 여러 곳에 흩어져 있으므로 한 곳으로 모음.

```python
def _increment_quality(self, item, amount=1):
    item.quality = min(50, item.quality + amount)

def _decrement_quality(self, item, amount=1):
    item.quality = max(0, item.quality - amount)
```

- 중복된 `if item.quality < 50` / `if item.quality > 0` 조건 제거
- 만료 전/후 quality 변경 코드가 동일한 API 사용

**검증**: 테스트 전체 통과

---

## Step 4. 만료 전/후 분리 로직 통합

**목표**: 현재 sell_in 감소를 기준으로 quality 업데이트가 앞뒤로 쪼개져 있음.
한 번의 `update_quality()` 호출에서 quality가 두 번 변경되는 구조를 정리.

```
현재 흐름 (sell_in=0 일반 아이템):
  1) quality -= 1   (만료 전 처리)
  2) sell_in -= 1   → -1
  3) quality -= 1   (만료 후 처리, 별도 블록)

변경 후 흐름:
  1) sell_in -= 1   → -1   (먼저 감소)
  2) expired = sell_in < 0 여부 판단
  3) 만료 여부에 따라 quality 한 번만 처리
```

- 각 아이템 타입의 처리 로직이 하나의 연속된 블록으로 정리됨
- Step 5의 메서드 분리를 위한 선행 작업

**검증**: 테스트 전체 통과

---

## Step 5. 아이템 타입별 메서드 분리

**목표**: `update_quality`가 dispatch만 담당하고, 각 타입의 로직은 별도 메서드로 분리.

```python
def update_quality(self):
    for item in self.items:
        if item.name == SULFURAS:
            pass
        elif item.name == AGED_BRIE:
            self._update_aged_brie(item)
        elif item.name == BACKSTAGE:
            self._update_backstage(item)
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
        self._increment_quality(item, 1)
```

- `update_quality`의 중첩 완전 제거
- 각 타입의 동작을 독립적으로 읽고 테스트 가능

**검증**: 테스트 전체 통과

---

## Step 6. Conjured 아이템 추가 (기능 확장)

**목표**: Step 5의 구조 덕분에 기존 코드 수정 없이 새 타입을 추가 가능함을 검증.

- 규칙: 하루에 quality 2 감소, 만료 후 4 감소
- 테스트 먼저 작성 (TDD)

```python
CONJURED = "Conjured Mana Cake"

def _update_conjured(self, item):
    item.sell_in -= 1
    amount = 4 if item.sell_in < 0 else 2
    self._decrement_quality(item, amount)
```

- `update_quality`의 dispatch에 `elif item.name == CONJURED:` 한 줄만 추가
- OCP 준수 검증

**검증**: 신규 테스트 포함 전체 통과

---

## 단계별 요약

| 단계 | 변경 범위 | 동작 변경 | 목적 |
|------|-----------|-----------|------|
| Step 0 | 테스트 파일 | 없음 | 안전망 확보 |
| Step 1 | 표현만 교체 | 없음 | 가독성 |
| Step 2 | Guard clause | 없음 | 중첩 감소 |
| Step 3 | 헬퍼 추출 | 없음 | 중복 제거 |
| Step 4 | 로직 순서 통합 | 없음 | 흐름 단순화 |
| Step 5 | 메서드 분리 | 없음 | SRP / OCP 기반 마련 |
| Step 6 | 기능 추가 | 있음 (신규) | OCP 준수 검증 |
