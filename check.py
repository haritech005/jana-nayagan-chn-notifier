import os
import sys
import json
from datetime import datetime
import requests

API_URL = "https://in.bookmyshow.com/api/movies-data/v4/showtimes-by-event/primary-dynamic"
STATE_FILE = "state.json"
NTFY_TOPIC = "jana-nayagan-chn-z4b7k9"

def send_notification(venue_name):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Title": "Jana Nayagan Theatre Open!",
        "Click": "https://in.bookmyshow.com/movies/chennai/jana-nayagan/ET00430817"
    }
    body = f"New Theatre Added: {venue_name}"
    try:
        resp = requests.post(url, data=body.encode("utf-8"), headers=headers, timeout=10)
        if resp.status_code == 200:
            print(f"Notification sent successfully for {venue_name}")
        else:
            print(f"Failed to send notification for {venue_name}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"Error sending notification for {venue_name}: {e}")


def fetch_and_parse_venues():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://in.bookmyshow.com/movies/chennai/buytickets/ET00430817/",
        "sec-ch-ua": '"Chromium";v="145", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "x-app-code": "WEB",
        "x-region-code": "CHEN",
        "x-region-slug": "chennai",
        "x-geohash": "tf3",
        "x-latitude": "13.056",
        "x-longitude": "80.206",
        "x-location-selection": "manual",
        "x-lsid": "",
    }
    
    params = {
        "eventCode": "ET00430817",
        "dateCode": "",
        "isDesktop": "true",
        "regionCode": "CHEN",
        "xLocationShared": "false",
        "memberId": "",
        "lsId": "",
        "subCode": "",
        "lat": "13.056",
        "lon": "80.206",
    }
    
    venues = {}
    
    try:
        resp = requests.get(API_URL, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"HTTP Error: {resp.status_code}")
            return venues
            
        data = resp.json()
        
        # Check if error metadata exists
        metadata = data.get("metadata", {})
        error = metadata.get("error", {})
        if error:
            error_code = error.get("errorCode")
            error_msg = error.get("message", "Unknown error")
            print(f"BMS API Info: {error_msg} (Code: {error_code})")
            # Usually errorCode "1a.1b.2001" means "There are no shows available in this region."
            return venues
            
        # Parse showtime widgets if available
        widgets = data.get("data", {}).get("showtimeWidgets", [])
        for w in widgets:
            if w.get("type") == "groupList":
                for g in w.get("data", []):
                    if g.get("type") == "venueGroup":
                        for card in g.get("data", []):
                            if card.get("type") == "venue-card":
                                addl = card.get("additionalData", {})
                                code = addl.get("venueCode")
                                name = addl.get("venueName")
                                if code and name:
                                    venues[code.strip()] = name.strip()
                                    
    except Exception as e:
        print(f"Error fetching/parsing BMS API: {e}")
        
    return venues

def main():
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] Running check.py")
        
        # 1. Fetch current venues
        current_venues = fetch_and_parse_venues()
        print(f"Found {len(current_venues)} active venue(s).")
        if current_venues:
            for code, name in current_venues.items():
                print(f"  - {code}: {name}")
                
        # 2. Load previous state
        old_state = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    old_state = json.load(f)
            except Exception as e:
                print(f"Warning: Could not parse state.json ({e}). Starting fresh.")
                
        # 3. Detect changes
        new_venue_codes = set(current_venues.keys()) - set(old_state.keys())
        new_venues = {code: current_venues[code] for code in new_venue_codes}
        
        # Print new venues and send notifications
        print(f"Detected {len(new_venues)} new venue(s):")
        for code, name in new_venues.items():
            print(f"  * NEW * {code}: {name}")
            send_notification(name)
            
        # 4. Save state if changed
        if current_venues != old_state:
            try:
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(current_venues, f, indent=2, ensure_ascii=False)
                print("state.json updated.")
            except Exception as e:
                print(f"Error saving state.json: {e}")
        else:
            print("No changes in venue list. state.json remains the same.")
            
    except Exception as e:
        print(f"Unhandled error in main execution: {e}")
        # Always exit 0 to avoid breaking GitHub Actions workflow runs
        sys.exit(0)

if __name__ == "__main__":
    main()
