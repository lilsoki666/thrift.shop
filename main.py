
import json
import os
import random

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget

__version__ = "0.1.0"

Window.clearcolor = (0.10, 0.12, 0.13, 1)

STARTING_CASH = 250_000

STARTER_ITEMS = [
    {"name": "Vintage Tee", "cost": 25000, "price": 45000,
     "stock": 4, "rarity": "Common", "icon": "👕"},
    {"name": "Graphic Tee", "cost": 35000, "price": 65000,
     "stock": 3, "rarity": "Uncommon", "icon": "🎽"},
    {"name": "Denim Jacket", "cost": 75000, "price": 125000,
     "stock": 2, "rarity": "Rare", "icon": "🧥"},
    {"name": "Retro Sneakers", "cost": 60000, "price": 100000,
     "stock": 2, "rarity": "Uncommon", "icon": "👟"},
    {"name": "Canvas Bag", "cost": 20000, "price": 40000,
     "stock": 3, "rarity": "Common", "icon": "👜"},
]


class ThriftGame(App):
    title = "Thrift Shop Simulator"

    def build(self):
        self.save_path = os.path.join(
            self.user_data_dir, "thrift_save.json"
        )
        self.load_game()
        self.page = "shop"
        self.notice = "Selamat datang! Buka toko dan mulai berjualan."
        self.root_box = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8),
        )
        self.refresh()
        return self.root_box

    def load_game(self):
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.cash = int(data.get("cash", STARTING_CASH))
            self.day = int(data.get("day", 1))
            self.reputation = int(data.get("reputation", 50))
            self.items = data.get("items", STARTER_ITEMS.copy())
            self.sales = int(data.get("sales", 0))
            self.revenue = int(data.get("revenue", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.cash = STARTING_CASH
            self.day = 1
            self.reputation = 50
            self.items = [item.copy() for item in STARTER_ITEMS]
            self.sales = 0
            self.revenue = 0

    def save_game(self):
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        data = {
            "cash": self.cash,
            "day": self.day,
            "reputation": self.reputation,
            "items": self.items,
            "sales": self.sales,
            "revenue": self.revenue,
        }
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def money(value):
        return "Rp " + f"{int(value):,}".replace(",", ".")

    def label(self, text, size=16, color=(1, 1, 1, 1),
              height=dp(34), bold=False):
        return Label(
            text=text,
            font_size=sp(size),
            color=color,
            bold=bold,
            size_hint_y=None,
            height=height,
            halign="left",
            valign="middle",
        )

    def button(self, text, callback, color=(0.24, 0.43, 0.31, 1),
               height=dp(46)):
        btn = Button(
            text=text,
            size_hint_y=None,
            height=height,
            background_normal="",
            background_down="",
            background_color=color,
            color=(1, 1, 1, 1),
            font_size=sp(15),
            bold=True,
        )
        btn.bind(on_release=lambda *_: callback())
        return btn

    def refresh(self):
        self.root_box.clear_widgets()

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(112),
            spacing=dp(3),
        )
        header.add_widget(self.label(
            "THRIFT SHOP",
            26, (0.98, 0.77, 0.39, 1), dp(40), True
        ))
        header.add_widget(self.label(
            f"HARI {self.day}   |   "
            f"KAS {self.money(self.cash)}   |   "
            f"REPUTASI {self.reputation}/100",
            14, (0.84, 0.91, 0.82, 1), dp(28), True
        ))
        header.add_widget(self.label(
            self.notice, 13, (1, 0.84, 0.58, 1), dp(34)
        ))
        self.root_box.add_widget(header)

        nav = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(44),
            spacing=dp(5),
        )
        nav.add_widget(self.button("TOKO", lambda: self.change_page("shop")))
        nav.add_widget(self.button("GUDANG", lambda: self.change_page("stock")))
        nav.add_widget(self.button("LAPORAN", lambda: self.change_page("report")))
        self.root_box.add_widget(nav)

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
        )
        self.root_box.add_widget(self.content)

        if self.page == "shop":
            self.show_shop()
        elif self.page == "stock":
            self.show_stock()
        else:
            self.show_report()

        footer = GridLayout(
            cols=2,
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6),
        )
        footer.add_widget(self.button(
            "TUTUP HARI", self.end_day, (0.57, 0.31, 0.21, 1)
        ))
        footer.add_widget(self.button(
            "SIMPAN GAME", self.manual_save, (0.23, 0.36, 0.51, 1)
        ))
        self.root_box.add_widget(footer)

    def change_page(self, page):
        self.page = page
        self.refresh()

    def show_shop(self):
        self.content.add_widget(self.label(
            "TOKO HARI INI", 19, (0.98, 0.77, 0.39, 1),
            dp(36), True
        ))
        self.content.add_widget(self.label(
            "Pilih barang untuk melayani pelanggan.", 13
        ))

        scroll = ScrollView()
        listing = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None,
            padding=(0, dp(4)),
        )
        listing.bind(minimum_height=listing.setter("height"))

        for index, item in enumerate(self.items):
            card = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(82),
                padding=dp(7),
                spacing=dp(8),
            )
            card.add_widget(Label(
                text=f"{item['icon']}  {item['name']}\n"
                     f"{item['rarity']}  |  Stok: {item['stock']}\n"
                     f"Harga: {self.money(item['price'])}",
                color=(1, 1, 1, 1),
                font_size=sp(13),
                halign="left",
                valign="middle",
            ))
            card.add_widget(self.button(
                "JUAL 1",
                lambda i=index: self.sell_item(i),
                (0.20, 0.49, 0.34, 1),
                dp(54),
            ))
            listing.add_widget(card)

        scroll.add_widget(listing)
        self.content.add_widget(scroll)

    def show_stock(self):
        self.content.add_widget(self.label(
            "PEMASOK & STOK", 20, (0.98, 0.77, 0.39, 1),
            dp(38), True
        ))
        self.content.add_widget(self.label(
            "Beli satu unit barang untuk menambah persediaan."
        ))

        scroll = ScrollView()
        listing = GridLayout(
            cols=1, spacing=dp(8), size_hint_y=None
        )
        listing.bind(minimum_height=listing.setter("height"))

        for index, item in enumerate(self.items):
            listing.add_widget(self.label(
                f"{item['icon']}  {item['name']} — "
                f"{self.money(item['cost'])} / unit"
                f"   (stok {item['stock']})",
                14, height=dp(44)
            ))
            listing.add_widget(self.button(
                f"BELI 1  •  {self.money(item['cost'])}",
                lambda i=index: self.buy_item(i),
                (0.29, 0.39, 0.49, 1),
            ))

        scroll.add_widget(listing)
        self.content.add_widget(scroll)

    def show_report(self):
        self.content.add_widget(self.label(
            "LAPORAN BISNIS", 20,
            (0.98, 0.77, 0.39, 1), dp(40), True
        ))
        for line in [
            f"Hari berjalan: {self.day}",
            f"Total barang terjual: {self.sales}",
            f"Pendapatan kotor: {self.money(self.revenue)}",
            f"Uang saat ini: {self.money(self.cash)}",
            f"Reputasi toko: {self.reputation}/100",
            f"Jenis barang: {len(self.items)}",
            f"Total unit stok: {sum(i['stock'] for i in self.items)}",
        ]:
            self.content.add_widget(self.label(line, 15, height=dp(40)))

        self.content.add_widget(Widget())

    def sell_item(self, index):
        item = self.items[index]
        if item["stock"] <= 0:
            self.notice = "Stok habis! Buka Gudang untuk membeli stok."
        else:
            item["stock"] -= 1
            self.cash += item["price"]
            self.revenue += item["price"]
            self.sales += 1
            self.reputation = min(100, self.reputation + 1)
            self.notice = (
                f"Terjual: {item['name']}! "
                f"+{self.money(item['price'])}"
            )
        self.save_game()
        self.refresh()

    def buy_item(self, index):
        item = self.items[index]
        if self.cash < item["cost"]:
            self.notice = "Uang tidak cukup untuk membeli stok."
        else:
            self.cash -= item["cost"]
            item["stock"] += 1
            self.notice = f"Stok {item['name']} berhasil ditambah."
        self.save_game()
        self.refresh()

    def end_day(self):
        customer_bonus = random.randint(0, 3)
        if customer_bonus:
            self.reputation = min(100, self.reputation + 1)
            self.notice = (
                f"Hari selesai! Ada {customer_bonus} pelanggan puas. "
                "Toko siap dibuka lagi."
            )
        else:
            self.notice = "Hari selesai. Besok coba tarik lebih banyak pelanggan."
        self.day += 1
        self.save_game()
        self.refresh()

    def manual_save(self):
        self.save_game()
        self.notice = "Game berhasil disimpan."
        self.refresh()


def sp(value):
    return dp(value)


if __name__ == "__main__":
    ThriftGame().run()
