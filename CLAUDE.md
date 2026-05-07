# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 작업 범위

이 저장소는 GildedRose Refactoring Kata이며, **Python 구현(`python/`)만 작업 대상**이다. `Java/`, `cpp/`는 무시한다.

---

## 테스트 실행

```bash
# 전체 테스트 + 커버리지
cd python
pytest test_gilded_rose.py -v --cov=gilded_rose --cov-report=term-missing

# 단일 테스트
pytest test_gilded_rose.py::test_normal_item_decreases_quality_before_sell_date -v
```

현재 테스트: **18개, coverage 100%**. 모든 리팩토링 단계 후에도 이 상태를 유지해야 한다.

---

## 코드 구조

```
python/
  gilded_rose.py        # GildedRose (update_quality), Item 클래스
  test_gilded_rose.py   # pytest 테스트
  texttest_fixture.py   # 수동 확인용 픽스처 (수정 불필요)
docs/
  plan.md               # 6단계 리팩토링 로드맵
  design/
    phase1_cosmetic.md  # 각 Phase의 세부 설계 문서
```

### 핵심 제약

- `Item` 클래스와 `self.items` 속성은 **절대 수정 금지** (카타 규칙)
- `GildedRose.update_quality()`는 자유롭게 변경 가능

### 아이템 규칙 요약

| 아이템 | 동작 |
|--------|------|
| 일반 | sell_in, quality 매일 -1. 만료 후 quality -2 |
| Aged Brie | quality 매일 +1. 만료 후 +2. 상한 50 |
| Sulfuras, Hand of Ragnaros | sell_in, quality 모두 불변. quality 고정값 80 |
| Backstage passes to a TAFKAL80ETC concert | 10일 이하 +2, 5일 이하 +3. 만료 후 quality = 0 |
| Conjured (미구현) | 일반의 2배 속도로 quality 감소 |

---

## 리팩토링 진행 방식

**각 Phase는 반드시 아래 순서로 진행한다:**

1. `docs/design/phase{N}_*.md` 설계 문서 작성
2. 사용자 검토 및 승인 대기
3. 승인 후 `gilded_rose.py` 수정
4. 테스트 전체 통과 확인

### Phase 로드맵 (`docs/plan.md` 참고)

| Phase | 내용 | 동작 변경 | 상태 |
|-------|------|-----------|------|
| 0 | UnitTest 확보 (18개, coverage 100%) | 없음 | 완료 |
| 1 | 매직 스트링 → 상수, `+=/-=` 표현 정리 | 없음 | 완료 |
| 2 | Sulfuras guard clause, 중첩 제거 | 없음 | 미시작 |
| 3 | `_increment_quality` / `_decrement_quality` 헬퍼 추출 | 없음 | 미시작 |
| 4 | sell_in 감소 타이밍 통합 (quality 이중 변경 제거) | 없음 | 미시작 |
| 5 | 아이템 타입별 메서드 분리, dispatch 패턴 | 없음 | 미시작 |
| 6 | Conjured 아이템 추가 (TDD) | 있음(신규) | 미시작 |

### 현재 진행 위치

Phase 1 완료. Phase 2 설계 문서 작성 전.
