# Rio's Cafe — the sheet to send them

Send this AFTER they've bought their domain. Swap `rioscafe.co.uk` for whatever
they actually bought. Everything else is already filled in and correct.

---

**Subject:** Setting up rioscafe.co.uk — 5 things to copy and paste

Hi Rio's team,

Great news on getting rioscafe.co.uk. Here's how to point it at your new
website. It's five entries to copy and paste, about five minutes. You do it in
your own account, so nobody else ever needs your password.

**Step 1.** Log in to wherever you bought rioscafe.co.uk.

**Step 2.** Find the DNS settings. It's usually a button called **DNS**,
**Manage DNS**, or **DNS Records**.

**Step 3.** Add these five records. There will be an **Add record** button.
Copy and paste each one exactly.

Record 1
```
Type:  A
Name:  @
Value: 185.199.108.153
```

Record 2
```
Type:  A
Name:  @
Value: 185.199.109.153
```

Record 3
```
Type:  A
Name:  @
Value: 185.199.110.153
```

Record 4
```
Type:  A
Name:  @
Value: 185.199.111.153
```

Record 5
```
Type:  CNAME
Name:  www
Value: ejpc.github.io
```

Leave TTL on **Automatic**. If it asks about a proxy or shows an orange cloud,
set it to **DNS only**.

**Step 4.** Save, then send me a message saying it's done.

I'll do the rest and message you the moment the site is live at
rioscafe.co.uk — usually the same day.

---

**Three things that are completely normal, so please don't worry:**

- The address might not work straight away. It can take a few minutes to a few
  hours to spread around the internet.
- If it briefly says "not secure", that's just the padlock still being made.
- **Please only ADD these records, never delete anything that's already there.**
  If you have email on this address, deleting an existing record could stop your
  email working. Adding these five won't affect it at all.

If anything looks different to the above, take a screenshot of the page and send
it to me — I'll tell you exactly what to tap.

Thanks,
Wilf Cartwright

---

## After they reply (your side)

1. Check it actually worked before touching GitHub:
   ```
   dig +short @1.1.1.1 rioscafe.co.uk        # expect the four 185.199.x.x
   dig +short @1.1.1.1 www.rioscafe.co.uk    # expect ejpc.github.io
   ```
2. Repoint the site's SEO tags:
   ```
   cd rios-cafe && python3 set-domain.py rioscafe.co.uk
   git add -A && git commit -m "Move to rioscafe.co.uk" && git push
   ```
3. GitHub → repo → Settings → Pages → Custom domain → `rioscafe.co.uk` → Save.
   Wait for the green tick.
4. Tick **Enforce HTTPS** once it stops being greyed out.
5. Regenerate `qr-code.png` / `qr-code.svg` for `https://rioscafe.co.uk`.
6. Retire the old address, POINTER FIRST: remove the old custom domain in
   GitHub, then delete the `rioscafe` record in Cloudflare.
7. Tell them it's live, and send the QR code.
