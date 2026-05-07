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


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
