import datetime
from statistics import mean

from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    TRANSLATIONS = {
        "en": {
            "today": "Today",
            "now": "Now",
            "feels": "Feels like",
            "pressure": "Pressure",
            "humidity": "Humidity",
            "wind_speed": "Wind speed",
            "wind_dir": "Wind direction",
            "unit_pressure": "mm Hg",
            "unit_wind": "m/s",
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "dirs": {
                "N_0": "North", "NE": "North-East", "E": "East",
                "SE": "South-East", "S": "South", "SW": "South-West",
                "W": "West", "NW": "North-West", "N_360": "North"
            }
        },
        "ru": {
            "today": "Сегодня",
            "now": "Сейчас",
            "feels": "Ощущается как",
            "pressure": "Давление",
            "humidity": "Влажность",
            "wind_speed": "Скорость ветра",
            "wind_dir": "Направление ветра",
            "unit_wind": "м/с",
            "weekdays": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "unit_pressure": "мм рт.ст.",
            "dirs": {
                "N_0": "Северный", "NE": "Северо-восточный", "E": "Восточный",
                "SE": "Юго-восточный", "S": "Южный", "SW": "Юго-западный",
                "W": "Западный", "NW": "Северо-западный", "N_360": "Северный"
            }
        }
    }

    def __init__(self,
                 current: dict,
                 bg_dir: str = "/home/grigoscope/weatherly/weatherly/images/backgrounds/",
                 icon_dir: str = "/home/grigoscope/weatherly/weatherly/images/icons/",
                 lang: str = "ru"):
        self.current = current
        self.bg_dir = bg_dir.rstrip("/") + "/"
        self.icon_dir = icon_dir.rstrip("/") + "/"
        self.lang = lang if lang in ("en", "ru") else "ru"
        self.font_big = ImageFont.truetype("calibri.ttf", 120)
        self.font_mid = ImageFont.truetype("calibri.ttf", 65)
        self.font_small = ImageFont.truetype("calibri.ttf", 45)
        self.font_center = ImageFont.truetype("calibri.ttf", 120)

    def curr_weather_img(self) -> Image.Image:
        code = self.current["icon"][-1]
        img = Image.open(f"{self.bg_dir}background_{code}.png").convert("RGBA")
        draw = ImageDraw.Draw(img)
        W, H = img.size
        x, y = 50, 50

        draw.text((x, y), self.current["name"], font=self.font_mid, fill="white")
        _, _, _, h = draw.textbbox((0, 0), self.current["name"], font=self.font_mid)
        y += h + 20

        cond = self.current["condition"]
        try:
            ico = Image.open(f"{self.icon_dir}{self.current['icon']}.png").convert("RGBA")
            _, _, _, ch = draw.textbbox((0, 0), cond, font=self.font_small)
            ico = ico.resize((ch, ch), Image.LANCZOS)
            img.paste(ico, (x, y), ico)
            tx = x + ico.width + 10
        except:
            tx = x
        draw.text((tx, y), cond, font=self.font_small, fill="white")
        _, _, _, h = draw.textbbox((0, 0), cond, font=self.font_small)
        y += h + 40

        temp = f"{self.current['temp']}°C"
        draw.text((x, y), temp, font=self.font_big, fill="white")
        _, _, _, h = draw.textbbox((0, 0), temp, font=self.font_big)
        y += h

        now = self.TRANSLATIONS[self.lang]["now"]
        bx0, by0, bx1, by1 = draw.textbbox((0, 0), now, font=self.font_center)
        tw, th = bx1 - bx0, by1 - by0
        draw.text(((W - tw) / 2, (H - th) / 2 - 50), now, font=self.font_center, fill="white")

        t = self.TRANSLATIONS[self.lang]
        keys = ["feels", "pressure", "humidity", "wind_speed", "wind_dir"]
        icons = {k: Image.open(f"{self.icon_dir}{k}.png").convert("RGBA") for k in keys}
        md = {
            "feels": f"{self.current['feels_like']}°C",
            "pressure": f"{self.current['pressure']} {t['unit_pressure']}",
            "humidity": f"{self.current['humidity']}%",
            "wind_speed": f"{self.current['wind_speed']} {'м/с' if self.lang == 'ru' else 'm/s'}",
            "wind_dir": t["dirs"].get(self.current["wind_dir"], self.current["wind_dir"])
        }
        ICON_SIZE = 48
        PAD = 20
        y0 = H - len(keys) * (ICON_SIZE + PAD) - 50
        for k in keys:
            ic = icons[k].resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
            img.paste(ic, (x, y0), ic)
            text = f"{t[k]}: {md[k]}"
            _, _, _, th = draw.textbbox((0, 0), text, font=self.font_small)
            draw.text((x + ICON_SIZE + 10, y0 + (ICON_SIZE - th) / 2),
                      text, font=self.font_small, fill="white")
            y0 += ICON_SIZE + PAD

        return img

    def daily_forecast_img(self, forecast: list[dict]) -> Image.Image:
        code = forecast[0]["icon"][-1]
        img = Image.open(f"{self.bg_dir}background_{code}.png").convert("RGBA")
        draw = ImageDraw.Draw(img)
        W, H = img.size

        x, y = 50, 50
        avg_temp = int(mean(e["temp"] for e in forecast))
        draw.text((x, y), self.current["name"], font=self.font_mid, fill="white")
        y += draw.textbbox((0, 0), self.current["name"], font=self.font_mid)[3] + 10
        draw.text((x, y), f"{avg_temp}°C",       font=self.font_big, fill="white")

        lbl = self.TRANSLATIONS[self.lang]["today"]
        bx0, by0, bx1, by1 = draw.textbbox((0, 0), lbl, font=self.font_big)
        tw, th = bx1 - bx0, by1 - by0
        cx, cy = (W - tw) // 2, (H - th) // 2 - 80
        draw.text((cx, cy), lbl, font=self.font_big, fill="white")

        t = self.TRANSLATIONS[self.lang]
        ps = sum(e["pressure"] for e in forecast) // len(forecast)
        hs = sum(e["humidity"] for e in forecast) // len(forecast)
        ws = sum(e["wind_speed"] for e in forecast) // len(forecast)
        metrics = [
            ("humidity", f"{hs}%"),
            ("pressure", f"{ps} {t['unit_pressure']}"),
            ("wind_speed", f"{ws} {'м/с' if self.lang == 'ru' else 'm/s'}")
        ]
        ICON_M = 36
        gap = 10
        y1 = cy + th + 140
        margin_x = 200
        step = (W - 2 * margin_x) / 2
        xs = [margin_x + i * step for i in range(3)]

        for (key, val), px in zip(metrics, xs):
            ico = Image.open(f"{self.icon_dir}{key}.png") \
                .convert("RGBA") \
                .resize((ICON_M, ICON_M), Image.LANCZOS)
            ix = int(px - (ICON_M + gap + draw.textbbox((0, 0), val, font=self.font_small)[2]) / 2)
            img.paste(ico, (ix, int(y1 - ICON_M / 2)), ico)
            draw.text((ix + ICON_M + gap, y1),
                      val,
                      font=self.font_small,
                      fill="white",
                      anchor="lm")

        margin = 120
        left, right = margin, W - margin
        n = len(forecast)
        step = (right - left) / (n - 1)
        base_y = H - 160
        temps = [e["temp"] for e in forecast]
        tmin, tmax = min(temps), max(temps)
        span_h = 120

        points = []
        for i, e in enumerate(forecast):
            xi = left + i * step
            yi = base_y - (e["temp"] - tmin) / (tmax - tmin or 1) * span_h
            points.append((xi, yi))
        draw.line(points, fill="white", width=4)

        ICON_SZ = 48
        TEMP_OFF = ICON_SZ + 10
        HOUR_OFF = 40

        for (xi, yi), e in zip(points, forecast):
            ico = Image.open(f"{self.icon_dir}{e['icon']}.png") \
                .convert("RGBA") \
                .resize((ICON_SZ, ICON_SZ), Image.LANCZOS)
            img.paste(ico, (int(xi - ICON_SZ / 2), int(yi - ICON_SZ)), ico)
            draw.text((xi, yi - TEMP_OFF),
                      f"{e['temp']}°",
                      font=self.font_small,
                      fill="white",
                      anchor="mm")
            hr = e["datetime"][11:13]
            draw.text((xi, base_y + HOUR_OFF),
                      hr,
                      font=self.font_small,
                      fill="white",
                      anchor="mm")

        return img

    def five_days_img(self, forecast: list[dict]) -> Image.Image:
        groups = {}
        for e in forecast:
            day = e["datetime"].split()[0]
            groups.setdefault(day, []).append(e)

        dates = sorted(groups.keys())
        today, *others = dates
        next5 = others[:5]

        def summarize(lst):
            temps = [d["temp"] for d in lst]
            prs = [d["pressure"] for d in lst]
            hums = [d["humidity"] for d in lst]
            winds = [d["wind_speed"] for d in lst]

            ref = min(lst, key=lambda d: abs(int(d["datetime"][11:13]) - 12))
            return {
                "high": int(max(temps)),
                "low": int(min(temps)),
                "press": int(mean(prs)),
                "hum": int(mean(hums)),
                "wind": int(mean(winds)),
                "icon": ref["icon"],
                "desc": ref.get("condition", "").capitalize()
            }

        today_s = summarize(groups[today])
        days_s = [(d, summarize(groups[d])) for d in next5]

        bgc = today_s["icon"][-1]
        img = Image.open(f"{self.bg_dir}background_{bgc}.png").convert("RGBA")
        draw = ImageDraw.Draw(img)
        W, H = img.size

        bh = H // 3
        draw.rounded_rectangle(
            (20, 20, W - 20, bh),
            radius=25,
            outline=(0, 0, 50, 200),
            width=4
        )

        lbl = self.TRANSLATIONS[self.lang]["today"]
        unit_p = self.TRANSLATIONS[self.lang]["unit_pressure"]
        unit_w = self.TRANSLATIONS[self.lang]["unit_wind"]

        y0 = 60
        draw.text((W / 2, y0), lbl,
                  font=self.font_big, fill="white",
                  anchor="ma")

        y1 = y0 + self.font_big.getbbox(lbl)[3] + 15
        hl_txt = f"{today_s['high']}/{today_s['low']}°"
        draw.text((W / 2, y1), hl_txt,
                  font=self.font_big, fill="white",
                  anchor="ma")

        y2 = y1 + self.font_big.getbbox(hl_txt)[3] + 15
        draw.text((W / 2, y2), today_s["desc"],
                  font=self.font_mid, fill="white",
                  anchor="ma")

        mets = [
            ("wind_speed", f"{today_s['wind']} {unit_w}"),
            ("pressure", f"{today_s['press']} {unit_p}"),
            ("humidity", f"{today_s['hum']}%")
        ]
        ICON = 48
        GAP = 80

        total_w = sum(
            ICON + 10 + draw.textbbox((0, 0), val, font=self.font_small)[2]
            for _, val in mets
        ) + GAP * (len(mets) - 1)
        xm = (W - total_w) / 2
        y3 = y2 + self.font_mid.getbbox(today_s["desc"])[3] + 60

        for key, val in mets:
            ico = Image.open(f"{self.icon_dir}{key}.png") \
                .convert("RGBA") \
                .resize((ICON, ICON), Image.LANCZOS)
            img.paste(ico, (int(xm), int(y3 - ICON / 2)), ico)
            draw.text((xm + ICON + 10, y3), val,
                      font=self.font_small, fill="white",
                      anchor="lm")
            xm += ICON + 10 + draw.textbbox((0, 0), val, font=self.font_small)[2] + GAP

        start_y = bh + 40
        end_y = H - 40
        slot_h = (end_y - start_y) / 5
        x_day = 40
        x_icon = 200
        x_temp = W - 40
        weekdays = self.TRANSLATIONS[self.lang]["weekdays"]

        for i, (day, info) in enumerate(days_s):
            yy = start_y + slot_h / 2 + i * slot_h
            wd_index = datetime.datetime.strptime(day, "%Y-%m-%d").weekday()
            wd = weekdays[wd_index]

            draw.text((x_day, yy), wd,
                      font=self.font_mid, fill="white",
                      anchor="lm")
            ico2 = Image.open(f"{self.icon_dir}{info['icon']}.png") \
                .convert("RGBA") \
                .resize((ICON, ICON), Image.LANCZOS)
            img.paste(ico2, (x_icon, int(yy - ICON / 2)), ico2)

            hl = f"{info['high']}°/{info['low']}°"
            draw.text((x_temp, yy), hl,
                      font=self.font_mid, fill="white",
                      anchor="rm")

        return img
