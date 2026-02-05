from ignorant.core import *
from ignorant.localuseragent import *


async def github(phone, country_code, email, username, client, out):
    name = "github"
    domain = "github.com"
    method = "profile"
    frequent_rate_limit = False

    # Only works with username
    if not username:
        return

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "close",
    }

    try:
        # GitHub API to check user existence
        url = f"https://api.github.com/users/{username}"

        response = await client.get(url, headers=headers, follow_redirects=True)

        if response.status_code == 200:
            # User exists
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True
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
        elif response.status_code == 403 or response.status_code == 429:
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
            # Unknown response
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
