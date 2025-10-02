import os, json, stripe
from flask import Flask, request, jsonify
from utils.storage import upsert_subscription_record

app = Flask(__name__)

SECRET = os.environ.get("STRIPE_SECRET","")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET","")
if not SECRET:
    try:
        import streamlit as st
        SECRET = st.secrets.get("stripe", {}).get("secret_key","")
        WEBHOOK_SECRET = st.secrets.get("stripe", {}).get("webhook_secret","")
    except Exception:
        pass
stripe.api_key = SECRET

@app.post("/stripe/webhook")
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    et = event["type"]
    obj = event["data"]["object"]

    if et == "checkout.session.completed":
        user = (obj.get("metadata") or {}).get("user") or "訪客"
        plan = (obj.get("metadata") or {}).get("plan") or "Pro"
        customer = obj.get("customer") or ""
        subscription = obj.get("subscription") or ""
        status = "active"
        cpe = ""
        try:
            if subscription:
                sub = stripe.Subscription.retrieve(subscription)
                status = sub.get("status", status)
                cpe = sub.get("current_period_end", "")
        except Exception:
            pass
        upsert_subscription_record(user, plan, customer, subscription, cpe, status)

    elif et in ("customer.subscription.updated","customer.subscription.deleted"):
        sub = obj
        customer = sub.get("customer") or ""
        subscription = sub.get("id") or ""
        status = sub.get("status") or "canceled"
        cpe = sub.get("current_period_end", "")
        # TODO: 如需 user <-> customer 對應，可在此更新

    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
