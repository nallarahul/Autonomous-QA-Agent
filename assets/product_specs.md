# Product Specifications: E-Shop Checkout

## 1. Discount Codes
* **Code:** `SAVE15`
* **Effect:** Applies a 15% discount to the total cart value (including shipping).
* **Validity:** Can be applied only once per session.
* **Invalid Codes:** Any other code should display an "Invalid Code" error message.

## 2. Shipping Policies
* **Standard Shipping:**
    * Cost: $0.00 (Free)
    * Delivery: 5-7 business days.
* **Express Shipping:**
    * Cost: $10.00 flat rate.
    * Delivery: 1-2 business days.
* **Calculation:** Shipping cost is added to the subtotal before discount application.

## 3. Cart Limits
* Minimum order value: None.
* Maximum items per cart: No limit enforced in this version.