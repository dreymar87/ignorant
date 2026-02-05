from ignorant.core import *
from ignorant.localuseragent import *


async def tiktok(phone, country_code, email, username, client, out):
    name = "tiktok"
    domain = "tiktok.com"
    method = "register"
    frequent_rate_limit = False

    # Only works with email
    if not email:
        return

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.tiktok.com",
        "Connection": "close",
    }

    try:
        # TikTok password reset endpoint to check if email exists
        reset_url = "https://www.tiktok.com/passport/web/send_code/v2/"

        # Get initial page for cookies/tokens
        init_response = await client.get("https://www.tiktok.com/", headers=headers, follow_redirects=True)

        # Update headers with cookies
        cookies = init_response.cookies

        # Prepare data for email check
        data = {
            "email": email,
            "type": 16,  # Password reset type
            "account": email
        }

        # Make request to check if email exists
        response = await client.post(reset_url, headers=headers, data=data, cookies=cookies, follow_redirects=True)

        if response.status_code == 200:
            try:
                result = response.json()

                # TikTok returns different codes for different scenarios
                # Check the response for account existence
                if result.get("data", {}).get("error_code") == 1009:
                    # Email not registered
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False
                    })
                elif result.get("message") == "success" or result.get("data", {}).get("send_status") == 1:
                    # Email exists and code was sent
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True
                    })
                else:
                    # Try alternative method - signup check
                    signup_url = "https://www.tiktok.com/passport/web/check_email/"
                    signup_data = {
                        "email": email,
                        "scene": 1
                    }

                    signup_response = await client.post(signup_url, headers=headers, data=signup_data, cookies=cookies, follow_redirects=True)

                    if signup_response.status_code == 200:
                        signup_result = signup_response.json()

                        # Check if email is available or taken
                        if signup_result.get("data", {}).get("is_registered") == 1:
                            # Email is registered
                            out.append({
                                "name": name,
                                "domain": domain,
                                "method": method,
                                "frequent_rate_limit": frequent_rate_limit,
                                "rateLimit": False,
                                "exists": True
                            })
                        elif signup_result.get("data", {}).get("is_registered") == 0:
                            # Email not registered
                            out.append({
                                "name": name,
                                "domain": domain,
                                "method": method,
                                "frequent_rate_limit": frequent_rate_limit,
                                "rateLimit": False,
                                "exists": False
                            })
                        else:
                            # Uncertain, mark as rate limit
                            out.append({
                                "name": name,
                                "domain": domain,
                                "method": method,
                                "frequent_rate_limit": frequent_rate_limit,
                                "rateLimit": True,
                                "exists": False
                            })
                    else:
                        # Rate limited or error
                        out.append({
                            "name": name,
                            "domain": domain,
                            "method": method,
                            "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": True,
                            "exists": False
                        })

            except json.JSONDecodeError:
                # JSON parsing error, likely rate limited
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True,
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
            # Other error
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
