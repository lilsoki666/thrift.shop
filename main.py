
import json
import os
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


APP_VERSION = "0.1.0"

Window.clearcolor = (0.10, 0.13, 0.12, 1)
Window.size = (960, 540)

STARTING_CASH = 250_000

DEFAULT_ITEMS = [
    {"name": "Vintage Tee", "cost": 25000, "price": 45000, "stock": 8},
    {"name": "Graphic Tee", "cost": 35000, "price": 65000, "stock": 6},
    {"name": "Denim Jacket", "cost": 75000, "price": 125000, "stock": 4},
    {"name": "Retro Sneakers", "cost": 60000, "price": 100000, "stock": 4},
    {"name": "Canvas Bag", "cost": 20000, "price": 40000, "stock": 5},
]


def money(value):
    return "Rp " + f"{int(value):,}".replace(",", ".")


class ShopWorld(Widget):
    """Toko top-down sederhana yang digambar langsung melalui Kivy."""

    COLS = 10
    ROWS = 7

    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
        self.customers = []
        self.spawn_timer = 1.5
        self.elapsed = 0.0
        self.bind(pos=self.draw_world, size=self.draw_world)
        Clock.schedule_interval(self.update_world, 1 / 30)
        Clock.schedule_once(self.draw_world, 0)

    def tile_center(self, tx, ty):
        tile_w = self.width / self.COLS
        tile_h = self.height / self.ROWS
        return (
            self.x + (tx + 0.5) * tile_w,
            self.y + (ty + 0.5) * tile_h,
        )

    def update_world(self, dt):
        self.elapsed += dt

        if not self.game.paused:
            self.spawn_timer -= dt * self.game.speed

            if self.spawn_timer <= 0:
                if len(self.customers) < 4:
                    self.spawn_customer()
                self.spawn_timer = random.uniform(4.0, 7.0)

            self.advance_customers(dt * self.game.speed)

        self.draw_world()

    def spawn_customer(self):
        rack_targets = [(2, 4), (4, 4), (6, 4), (2, 2), (4, 2)]
        target = random.choice(rack_targets)

        self.customers.append({
            "x": 8.7,
            "y": 0.5,
            "target": target,
            "state": "browsing",
            "wait": random.uniform(1.5, 3.0),
            "color": random.choice([
                (0.87, 0.48, 0.31, 1),
                (0.38, 0.66, 0.80, 1),
                (0.90, 0.73, 0.35, 1),
                (0.70, 0.55, 0.79, 1),
                (0.85, 0.82, 0.69, 1),
            ]),
        })
        self.game.notice = "Pelanggan baru masuk ke toko."

    def move_towards(self, customer, target, dt):
        tx, ty = target
        dx = tx - customer["x"]
        dy = ty - customer["y"]
        distance = (dx * dx + dy * dy) ** 0.5

        if distance < 0.12:
            customer["x"] = float(tx)
            customer["y"] = float(ty)
            return True

        step = min(distance, 1.25 * dt)
        customer["x"] += dx / distance * step
        customer["y"] += dy / distance * step
        return False

    def advance_customers(self, dt):
        finished = []

        for customer in self.customers:
            state = customer["state"]

            if state == "browsing":
                if self.move_towards(customer, customer["target"], dt):
                    customer["state"] = "choosing"
                    customer["wait"] = random.uniform(1.0, 2.5)

            elif state == "choosing":
                customer["wait"] -= dt
                if customer["wait"] <= 0:
                    available = [
                        item for item in self.game.items
                        if item["stock"] > 0
                    ]
                    if available:
                        customer["purchase"] = random.choice(available)
                        customer["state"] = "checkout"
                    else:
                        customer["state"] = "leaving"

            elif state == "checkout":
                if self.move_towards(customer, (7, 1), dt):
                    item = customer.get("purchase")
                    if item and item["stock"] > 0:
                        item["stock"] -= 1
                        self.game.cash += item["price"]
                        self.game.revenue += item["price"]
                        self.game.sales += 1
                        self.game.reputation = min(
                            100, self.game.reputation + 1
                        )
                        self.game.notice = (
                            "Terjual: " + item["name"] + " • "
                            + money(item["price"])
                        )
                        self.game.refresh_header()
                        self.game.save_game()
                    customer["state"] = "leaving"

            elif state == "leaving":
                if self.move_towards(customer, (9.1, 0.5), dt):
                    finished.append(customer)

        for customer in finished:
            if customer in self.customers:
                self.customers.remove(customer)

    def draw_world(self, *_):
        if self.width <= 0 or self.height <= 0:
            return

        self.canvas.clear()

        with self.canvas:
            tile_w = self.width / self.COLS
            tile_h = self.height / self.ROWS

            # Lantai toko
            Color(0.73, 0.68, 0.53, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Pola lantai kotak-kotak
            for row in range(self.ROWS):
                for col in range(self.COLS):
                    if (row + col) % 2 == 0:
                        Color(0.78, 0.73, 0.59, 1)
                    else:
                        Color(0.70, 0.65, 0.51, 1)
                    Rectangle(
                        pos=(
                            self.x + col * tile_w,
                            self.y + row * tile_h,
                        ),
                        size=(tile_w, tile_h),
                    )

            # Garis grid
            Color(0.47, 0.44, 0.35, 0.45)
            for col in range(self.COLS + 1):
                x = self.x + col * tile_w
                Line(points=[x, self.y, x, self.top], width=0.6)
            for row in range(self.ROWS + 1):
                y = self.y + row * tile_h
                Line(points=[self.x, y, self.right, y], width=0.6)

            # Rak pakaian
            racks = [
                (1, 4, "TEE"),
                (3, 4, "DENIM"),
                (5, 4, "HOOD"),
                (1, 2, "SHOES"),
                (3, 2, "BAGS"),
            ]

            for tx, ty, _name in racks:
                px, py = self.tile_center(tx, ty)
                Color(0.32, 0.22, 0.16, 1)
                Rectangle(
                    pos=(px - tile_w * 0.40, py - tile_h * 0.28),
                    size=(tile_w * 0.80, tile_h * 0.56),
                )
                Color(0.61, 0.40, 0.25, 1)
                Rectangle(
                    pos=(px - tile_w * 0.35, py - tile_h * 0.18),
                    size=(tile_w * 0.70, tile_h * 0.35),
                )

                # Gantungan dan pakaian berwarna
                clothing_colors = [
                    (0.76, 0.28, 0.23, 1),
                    (0.25, 0.48, 0.69, 1),
                    (0.87, 0.72, 0.40, 1),
                    (0.36, 0.51, 0.37, 1),
                ]
                for n, color in enumerate(clothing_colors):
                    Color(*color)
                    Rectangle(
                        pos=(
                            px - tile_w * 0.29 + n * tile_w * 0.15,
                            py - tile_h * 0.12,
                        ),
                        size=(tile_w * 0.12, tile_h * 0.26),
                    )

            # Meja kasir
            px, py = self.tile_center(7, 1)
            Color(0.34, 0.21, 0.14, 1)
            Rectangle(
                pos=(px - tile_w * 0.42, py - tile_h * 0.32),
                size=(tile_w * 0.84, tile_h * 0.64),
            )
            Color(0.81, 0.61, 0.36, 1)
            Rectangle(
                pos=(px - tile_w * 0.35, py + tile_h * 0.05),
                size=(tile_w * 0.70, tile_h * 0.12),
            )

            # Pintu toko
            dx, dy = self.tile_center(9, 0)
            Color(0.25, 0.37, 0.30, 1)
            Rectangle(
                pos=(dx - tile_w * 0.35, dy - tile_h * 0.40),
                size=(tile_w * 0.70, tile_h * 0.80),
            )
            Color(0.90, 0.79, 0.48, 1)
            Ellipse(
                pos=(dx + tile_w * 0.10, dy),
                size=(tile_w * 0.08, tile_w * 0.08),
            )

            # Karakter kasir
            cx, cy = self.tile_center(7, 0.35)
            self.draw_character(
                cx, cy, tile_w, tile_h, (0.24, 0.38, 0.74, 1)
            )

            # Pelanggan
            for customer in self.customers:
                cx, cy = self.tile_center(
                    customer["x"], customer["y"]
                )
                self.draw_character(
                    cx, cy, tile_w, tile_h, customer["color"]
                )

    def draw_character(self, cx, cy, tile_w, tile_h, color):
        # Bayangan
        Color(0.25, 0.24, 0.20, 0.28)
        Ellipse(
            pos=(cx - tile_w * 0.23, cy - tile_h * 0.20),
            size=(tile_w * 0.46, tile_h * 0.25),
        )

        # Badan
        Color(*color)
        Rectangle(
            pos=(cx - tile_w * 0.17, cy - tile_h * 0.16),
            size=(tile_w * 0.34, tile_h * 0.36),
        )

        # Kepala
        Color(0.91, 0.70, 0.51, 1)
        Rectangle(
            pos=(cx - tile_w * 0.13, cy + tile_h * 0.08),
            size=(tile_w * 0.26, tile_h * 0.25),
        )

        # Rambut
        Color(0.20, 0.17, 0.15, 1)
        Rectangle(
            pos=(cx - tile_w * 0.14, cy + tile_h * 0.26),
            size=(tile_w * 0.28, tile_h * 0.08),
        )


class ThriftShopApp(App):
    title = "Thrift Shop Simulator"

    def build(self):
        self.save_path = os.path.join(
            self.user_data_dir, "thrift_save.json"
        )
        self.load_game()

        self.paused = False
        self.speed = 1.0
        self.notice = "Toko siap buka! Pelanggan akan datang otomatis."

        self.root_box = BoxLayout(
            orientation="vertical",
            padding=dp(7),
            spacing=dp(5),
        )

        self.header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(54),
            spacing=dp(8),
        )
        self.root_box.add_widget(self.header)

        self.world = ShopWorld(
            self,
            size_hint=(1, 1),
        )
        self.root_box.add_widget(self.world)

        self.status = Label(
            text="",
            size_hint_y=None,
            height=dp(28),
            font_size=dp(12),
            color=(0.95, 0.84, 0.61, 1),
        )
        self.root_box.add_widget(self.status)

        controls = GridLayout(
            cols=5,
            size_hint_y=None,
            height=dp(48),
            spacing=dp(5),
        )
        controls.add_widget(self.make_button(
            "JEDA", self.toggle_pause, (0.55, 0.35, 0.20, 1)
        ))
        controls.add_widget(self.make_button(
            "2X", self.toggle_speed, (0.25, 0.39, 0.52, 1)
        ))
        controls.add_widget(self.make_button(
            "ISI STOK", self.restock, (0.22, 0.49, 0.34, 1)
        ))
        controls.add_widget(self.make_button(
            "LAPORAN", self.report, (0.38, 0.35, 0.53, 1)
        ))
        controls.add_widget(self.make_button(
            "SIMPAN", self.manual_save, (0.24, 0.36, 0.40, 1)
        ))
        self.root_box.add_widget(controls)

        self.refresh_header()
        Clock.schedule_interval(self.update_status, 0.5)
        return self.root_box

    def load_game(self):
        try:
            with open(self.save_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.cash = int(data.get("cash", STARTING_CASH))
            self.day = int(data.get("day", 1))
            self.reputation = int(data.get("reputation", 50))
            self.sales = int(data.get("sales", 0))
            self.revenue = int(data.get("revenue", 0))
            saved_items = data.get("items", [])
            self.items = saved_items or [
                item.copy() for item in DEFAULT_ITEMS
            ]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.cash = STARTING_CASH
            self.day = 1
            self.reputation = 50
            self.sales = 0
            self.revenue = 0
            self.items = [item.copy() for item in DEFAULT_ITEMS]

    def save_game(self):
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        data = {
            "cash": self.cash,
            "day": self.day,
            "reputation": self.reputation,
            "sales": self.sales,
            "revenue": self.revenue,
            "items": self.items,
        }
        temporary = self.save_path + ".tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        os.replace(temporary, self.save_path)

    def make_button(self, text, callback, color):
        button = Button(
            text=text,
            font_size=dp(12),
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_down="",
            background_color=color,
        )
        button.bind(on_release=lambda *_: callback())
        return button

    def refresh_header(self):
        if not hasattr(self, "header"):
            return

        self.header.clear_widgets()
        info = (
            f"THRIFT SHOP  |  HARI {self.day}\n"
            f"KAS {money(self.cash)}"
        )
        self.header.add_widget(Label(
            text=info,
            halign="left",
            font_size=dp(14),
            bold=True,
            color=(0.97, 0.79, 0.45, 1),
        ))
        self.header.add_widget(Label(
            text=f"REPUTASI {self.reputation}/100\n"
                 f"TERJUAL {self.sales} BARANG",
            halign="right",
            font_size=dp(12),
            color=(0.82, 0.90, 0.80, 1),
        ))

    def update_status(self, _dt):
        if not hasattr(self, "status"):
            return
        mode = "DIJEDA" if self.paused else (
            "SIMULASI 2X" if self.speed > 1 else "TOKO BUKA"
        )
        self.status.text = (
            f"{mode}  •  Pelanggan: {len(self.world.customers)}"
            f"  •  {self.notice}"
        )

    def toggle_pause(self):
        self.paused = not self.paused
        self.notice = "Simulasi dijeda." if self.paused else "Toko kembali berjalan."

    def toggle_speed(self):
        self.speed = 2.0 if self.speed == 1.0 else 1.0
        self.notice = "Kecepatan simulasi: " + str(int(self.speed)) + "x"

    def restock(self):
        if self.paused:
            self.notice = "Lanjutkan simulasi sebelum mengisi stok."
            return

        affordable = [
            item for item in self.items
            if self.cash >= item["cost"]
        ]
        if not affordable:
            self.notice = "Uang tidak cukup untuk membeli stok."
            return

        item = min(affordable, key=lambda product: product["cost"])
        self.cash -= item["cost"]
        item["stock"] += 3
        self.notice = (
            f"Tambah 3 unit {item['name']} • "
            f"-{money(item['cost'])}"
        )
        self.refresh_header()
        self.save_game()

    def report(self):
        self.paused = True
        self.notice = (
            f"Laporan: {self.sales} barang terjual, "
            f"pendapatan {money(self.revenue)}, "
            f"uang {money(self.cash)}. Tekan JEDA untuk lanjut."
        )

    def manual_save(self):
        self.save_game()
        self.notice = "Game berhasil disimpan."
        self.refresh_header()

    def on_pause(self):
        self.save_game()
        return True

    def on_stop(self):
        self.save_game()


if __name__ == "__main__":
    ThriftShopApp().run()
