from ignorant.core import *
from ignorant.localuseragent import *


async def reddit(phone, country_code, email, username, client, out):
    name = "reddit"
    domain = "reddit.com"
    method = "profile"
    frequent_rate_limit = False

    # Only works with username
    if not username:
        return

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "close",
    }

    try:
        # Reddit profile page check
        url = f"https://www.reddit.com/user/{username}/about.json"

        response = await client.get(url, headers=headers, follow_redirects=True)

        if response.status_code == 200:
            try:
                data = response.json()
                # Check if user data exists
                if "data" in data and data["data"]:
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True
                    })
                else:
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False
                    })
            except json.JSONDecodeError:
                # Not a valid JSON response, likely doesn't exist
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False
                })

        elif response.status_code == 404:
            # User doesn't exist
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False
            })
        elif response.status_code == 429:
            # Rate limited
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
        else:
            # Unknown response, mark as rate limited
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })

    except Exception as e:
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False,
            "error": str(type(e).__name__)
        })
