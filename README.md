# Jana Nayagan (Chennai) BookMyShow Theater-Open Notifier

This repository monitors BookMyShow for **Jana Nayagan** showtimes in **Chennai** and sends immediate push notifications as soon as any new theater opens for booking.

It runs entirely on a free-tier setup using GitHub Actions (monitoring every 5 minutes) and **ntfy.sh** for instant push notifications.

---

## Getting Notifications

To receive push alerts on your phone or browser when a new theater opens:
1. **Download** the **ntfy** app on your phone (available on Google Play and Apple App Store), or open the web client.
2. **Subscribe** to the unique, unguessable topic name: **`jana-nayagan-chn-z4b7k9`**
3. Subscription Link: [https://ntfy.sh/jana-nayagan-chn-z4b7k9](https://ntfy.sh/jana-nayagan-chn-z4b7k9)

---

## How It Works

* **Target Movie**: Jana Nayagan (Chennai region, Event Code: `ET00430817`).
* **Check Interval**: Runs every 5 minutes via GitHub Actions.
* **Auto-Stop**: The script compares today's date (in Indian Standard Time / IST) against the movie's release date **2026-07-23**. Once this date passes, the check immediately skips to save GitHub Action workflow minutes.
* **State Persistence**: The script stores previously seen venues in `state.json` inside the repository. If changes are detected, GitHub Actions commits the updated `state.json` file back to the repository and dispatches a push notification.

---

## Manual Execution

You can trigger a manual check at any time:
1. Go to the **Actions** tab of this repository on GitHub.
2. Select **BookMyShow Theater Watcher** from the left sidebar.
3. Click the **Run workflow** dropdown on the right side of the screen.
4. Click the green **Run workflow** button.

---

## How to Disable the Notifier

If you want to stop the notifier before the release date:
1. Go to **Settings** -> **Actions** -> **General** on your repository.
2. Under **Actions permissions**, select **Disable actions** and save.
3. *Alternatively*, navigate to the **Actions** tab, click **BookMyShow Theater Watcher**, click the `...` menu on the right, and select **Disable workflow**.

---

## Known Dependency & Risk: Cloudflare Bot-Protection

BookMyShow uses **Cloudflare WAF** to protect its endpoints. Standard HTTP client libraries (like Python `requests`) are blocked with an HTTP `403 Forbidden` when executing from cloud datacenter IP ranges (such as GitHub Actions runners).

* **Our Bypass**: This codebase uses **`cloudscraper`** to automatically bypass Cloudflare's JS challenges and WAF protections.
* **Future Risks**: If BookMyShow updates its security policies or upgrades its Cloudflare settings (such as forcing mandatory interactive Turnstile Captchas), `cloudscraper` might fail in the future. If that happens:
  1. The GitHub Actions job will fail gracefully (exiting with code `0` to keep the logs clean but sending no notification).
  2. You will see `HTTP Error: 403` with a Cloudflare "Attention Required" message in the workflow logs.
  3. Bypassing it would then require setting up a residential proxy or migrating to a headless browser framework (like Playwright stealth).
