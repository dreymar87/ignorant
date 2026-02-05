from ignorant.core import *
from ignorant.localuseragent import *


async def linkedin(phone, country_code, email, client, out):
    name = "linkedin"
    domain = "linkedin.com"
    method = "register"
    frequent_rate_limit = False

    # Only works with email
    if not email:
        return

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "Origin": "https://www.linkedin.com",
        "Connection": "close",
    }

    try:
        # LinkedIn password reset endpoint
        url = "https://www.linkedin.com/checkpoint/rp/request-password-reset-submit"

        # Get initial page for CSRF token
        init_url = "https://www.linkedin.com/checkpoint/rp/request-password-reset"
        init_response = await client.get(init_url, headers=headers, follow_redirects=True)
        soup = BeautifulSoup(init_response.text, 'html.parser')

        # Extract CSRF token
        csrf_token = ""
        for input_tag in soup.find_all('input', {'name': 'csrfToken'}):
            if input_tag.get('value'):
                csrf_token = input_tag['value']
                break

        # Alternative: check from meta tag
        if not csrf_token:
            meta_tag = soup.find('meta', {'name': 'csrf-token'})
            if meta_tag and meta_tag.get('content'):
                csrf_token = meta_tag['content']

        # Prepare data for password reset request
        data = {
            "email": email,
            "csrfToken": csrf_token
        }

        # Update headers with CSRF
        headers["Csrf-Token"] = csrf_token
        headers["Referer"] = init_url

        # Submit password reset
        response = await client.post(url, headers=headers, json=data, follow_redirects=True)

        # Check response
        if response.status_code == 200:
            response_text = response.text.lower()
            result_json = {}
            try:
                result_json = response.json()
            except:
                pass

            # Check for "no account found" or similar messages
            if "no account exists" in response_text or "couldn't find" in response_text or \
               (result_json.get("status") == "error" and "not found" in str(result_json.get("message", "")).lower()):
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False
                })
            # If we get a success or confirmation message, account exists
            elif "email sent" in response_text or "check your email" in response_text or \
                 result_json.get("status") == "success":
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True
                })
            else:
                # Try alternative method - registration check
                reg_url = "https://www.linkedin.com/signup/cold-join"
                reg_response = await client.get(reg_url, headers=headers, follow_redirects=True)
                reg_soup = BeautifulSoup(reg_response.text, 'html.parser')

                # Extract CSRF for registration
                reg_csrf = ""
                for input_tag in reg_soup.find_all('input', {'name': 'csrfToken'}):
                    if input_tag.get('value'):
                        reg_csrf = input_tag['value']
                        break

                # Check email via registration endpoint
                check_url = "https://www.linkedin.com/checkpoint/lg/login-submit"
                check_data = {
                    "session_key": email,
                    "csrfToken": reg_csrf
                }

                check_response = await client.post(check_url, headers=headers, data=check_data, follow_redirects=True)
                check_text = check_response.text.lower()

                if "couldn't find a linkedin account" in check_text or "no account found" in check_text:
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

    except:
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False
        })
