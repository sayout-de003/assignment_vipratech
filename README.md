# **VipraTech Django Stripe Shop – Assignment**

This project is a **minimal e-commerce prototype** built using Django, REST Framework, and Stripe Checkout. It demonstrates user authentication, product catalog, order creation, secure payment processing, webhook-based confirmation, and double-payment prevention.

---

## 🚀 **Features**

### 🛍️ Shop & Checkout

* Displays **3 fixed products** (seeded using a management command).
* Users can select quantities and start checkout in a single page.
* Stripe Checkout redirects customers to a **secure hosted payment page**.

### 💳 Stripe Payments

* Stripe Checkout Session integration.
* Webhook listener ensures **reliable post-payment order creation**.
* Full idempotency protection:

  * Stripe session ID is used as the unique order key.
  * Django `transaction.atomic()` prevents race conditions.
  * Buy button is disabled on click to avoid double clicks.

### 👤 Authentication (Optional)

* Signup using Django’s built-in `UserCreationForm`.
* Login/Logout using Django auth.
* Authenticated users can view **their past paid orders**.

### 🔒 Reliability & Safety

* Buy button immediately disables → no double submissions.
* Webhook always returns `200 OK` even after replays.
* Stripe events processed only once using a unique session ID.

### 🎨 Frontend

* Bootstrap 5 UI
* Fully responsive layout
* Inline cart → checkout → payment completion flow


---

## 🧩 **Architecture & Tech Stack**

* **Backend:** Django 5.2+, Django REST Framework
* **Frontend:** Bootstrap 5
* **Database:** PostgreSQL
* **Payments:** Stripe Checkout Session
* **Async:** Django async views with `sync_to_async`
* **Templates:** Django HTML templates
* **Webhooks:** Stripe → `/stripe-webhook/`

---

## 📂 **Directory Structure**

```
assignment_vipratech/
├── manage.py
├── requirements.txt
├── README.md
├── assignment_vipratech/
│   └── urls.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── shop/
│   ├── urls.py
│   ├── views.py
│   ├── models.py
│   ├── serializers.py
│   ├── admin.py
│   ├── templates/
│   │   ├── registration/
│   │   │   └── login.html
│   │   └── shop/
│   │       └── index.html
│   ├── management/
│   │   └── commands/
│   │       └── seed_products.py
│   ├── migrations/
│   └── tests.py
├── static/
├── templates/
│   └── registration/
│       ├── login.html
│       └── signup.html
```

---

## ⚙️ **Setup Instructions**

### **1. Install prerequisites**

* Python 3.11+
* PostgreSQL installed & running
* Stripe test keys

---

### **2. Create virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

### **4. Configure environment variables**

Create `.env` using `.env.example`:

```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
DATABASE_URL=postgres://...
```

---

### **5. Run migrations**

```bash
python manage.py migrate
```

---

### **6. Seed initial products**

```bash
python manage.py seed_products
```

---

### **7. Start Stripe webhook listener**

```bash
stripe listen --forward-to localhost:8000/stripe-webhook/
```

---

### **8. Start the development server**

Run via ASGI (recommended for async):

```bash
uvicorn config.asgi:application --reload
```

Or via Django runserver:

```bash
python manage.py runserver
```

---

### **9. Visit the shop**

➡️ [http://localhost:8000](http://localhost:8000)

---

## 💡 **Chosen Payment Flow**

Using **Stripe Checkout** provides:

* Secure hosted payment page
* No card handling in our backend
* Simple webhook-driven order verification
* Easy prevention of repeated or duplicate charges

Checkout Flow:

1. User selects product quantities.
2. User clicks **Buy**, Stripe Checkout Session is created.
3. User is redirected to Stripe’s secure page.
4. After successful payment:

   * Stripe sends a webhook → backend creates order.
5. Shop homepage displays **paid orders from webhook**.

This avoids race conditions and keeps the app simple and safe.

---

## 🛡️ **Double-Charge Prevention**

The system prevents double charging through:

### ✔ UI-level protection

* Buy button disabled immediately after click.

### ✔ Backend-level protection

* `Order.objects.get_or_create(stripe_session_id=...)`
* Wrapped in a `transaction.atomic()` block.
* Ensures repeated webhooks don’t duplicate orders.

---

## 🧪 Testing Notes

* Stripe webhook events can be replayed safely.
* All success responses are idempotent.
* Orders always reflect database-confirmed payments, not user redirects.

---

## 📧 Contact

If needed as part of the assignment:
**Developer:** Sayantan Dey 
**Email:** desayantan1947@gmail.com
**Tech stack:** Django, REST Framework, Stripe, PostgreSQL, Redis, WebSockets

---

---

## 📄 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for details.


