# Mini Project: Bill Generator
print("===== BILL GENERATOR =====")
item1 = input("Enter item 1: ")
price1 = float(input("Enter price: "))
item2 = input("Enter item 2: ")
price2 = float(input("Enter price: "))
item3 = input("Enter item 3: ")
price3 = float(input("Enter price: "))
total = price1 + price2 + price3
gst = total * 0.05
grand_total = total + gst
print("\n===== BILL =====")
print(item1, ":", price1)
print(item2, ":", price2)
print(item3, ":", price3)
print("--------------------")
print("Subtotal :", total)
print("GST (5%) :", gst)
print("Total Bill :", grand_total)
print("====================")
