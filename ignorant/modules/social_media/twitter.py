from ignorant.core import *
from ignorant.localuseragent import *


async def twitter(phone, country_code, email, username, client, out):
    name = "twitter"
    domain = "twitter.com"
    method = "register"
    frequent_rate_limit = False

    # Only works with email
    if not email:
        return

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Origin": "https://twitter.com",
        "Connection": "close",
    }

    try:
        # Twitter/X's registration flow checks email availability
        # Use the account existence check endpoint
        url = "https://api.twitter.com/i/users/email_available.json"

        params = {
            "email": email
        }

        response = await client.get(url, headers=headers, params=params, follow_redirects=True)

        # Parse response
        if response.status_code == 200:
            data = response.json()
            # If email is available, account doesn't exist
            if data.get("valid", False) or data.get("taken", True) == False:
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False
                })
            else:
                # Email is taken, account exists
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True
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
            # Try alternative method - password reset flow
            reset_url = "https://twitter.com/account/begin_password_reset"
            response = await client.get(reset_url, headers=headers, follow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract form data
            form_data = {}
            for input_tag in soup.find_all('input', {'type': ['hidden']}):
                if input_tag.get('name') and input_tag.get('value'):
                    form_data[input_tag['name']] = input_tag['value']

            form_data['account_identifier'] = email

            # Submit password reset
            post_response = await client.post(reset_url, headers=headers, data=form_data, follow_redirects=True)

            # Check if account exists based on response
            response_text = post_response.text.lower()
            if "couldn't find your account" in response_text or "no account found" in response_text:
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False
                })
            else:
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True
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
