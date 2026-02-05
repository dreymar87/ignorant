from ignorant.core import *
from ignorant.localuseragent import *


async def facebook(phone, country_code, email, username, client, out):
    name = "facebook"
    domain = "facebook.com"
    method = "register"
    frequent_rate_limit = False

    # Only works with email
    if not email:
        return

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # Use Facebook's login endpoint to check email
        url = "https://www.facebook.com/login.php"

        # Attempt login with email and dummy password
        login_data = {
            "email": email,
            "pass": "dummy_password_12345"
        }

        response = await client.post(url, headers=headers, data=login_data, follow_redirects=True)
        response_text = response.text.lower()

        # Check for specific indicators
        # If account doesn't exist, Facebook says "couldn't find your account" or similar
        if any(phrase in response_text for phrase in [
            "couldn't find your account",
            "the email you entered isn't connected",
            "no account found",
            "find your account",
            "recover your account"
        ]):
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False
            })
        # If account exists, Facebook asks for password or shows "wrong password"
        elif any(phrase in response_text for phrase in [
            "the password you've entered is incorrect",
            "wrong password",
            "incorrect password",
            "login_error"
        ]):
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True
            })
        # If captcha or rate limit
        elif any(phrase in response_text for phrase in [
            "captcha",
            "security check",
            "checkpoint",
            "try again later"
        ]):
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
        else:
            # Unknown response, mark as rate limited to be safe
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
    except Exception as e:
        # Specific error handling instead of bare except
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False,
            "error": str(type(e).__name__)
        })
