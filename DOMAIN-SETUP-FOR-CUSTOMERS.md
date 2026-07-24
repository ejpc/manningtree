# Pointing a customer's domain at their site

For when the customer buys their own web address and you need it to point at the
site you built — **without ever touching their account or asking for a password.**

Works for any registrar (GoDaddy, Namecheap, 123-Reg, IONOS, Cloudflare...).

---

## The order things happen

| # | Who | What |
|---|---|---|
| 1 | Customer | Buys the domain in their own name |
| 2 | You | Send them the record sheet (below) |
| 3 | Customer | Adds the records, tells you it's done |
| 4 | You | Check it worked — `dig +short @1.1.1.1 theirdomain.co.uk` |
| 5 | You | GitHub → Settings → Pages → Custom domain → save → wait for green tick |
| 6 | You | Tick Enforce HTTPS once the certificate issues |
| 7 | You | Regenerate their QR code for the new address |
| 8 | You | Send the "you're live" email |

**Never do 5 before 4 works.** GitHub checks DNS itself and will just refuse.

---

## The records (GitHub Pages)

| Address | Record type | Name / Host | Value |
|---|---|---|---|
| Apex, e.g. `rioscafe.co.uk` | **A** ×4 | `@` | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| With www | **CNAME** | `www` | `ejpc.github.io` |

An apex domain can't be a CNAME — that's why it needs four A records. A
subdomain (`shop.theirdomain.co.uk`) is a single CNAME instead.

If their DNS is on Cloudflare, the proxy must be **DNS only / grey cloud**, or
GitHub can't issue the HTTPS certificate.

---

## THE SHEET — copy this into an email

> Hi [name],
>
> Now that you own [domain], here's how to point it at your new website. It's
> five short entries and takes about five minutes. You do this yourself, so
> nobody else ever needs your login.
>
> **1.** Log in to wherever you bought the domain.
>
> **2.** Find the DNS settings. It's usually called **DNS**, **Manage DNS** or
> **DNS Records**, often under "My Domains".
>
> **3.** Add these five records. There'll be an "Add record" button.
>
> Four of type **A**, with the Name/Host set to **@** :
>
> | Type | Name / Host | Points to |
> |---|---|---|
> | A | @ | 185.199.108.153 |
> | A | @ | 185.199.109.153 |
> | A | @ | 185.199.110.153 |
> | A | @ | 185.199.111.153 |
>
> One of type **CNAME** :
>
> | Type | Name / Host | Points to |
> |---|---|---|
> | CNAME | www | ejpc.github.io |
>
> Leave TTL on Automatic or Default. If it asks about a proxy or an orange
> cloud, choose **DNS only**.
>
> **4.** Save, and send me a quick message.
>
> I'll take it from there — it takes a little while to spread across the
> internet, then I'll switch the site over and turn on the padlock (the secure
> https bit). I'll message you the moment it's live.
>
> A few things that are completely normal, so don't worry:
> - The address might not work straight away. It can take a few minutes to a
>   few hours to spread.
> - If it briefly says "not secure", that's the padlock still being made.
> - If you already have email on this domain, **don't delete anything** — we're
>   only adding. Your email won't be affected by these records.
>
> Any bother at all, send me a screenshot of the DNS page and I'll tell you
> exactly what to click.
>
> Thanks,
> Wilf

---

## Where the DNS settings hide

| Registrar | Path |
|---|---|
| GoDaddy | My Products → Domain → DNS → Manage Zones |
| Namecheap | Domain List → Manage → Advanced DNS |
| 123-Reg | Control Panel → Manage Domain → Manage DNS |
| IONOS | Domains & SSL → the domain → DNS |
| Cloudflare | Pick the domain → DNS → Records |
| Squarespace (ex-Google Domains) | Domains → the domain → DNS |

---

## Checking their work

```
dig +short @1.1.1.1 theirdomain.co.uk          # expect the four 185.199.x.x
dig +short @1.1.1.1 www.theirdomain.co.uk      # expect ejpc.github.io
```

Nothing back? Either it hasn't spread yet, or they saved it wrong. Ask for a
screenshot before assuming.

## Common mistakes they'll make

| What they did | Symptom | Fix |
|---|---|---|
| Typed the full domain in Name instead of `@` | Record shows as `rioscafe.co.uk.rioscafe.co.uk` | Change Name to `@` |
| Made the apex a CNAME | Registrar refuses, or email breaks | Use the four A records |
| Left Cloudflare proxy orange | Site loads but padlock never arrives | Set to DNS only |
| Deleted their existing records to "tidy up" | **Their email stops working** | Warn them in advance. Only ADD |
| Added the records at the wrong provider | Nothing ever resolves | Check `dig NS theirdomain.co.uk` for who really runs their DNS |

---

## Rules

- **Never ask for their password.** Never accept it if offered. A professional
  doesn't need it, and asking is what a scammer does.
- If they want you to do it, ask them to invite you as a **delegated user**
  (Cloudflare Members, GoDaddy Delegate Access) so it's under your own login
  and they can revoke it whenever they like.
- Only ever ADD records. If you're unsure what an existing record does, leave
  it — an MX record you delete is their email gone.
- Screenshot their DNS page before any change, so there's a record of what it
  looked like.
