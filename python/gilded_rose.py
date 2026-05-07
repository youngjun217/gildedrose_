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

    def _increment_quality(self, item, amount=1):
        item.quality = min(50, item.quality + amount)

    def _decrement_quality(self, item, amount=1):
        item.quality = max(0, item.quality - amount)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
