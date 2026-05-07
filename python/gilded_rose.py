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


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
