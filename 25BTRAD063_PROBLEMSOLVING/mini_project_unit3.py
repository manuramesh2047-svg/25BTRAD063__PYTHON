"""
Mini Project (UNIT 3) - Problem Solving Component
Name : Manu R
USN  : 25BTRAD063

Part 1: Attendance Tracker
Part 2: Sales Data Analyzer
Both use lists and dictionaries.
"""

# =====================================================================
# PART 1: ATTENDANCE TRACKER
# =====================================================================
# Data structure: dictionary -> {student_name: [list of "P"/"A" records]}

def add_student(attendance, name):
    """Add a new student with an empty attendance list."""
    if name in attendance:
        print(f"  '{name}' already exists.")
    else:
        attendance[name] = []
        print(f"  Student '{name}' added.")


def mark_attendance(attendance, name, status):
    """Add a new day's attendance ('P' or 'A') for a student."""
    status = status.upper()
    if name not in attendance:
        print(f"  '{name}' not found.")
    elif status not in ("P", "A"):
        print("  Status must be 'P' (Present) or 'A' (Absent).")
    else:
        attendance[name].append(status)
        print(f"  Marked {name} as {status}.")


def update_attendance(attendance, name, day, status):
    """Update an existing day's (1-based) attendance status."""
    status = status.upper()
    if name not in attendance:
        print(f"  '{name}' not found.")
    elif status not in ("P", "A"):
        print("  Status must be 'P' or 'A'.")
    elif not 1 <= day <= len(attendance[name]):
        print(f"  Day {day} is invalid for {name}.")
    else:
        attendance[name][day - 1] = status
        print(f"  Updated {name}, day {day} -> {status}.")


def attendance_percentage(records):
    """Return attendance percentage for a list of 'P'/'A' records."""
    if not records:
        return 0.0
    return records.count("P") / len(records) * 100


def display_attendance(attendance):
    """Display records in an organised table."""
    print("\n  {:<12} {:<22} {:>8}".format("Student", "Record", "Percent"))
    print("  " + "-" * 44)
    for name, records in attendance.items():
        print("  {:<12} {:<22} {:>7.2f}%".format(
            name, " ".join(records) if records else "-",
            attendance_percentage(records)))


def below_threshold(attendance, threshold):
    """Return list of (name, percent) for students below threshold."""
    return [(n, attendance_percentage(r)) for n, r in attendance.items()
            if attendance_percentage(r) < threshold]


def test_attendance():
    print("=" * 50)
    print("PART 1: ATTENDANCE TRACKER")
    print("=" * 50)
    attendance = {}

    # Scenario 1: add students
    print("\n[Scenario 1] Adding students")
    for s in ["Asha", "Bharath", "Chitra", "Dev"]:
        add_student(attendance, s)
    add_student(attendance, "Asha")          # duplicate

    # Scenario 2: mark attendance over 5 days
    print("\n[Scenario 2] Marking attendance for 5 days")
    data = {
        "Asha":    ["P", "P", "P", "P", "P"],   # 100%
        "Bharath": ["P", "A", "P", "A", "P"],   # 60%
        "Chitra":  ["A", "A", "P", "A", "A"],   # 20%
        "Dev":     ["P", "P", "P", "A", "P"],   # 80%
    }
    for name, recs in data.items():
        for r in recs:
            attendance[name].append(r)
    display_attendance(attendance)

    # Scenario 3: update + invalid inputs
    print("\n[Scenario 3] Updating records and invalid inputs")
    update_attendance(attendance, "Chitra", 1, "P")   # A -> P
    update_attendance(attendance, "Chitra", 9, "P")   # bad day
    update_attendance(attendance, "Zed", 1, "P")      # unknown student
    mark_attendance(attendance, "Dev", "X")           # bad status
    display_attendance(attendance)

    # Scenario 4: threshold check
    print("\n[Scenario 4] Students below 75% attendance")
    for name, pct in below_threshold(attendance, 75):
        print(f"  {name}: {pct:.2f}%  <-- SHORTAGE")

    print("\n[Scenario 5] Students below 50% attendance")
    low = below_threshold(attendance, 50)
    if low:
        for name, pct in low:
            print(f"  {name}: {pct:.2f}%")
    else:
        print("  None")

    # Scenario 6: edge case - student with no records
    print("\n[Scenario 6] New student with no records")
    add_student(attendance, "Esha")
    display_attendance(attendance)


# =====================================================================
# PART 2: SALES DATA ANALYZER
# =====================================================================
# Data structure: dictionary -> {product: {"quantity": int, "price": float}}

def add_or_update_product(sales, product, quantity, price):
    """Add a new product, or update quantity/price of an existing one."""
    if quantity < 0 or price < 0:
        print("  Quantity and price cannot be negative.")
        return
    if product in sales:
        sales[product]["quantity"] += quantity   # add to units sold
        sales[product]["price"] = price          # latest price
        print(f"  Updated '{product}': qty={sales[product]['quantity']}, "
              f"price={price}")
    else:
        sales[product] = {"quantity": quantity, "price": price}
        print(f"  Added '{product}': qty={quantity}, price={price}")


def product_revenue(sales):
    """Return dictionary {product: revenue}."""
    return {p: d["quantity"] * d["price"] for p, d in sales.items()}


def total_sales(sales):
    return sum(product_revenue(sales).values())


def highest_selling(sales):
    """Highest-selling product by quantity sold."""
    if not sales:
        return None
    return max(sales, key=lambda p: sales[p]["quantity"])


def top_revenue_product(sales):
    revenue = product_revenue(sales)
    return max(revenue, key=revenue.get) if revenue else None


def summarize(sales):
    """Product-wise performance summary with share of total revenue."""
    revenue = product_revenue(sales)
    total = total_sales(sales)
    print("\n  {:<12} {:>5} {:>8} {:>10} {:>7}".format(
        "Product", "Qty", "Price", "Revenue", "Share"))
    print("  " + "-" * 46)
    # sorted from best to worst revenue (comparison of performance)
    for p in sorted(revenue, key=revenue.get, reverse=True):
        share = revenue[p] / total * 100 if total else 0
        print("  {:<12} {:>5} {:>8.2f} {:>10.2f} {:>6.1f}%".format(
            p, sales[p]["quantity"], sales[p]["price"], revenue[p], share))
    print("  " + "-" * 46)
    print("  {:<12} {:>5} {:>8} {:>10.2f}".format(
        "TOTAL", sum(d["quantity"] for d in sales.values()), "", total))


def test_sales():
    print("\n" + "=" * 50)
    print("PART 2: SALES DATA ANALYZER")
    print("=" * 50)

    # Dataset 1: normal data
    print("\n[Dataset 1] Normal data")
    sales = {}
    for p, q, pr in [("Pen", 120, 10), ("Notebook", 60, 45),
                     ("Bag", 15, 500), ("Marker", 80, 25)]:
        add_or_update_product(sales, p, q, pr)
    summarize(sales)
    print(f"\n  Highest-selling (by quantity): {highest_selling(sales)}")
    print(f"  Highest revenue product      : {top_revenue_product(sales)}")
    print("  Interpretation: Pen sells the most units, but Bag earns the "
          "most revenue because of its high price.")

    # Dataset 2: update + invalid input
    print("\n[Dataset 2] Updating records / invalid input")
    add_or_update_product(sales, "Pen", 30, 12)       # update
    add_or_update_product(sales, "Eraser", -5, 3)     # invalid
    summarize(sales)

    # Dataset 3: one product dominates
    print("\n[Dataset 3] One dominant product")
    s2 = {}
    add_or_update_product(s2, "Laptop", 10, 50000)
    add_or_update_product(s2, "Mouse", 200, 400)
    summarize(s2)
    print(f"\n  Highest-selling (by quantity): {highest_selling(s2)}")
    print(f"  Highest revenue product      : {top_revenue_product(s2)}")
    print("  Interpretation: Mouse sells more units, yet Laptop generates "
          "most of the revenue.")

    # Dataset 4: empty data
    print("\n[Dataset 4] Empty dataset")
    s3 = {}
    print(f"  Total sales: {total_sales(s3)}")
    print(f"  Highest-selling: {highest_selling(s3)}")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    print("Name : Manu R")
    print("USN  : 25BTRAD063\n")
    test_attendance()
    test_sales()
