import pytest
from gilded_rose import Item, GildedRose

BACKSTAGE = "Backstage passes to a TAFKAL80ETC concert"
SULFURAS = "Sulfuras, Hand of Ragnaros"
AGED_BRIE = "Aged Brie"


def update(items):
    GildedRose(items).update_quality()
    return items


# ---------------------------------------------------------------------------
# Normal item
# ---------------------------------------------------------------------------

def test_normal_item_decreases_quality_before_sell_date():
    items = update([Item("normal", 5, 10)])
    assert items[0].quality == 9
    assert items[0].sell_in == 4


def test_normal_item_zero_quality_stays_zero():
    items = update([Item("normal", 5, 0)])
    assert items[0].quality == 0
    assert items[0].sell_in == 4


def test_normal_item_quality_decreases_twice_after_sell_date():
    # sell_in 0 → -1: quality는 만료 전 -1, 만료 후 -1 총 2 감소
    items = update([Item("normal", 0, 5)])
    assert items[0].quality == 3
    assert items[0].sell_in == -1


def test_normal_item_quality_does_not_go_below_zero_after_sell_date():
    # 첫 번째 감소로 quality가 0이 된 뒤 만료 후 추가 감소 없음
    items = update([Item("normal", 0, 1)])
    assert items[0].quality == 0
    assert items[0].sell_in == -1


# ---------------------------------------------------------------------------
# Aged Brie
# ---------------------------------------------------------------------------

def test_aged_brie_increases_quality():
    items = update([Item(AGED_BRIE, 5, 10)])
    assert items[0].quality == 11
    assert items[0].sell_in == 4


def test_aged_brie_max_quality_stays_at_50():
    items = update([Item(AGED_BRIE, 5, 50)])
    assert items[0].quality == 50
    assert items[0].sell_in == 4


def test_aged_brie_increases_quality_twice_after_sell_date():
    items = update([Item(AGED_BRIE, 0, 10)])
    assert items[0].quality == 12
    assert items[0].sell_in == -1


def test_aged_brie_max_quality_stays_at_50_after_sell_date():
    # quality가 이미 50이면 만료 후에도 증가 없음
    items = update([Item(AGED_BRIE, 0, 50)])
    assert items[0].quality == 50
    assert items[0].sell_in == -1


# ---------------------------------------------------------------------------
# Sulfuras
# ---------------------------------------------------------------------------

def test_sulfuras_never_changes():
    items = update([Item(SULFURAS, 0, 80)])
    assert items[0].quality == 80
    assert items[0].sell_in == 0


def test_sulfuras_never_changes_when_already_expired():
    # sell_in이 이미 음수여도 quality와 sell_in 모두 변하지 않아야 함
    items = update([Item(SULFURAS, -1, 80)])
    assert items[0].quality == 80
    assert items[0].sell_in == -1


# ---------------------------------------------------------------------------
# Backstage passes
# ---------------------------------------------------------------------------

def test_backstage_pass_increases_by_1_long_before_concert():
    # sell_in >= 11: quality +1
    items = update([Item(BACKSTAGE, 15, 10)])
    assert items[0].quality == 11
    assert items[0].sell_in == 14


def test_backstage_pass_increases_by_2_within_10_days():
    # sell_in == 10 (< 11): quality +2
    items = update([Item(BACKSTAGE, 10, 10)])
    assert items[0].quality == 12
    assert items[0].sell_in == 9


def test_backstage_pass_increases_by_3_within_5_days():
    # sell_in == 5 (< 6): quality +3
    items = update([Item(BACKSTAGE, 5, 10)])
    assert items[0].quality == 13
    assert items[0].sell_in == 4


def test_backstage_pass_quality_capped_at_50_in_10_day_window():
    # +1 후 50이 되면 두 번째 +1(11일 이내 보너스)은 적용되지 않음
    items = update([Item(BACKSTAGE, 10, 49)])
    assert items[0].quality == 50
    assert items[0].sell_in == 9


def test_backstage_pass_quality_capped_at_50_in_5_day_window():
    # 두 번째 +1 후 50이 되면 세 번째 +1(6일 이내 보너스)은 적용되지 않음
    items = update([Item(BACKSTAGE, 5, 48)])
    assert items[0].quality == 50
    assert items[0].sell_in == 4


def test_backstage_pass_quality_drops_to_zero_after_concert():
    # sell_in 0 → -1: 콘서트 이후 quality는 0
    items = update([Item(BACKSTAGE, 0, 20)])
    assert items[0].quality == 0
    assert items[0].sell_in == -1


def test_backstage_pass_at_max_quality_does_not_exceed_50():
    # quality가 이미 50이면 보너스 없이 그대로
    items = update([Item(BACKSTAGE, 15, 50)])
    assert items[0].quality == 50
    assert items[0].sell_in == 14


# ---------------------------------------------------------------------------
# Item.__repr__
# ---------------------------------------------------------------------------

def test_item_repr():
    assert repr(Item("normal", 5, 10)) == "normal, 5, 10"
