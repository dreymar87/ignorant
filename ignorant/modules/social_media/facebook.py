from ignorant.core import *
from ignorant.localuseragent import *


async def facebook(phone, country_code, email, client, out):
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
        # Use Facebook's account recovery endpoint
        url = "https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0"

        # First, get the page to extract form tokens
        response = await client.get(url, headers=headers, follow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract necessary form data
        form_data = {}
        for input_tag in soup.find_all('input', {'type': ['hidden', 'submit']}):
            if input_tag.get('name') and input_tag.get('value'):
                form_data[input_tag['name']] = input_tag['value']

        # Add the email to search for
        form_data['email'] = email

        # Submit the form
        post_url = "https://www.facebook.com/ajax/login/help/identify.php?ctx=recover"
        response = await client.post(post_url, headers=headers, data=form_data, follow_redirects=True)

        # Check response for account existence
        response_text = response.text.lower()

        # Facebook returns different responses based on whether account exists
        # If account doesn't exist, it shows "no results found" or "couldn't find your account"
        if "no results found" in response_text or "couldn't find" in response_text or "no account found" in response_text:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False
            })
        # If captcha or rate limit
        elif "captcha" in response_text or "security check" in response_text:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
        else:
            # Account likely exists
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True
            })
    except:
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False
        })
