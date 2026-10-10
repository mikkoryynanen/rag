"""Generate fake but realistic B2B invoices as PDF files, to use as a test corpus.

    uv run tests/generate_invoices.py              # one invoice
    uv run tests/generate_invoices.py --count 200  # as many as you like

Every company is invented. Invoice N is identical for a given --seed whatever --count is,
so generating more later never changes the ones you already have.
"""
import argparse
import random
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from itertools import cycle
from pathlib import Path
from textwrap import wrap

from fpdf import FPDF

BASE_DATE = date(2026, 9, 30)  # invoices are dated in the 18 months before this; fixed so runs are reproducible
LEFT, BLACK, GREY = 18, (20, 20, 20), (110, 110, 110)  # page margin in mm, text colours
MONTHS = "January February March April May June July August September October November December".split()

# VAT rates are the standard rates in force over the whole date range above.
# banks: (name, BIC, start of the national account number, random digits to append)
COUNTRIES = {
    "FI": dict(
        name="Finland", vat=Decimal("25.5"), number="{y}{n:05d}",
        date=lambda d: f"{d.day}.{d.month}.{d.year}",
        banks=[("Nordea Bank Abp", "NDEAFIHH", "1", 13), ("OP Corporate Bank plc", "OKOYFIHH", "5", 13)],
        people=["Mikael Lahtinen", "Sanna Korhonen", "Jukka Nieminen", "Elina Heikkinen", "Antti Mäkelä", "Laura Virtanen"],
        note="Complaints must be made within 8 days. Penalty interest on late payments in accordance with the Finnish Interest Act.",
    ),
    "DE": dict(
        name="Germany", vat=Decimal("19"), number="RE-{y}-{n:05d}",
        date=lambda d: f"{d:%d.%m.%Y}",
        banks=[("Commerzbank AG", "COBADEFFXXX", "50040000", 10), ("Deutsche Bank AG", "DEUTDEFFXXX", "50070010", 10)],
        people=["Anna Becker", "Stefan Hoffmann", "Julia Schäfer", "Markus Vogel", "Katrin Neumann", "Tobias Krüger"],
        note="Payable without deduction unless a cash discount is stated above. Goods remain our property until paid in full.",
    ),
    "NL": dict(
        name="Netherlands", vat=Decimal("21"), number="F{y}-{n:05d}",
        date=lambda d: f"{d:%d-%m-%Y}",
        banks=[("ING Bank N.V.", "INGBNL2A", "INGB0", 9), ("Coöperatieve Rabobank U.A.", "RABONL2U", "RABO0", 9)],
        people=["Sanne de Vries", "Daan Bakker", "Lotte Visser", "Ruben Smit", "Femke Mulder", "Bram van Dijk"],
        note="Our general terms and conditions apply to all deliveries and services. Statutory commercial interest is charged on late payments.",
    ),
    "IE": dict(
        name="Ireland", vat=Decimal("23"), number="INV-{y}{n:04d}",
        date=lambda d: f"{d:%d/%m/%Y}",
        banks=[("Allied Irish Banks, p.l.c.", "AIBKIE2D", "AIBK93", 12), ("Bank of Ireland", "BOFIIE2D", "BOFI90", 12)],
        people=["Aoife Byrne", "Conor Nolan", "Niamh Kavanagh", "Declan Walsh", "Siobhán Doyle", "Eoin Gallagher"],
        note="Late payment interest may be charged under the European Communities (Late Payment in Commercial Transactions) Regulations 2012.",
    ),
}

# (name, country, industry, address lines, city)
COMPANIES = [
    ("Nordlake Systems Oy", "FI", "software", ["Hämeentie 31", "00500 Helsinki"], "Helsinki"),
    ("Tammerkosken Teollisuustarvike Oy", "FI", "industrial", ["Hatanpään valtatie 24", "33100 Tampere"], "Tampere"),
    ("Pohjanrahti Logistics Oy", "FI", "freight", ["Poikkimaantie 14", "90400 Oulu"], "Oulu"),
    ("Isarwerk Antriebstechnik GmbH", "DE", "industrial", ["Schleißheimer Str. 141", "80797 München"], "München"),
    ("Kontor Elbe Spedition GmbH", "DE", "freight", ["Große Elbstraße 45", "22767 Hamburg"], "Hamburg"),
    ("Lichtblau Kreativagentur GmbH", "DE", "marketing", ["Torstraße 89", "10119 Berlin"], "Berlin"),
    ("Vossenberg Software B.V.", "NL", "software", ["Oudegracht 187", "3511 NE Utrecht"], "Utrecht"),
    ("Maasdijk Facility Services B.V.", "NL", "facility", ["Weena 505", "3013 AL Rotterdam"], "Rotterdam"),
    ("Grachtenhuis Studio B.V.", "NL", "marketing", ["Herengracht 282", "1016 BX Amsterdam"], "Amsterdam"),
    ("Liffey Quay Consulting Limited", "IE", "software", ["24 Baggot Street Lower", "Dublin 2", "D02 XK58"], "Dublin"),
    ("Corrib Office Care Limited", "IE", "facility", ["Unit 6, Liosbán Business Park", "Tuam Road", "Galway", "H91 TN4P"], "Galway"),
    ("Lee Valley Fasteners Limited", "IE", "industrial", ["Unit 12, Marina Commercial Park", "Centre Park Road", "Cork", "T12 R6FW"], "Cork"),
]

# industry: (sells goods, only sells within its own country, catalog)
# catalog rows: (description, unit, lowest price, highest price, lowest qty, highest qty, qty step)
INDUSTRIES = {
    "software": (False, False, [
        ("Software development, backend services, {period}", "h", 105, 135, 40, 160, 0.5),
        ("Software development, web frontend, {period}", "h", 95, 125, 20, 120, 0.5),
        ("Solution architecture consulting", "h", 140, 175, 4, 24, 0.5),
        ("Cloud hosting and monitoring, {period}", "month", 480, 1900, 1, 1, 1),
        ("Support and maintenance agreement, {period}", "month", 650, 2400, 1, 1, 1),
        ("Security audit, web application, fixed price", "pcs", 3800, 7200, 1, 1, 1),
        ("Travel expenses, on-site workshop", "pcs", 180, 640, 1, 1, 1),
    ]),
    "industrial": (True, False, [
        ("Hex bolt M10x40, DIN 933, zinc plated, box of 200", "box", 18, 26, 5, 40, 1),
        ("Hex nut M10, DIN 934, zinc plated, box of 500", "box", 14, 21, 2, 20, 1),
        ("Deep groove ball bearing 6204-2RS", "pcs", 3.2, 5.9, 20, 200, 10),
        ("Hydraulic hose assembly DN12 2SN, 3 m, fittings pressed", "pcs", 38, 61, 2, 24, 1),
        ("V-belt SPA 1250", "pcs", 9.5, 14.8, 4, 30, 1),
        ("Cutting disc 125 x 1.0 mm, inox, pack of 25", "pack", 21, 34, 2, 15, 1),
        ("Work gloves, nitrile coated, size 9, pack of 12 pairs", "pack", 16, 27, 2, 20, 1),
        ("Freight and packaging", "pcs", 24, 95, 1, 1, 1),
    ]),
    "freight": (False, False, [
        ("Road freight {from}-{to}, {pallets} EUR pallets, {kg} kg", "pcs", 420, 1650, 1, 1, 1),
        ("Full truckload {from}-{to}, 13.6 m curtain-sider", "pcs", 1900, 3400, 1, 1, 1),
        ("Fuel surcharge", "pcs", 35, 190, 1, 1, 1),
        ("Pallet storage, per pallet per week", "pcs", 4.5, 7.5, 10, 120, 1),
        ("Export customs declaration", "pcs", 45, 75, 1, 3, 1),
        ("Tail-lift delivery surcharge", "pcs", 35, 60, 1, 2, 1),
    ]),
    "facility": (False, True, [  # cleaning is taxed where the building is, so these stay domestic
        ("Office cleaning, 5 days per week, {period}", "month", 890, 2600, 1, 1, 1),
        ("Window cleaning, interior and exterior", "pcs", 240, 680, 1, 1, 1),
        ("Floor waxing and deep cleaning", "m²", 3.2, 5.5, 80, 600, 10),
        ("Washroom hygiene supplies, {period}", "month", 85, 240, 1, 1, 1),
        ("Waste collection, mixed waste, 660 l container", "pcs", 14, 22, 4, 9, 1),
        ("Additional cleaning hours on request", "h", 32, 44, 2, 16, 0.5),
    ]),
    "marketing": (False, False, [
        ("Brand identity refresh, phase {phase}: concept and design", "pcs", 4200, 9800, 1, 1, 1),
        ("Social media campaign management, {period}", "month", 1200, 3200, 1, 1, 1),
        ("Product photography, half-day studio shoot", "pcs", 780, 1350, 1, 3, 1),
        ("Copywriting, website landing pages", "page", 180, 320, 3, 10, 1),
        ("Paid search advertising management fee, {period}", "month", 600, 1500, 1, 1, 1),
        ("Graphic design, trade fair materials", "h", 85, 110, 6, 40, 0.5),
        ("Stock image licences", "pcs", 29, 79, 2, 12, 1),
    ]),
}

TERMS = [
    (14, "14 days net"),
    (21, "21 days net"),
    (30, "30 days net"),
    (30, "30 days net, 2% cash discount if paid within 10 days"),
]


def money(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def price(rng, lo, hi):
    """A price in [lo, hi] on the grid such prices use: cents for small items, round figures for rates and fees."""
    step = Decimal("0.01") if hi < 100 else 5 if hi < 1000 else 50
    return money(round(Decimal(str(rng.uniform(lo, hi))) / step) * step)


def iban(cc, bban):
    as_number = lambda s: int("".join(str(int(ch, 36)) for ch in s))  # A=10 ... Z=35
    code = f"{cc}{98 - as_number(bban + cc + '00') % 97:02d}{bban}"
    assert as_number(code[4:] + code[:4]) % 97 == 1, code
    return " ".join(wrap(code, 4))


def fi_reference(base):
    """Finnish payment reference: base digits plus a 7-3-1 weighted check digit, grouped in fives from the right."""
    total = sum(int(d) * w for d, w in zip(reversed(base), cycle((7, 3, 1))))
    return " ".join(wrap((base + str(-total % 10))[::-1], 5))[::-1]


def details(company):
    """Registration and bank details for a company, the same on every invoice it appears on."""
    name, cc, _, address, city = company
    rng = random.Random(name)
    digits = lambda n: str(rng.randint(10 ** (n - 1), 10 ** n - 1))
    country = COUNTRIES[cc]
    bank, bic, prefix, n = rng.choice(country["banks"])
    people = rng.sample(country["people"], 2)
    # shortcut: tax IDs have the right format but not valid check digits, add them if a validator ever reads these
    if cc == "FI":
        business_id = f"{digits(7)}-{digits(1)}"
        vat_id, register = "FI" + business_id.replace("-", ""), f"Business ID {business_id} · Registered office: {city}"
    elif cc == "DE":
        vat_id, register = "DE" + digits(9), f"Managing director: {people[1]} · Commercial register: Amtsgericht {city}, HRB {digits(6)}"
    elif cc == "NL":
        vat_id, register = f"NL{digits(9)}B01", f"Chamber of Commerce (KvK) no. {digits(8)}"
    else:
        vat_id, register = f"IE{digits(7)}{rng.choice('ABDFHLNPTW')}", f"Registered in Ireland no. {digits(6)} · Directors: {people[0]}, {people[1]}"
    return dict(
        name=name, cc=cc, city=city, address=address + [country["name"]], vat_id=vat_id, register=register,
        contact=people[0], bank=bank, bic=bic, iban=iban(cc, prefix + digits(n)),
        per_day=rng.randint(3, 25),  # invoices this company issues on a typical day
    )


def make_invoice(seed, index, attempt=0):
    """Return (invoice number, PDF bytes). A higher attempt gives a different invoice for the same index."""
    rng = random.Random(f"{seed}-{index}-{attempt}")
    seller = rng.choice(COMPANIES)
    goods, local_only, catalog = INDUSTRIES[seller[2]]
    buyer = rng.choice([
        c for c in COMPANIES
        if c is not seller and (c[1] == seller[1] or not local_only)
        and not (goods and c[2] in ("software", "marketing"))  # offices don't order bolts and bearings
    ])
    s, b = details(seller), details(buyer)
    country = COUNTRIES[s["cc"]]
    fmt = country["date"]

    issued = BASE_DATE - timedelta(days=rng.randrange(540))
    days, terms = rng.choice(TERMS)
    last_month = issued.replace(day=1) - timedelta(days=1)
    # numbers restart each January and rise through the year, so a later invoice never has a lower number
    seq = 100 + (issued - date(issued.year, 1, 1)).days * s["per_day"] + rng.randrange(s["per_day"])
    customer_no = random.Random(s["name"] + b["name"]).randint(10010, 48999)  # one number per customer
    number = country["number"].format(y=issued.year, n=seq)
    reference = fi_reference(f"{customer_no}{seq:05d}") if s["cc"] == "FI" else number

    fill = {
        "period": f"{MONTHS[last_month.month - 1]} {last_month.year}", "from": s["city"], "to": b["city"],
        "pallets": rng.randint(2, 12), "kg": rng.randrange(400, 6200, 50), "phase": rng.randint(1, 3),
    }
    lines = []
    for i in sorted(rng.sample(range(len(catalog)), rng.randint(1, min(5, len(catalog))))):
        desc, unit, lo, hi, qlo, qhi, step = catalog[i]
        qty = Decimal(str(qlo + step * rng.randint(0, int((qhi - qlo) / step))))
        unit_price = price(rng, lo, hi)
        lines.append((desc.format(**fill), qty, unit, unit_price, money(qty * unit_price)))

    domestic = s["cc"] == b["cc"]
    rate = country["vat"] if domestic else Decimal(0)
    net = sum((line[4] for line in lines), Decimal(0))
    vat = money(net * rate / 100)
    if domestic:
        vat_label, vat_note = f"VAT {rate}% on {net:,.2f}", ""
    elif goods:
        vat_label, vat_note = "VAT 0%", "VAT-exempt intra-Community supply of goods, Article 138 of Council Directive 2006/112/EC."
    else:
        vat_label, vat_note = "VAT 0%", "Reverse charge: VAT to be accounted for by the recipient, Article 196 of Council Directive 2006/112/EC."

    meta = [
        ("Invoice number", number),
        ("Invoice date", fmt(issued)),
        ("Due date", fmt(issued + timedelta(days=days))),
        ("Payment terms", terms),
        ("Customer number", str(customer_no)),
        ("Your reference", f"PO 4500{rng.randint(100000, 999999)} / {b['contact']}"),
        ("Our reference", s["contact"]),
    ]
    if goods:
        meta += [("Delivery date", fmt(issued - timedelta(days=rng.randint(1, 6)))), ("Delivery terms", f"DAP {b['city']} (Incoterms 2020)")]
    else:
        meta += [("Service period", fill["period"])]

    pdf = FPDF(format="A4")
    pdf.set_margins(LEFT, 16, LEFT)
    pdf.set_auto_page_break(False)
    pdf.add_page()
    pdf.set_title(f"Invoice {number}")
    pdf.set_author(s["name"])
    # dated like a real export, and fixed so a rerun writes byte-identical files
    pdf.set_creation_date(datetime(issued.year, issued.month, issued.day, 9, tzinfo=timezone.utc))

    def text(x, y, value, size=9, style="", grey=False, w=0, align="L"):
        """Write wrapped text at (x, y) and return the y just below it. w=0 runs to the right margin."""
        pdf.set_font("Helvetica", style, size)
        pdf.set_text_color(*(GREY if grey else BLACK))
        pdf.set_xy(x, y)
        pdf.multi_cell(w, size * 0.5, value, align=align, new_x="LMARGIN", new_y="NEXT")
        return pdf.get_y()

    text(LEFT, 16, "INVOICE", 20, "B", align="R")
    y = text(LEFT, 16, s["name"], 13, "B", w=110)
    y = text(LEFT, y + 1, "\n".join([*s["address"], f"VAT ID: {s['vat_id']}"]))

    top = y + 12
    text(LEFT, top, "BILL TO", 7, grey=True)
    y_left = text(LEFT, top + 4, b["name"], 10, "B", w=80)
    y_left = text(LEFT, y_left + 0.5, "\n".join([*b["address"], f"VAT ID: {b['vat_id']}"]), w=80)
    y = top
    for key, value in meta:
        text(108, y, key, grey=True, w=30)
        y = text(138, y, value, w=54) + 1

    pdf.set_xy(LEFT, max(y, y_left) + 8)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*BLACK)
    pdf.set_draw_color(*GREY)
    rows = [("#", "Description", "Qty", "Unit", "Unit price", "VAT %", "Net (EUR)")] + [
        (str(n), desc, f"{qty.normalize():f}", unit, f"{unit_price:,.2f}", str(rate), f"{amount:,.2f}")
        for n, (desc, qty, unit, unit_price, amount) in enumerate(lines, 1)
    ]
    with pdf.table(
        col_widths=(8, 76, 14, 14, 24, 14, 24), line_height=6, borders_layout="HORIZONTAL_LINES",
        text_align=("RIGHT", "LEFT", "RIGHT", "LEFT", "RIGHT", "RIGHT", "RIGHT"),
    ) as table:
        for row in rows:
            table.row(row)

    y = pdf.get_y() + 4
    for label, amount, style in [("Subtotal (net)", net, ""), (vat_label, vat, ""), ("Total due (EUR)", net + vat, "B")]:
        text(102, y, label, style=style, w=60, align="R")
        y = text(162, y, f"{amount:,.2f}", style=style, w=30, align="R") + 1.5
    if vat_note:
        y = text(LEFT, y + 3, vat_note)

    y = text(LEFT, y + 8, "Payment details", 10, "B") + 1
    for key, value in [("Beneficiary", s["name"]), ("Bank", s["bank"]), ("IBAN", s["iban"]), ("BIC", s["bic"]), ("Payment reference", reference)]:
        text(LEFT, y, key, grey=True, w=34)
        y = text(LEFT + 34, y, value) + 1
    text(LEFT, y + 5, "Please quote the payment reference with your payment. " + country["note"], 8, grey=True)

    pdf.line(LEFT, 277, 210 - LEFT, 277)
    text(LEFT, 279, f"{s['name']} · {', '.join(s['address'])} · {s['register']} · VAT ID {s['vat_id']}", 7, grey=True, align="C")
    return number, bytes(pdf.output())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, default=1, help="how many invoices to generate (default 1)")
    parser.add_argument("--seed", type=int, default=0, help="change to get a different set (default 0)")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent.parent / "data" / "invoices", help="output directory")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    numbers = set()
    for index in range(1, args.count + 1):
        attempt = 0
        while (invoice := make_invoice(args.seed, index, attempt))[0] in numbers:  # no two invoices share a number
            attempt += 1
        numbers.add(invoice[0])
        (args.out / f"invoice-{index:04d}.pdf").write_bytes(invoice[1])
    print(f"Wrote {args.count} invoice(s) to {args.out}")
