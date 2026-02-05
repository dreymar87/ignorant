from ignorant.core import *
from ignorant.localuseragent import *

#https://github.com/yazeed44/social-media-detector-api

USERS_LOOKUP_URL = 'https://i.instagram.com/api/v1/users/lookup/'
SIG_KEY_VERSION = '4'
IG_SIG_KEY = 'e6358aeede676184b9fe702b30f4fd35e71744605e39d2181a34cede076b3c33'


def generate_signature(data):
    return 'ig_sig_key_version=' + SIG_KEY_VERSION + '&signed_body=' + hmac.new(IG_SIG_KEY.encode('utf-8'),data.encode('utf-8'),hashlib.sha256).hexdigest() + '.'+ urllib.parse.quote_plus(data)

def generate_data( phone_number_raw):
    data = {'login_attempt_count': '0',
            'directly_sign_in': 'true',
            'source': 'default',
            'q': phone_number_raw,
            'ig_sig_key_version': SIG_KEY_VERSION
            }
    return data

async def instagram(phone, country_code, email, username, client, out):
    name = "instagram"
    domain = "instagram.com"
    method = "other"
    frequent_rate_limit=False

    # Handle phone lookup
    if phone:
        data=generate_signature(json.dumps(generate_data(str(country_code)+str(phone))))
        headers={
        "Accept-Language": "en-US",
        "User-Agent": "Instagram 101.0.0.15.120",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "X-FB-HTTP-Engine": "Liger",
        "Connection": "close"}
        try:
            r = await client.post(USERS_LOOKUP_URL,headers=headers,data=data)
            rep=r.json()
            if "message" in rep.keys() and rep["message"]=="No users found":
                out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                            "rateLimit": False,
                            "exists": False})
            else:
                out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                            "rateLimit": False,
                            "exists": True})
        except Exception as e:
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": True,
                        "exists": False})
    # Handle username lookup
    elif username:
        headers = {
            "User-Agent": random.choice(ua["browsers"]["chrome"]),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "close",
        }
        try:
            # Instagram profile page check
            url = f"https://www.instagram.com/{username}/"
            response = await client.get(url, headers=headers, follow_redirects=True)

            # If profile exists, status code is 200 and contains specific elements
            if response.status_code == 200:
                response_text = response.text.lower()
                # Check if it's a valid profile page (not a 404 page)
                if "not found" in response_text or "this page isn't available" in response_text:
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
            elif response.status_code == 404:
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False
                })
            else:
                # Rate limited or other error
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
    # Handle email lookup
    elif email:
        headers = {
            "User-Agent": random.choice(ua["browsers"]["chrome"]),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "close",
        }
        try:
            # Instagram signup API to check email availability
            url = "https://www.instagram.com/accounts/web_create_ajax/attempt/"

            # Get initial page for CSRF token
            init_response = await client.get("https://www.instagram.com/accounts/emailsignup/", headers=headers)

            # Extract CSRF token from cookies
            csrf_token = init_response.cookies.get("csrftoken", "")

            # Add CSRF to headers
            headers["X-CSRFToken"] = csrf_token
            headers["Referer"] = "https://www.instagram.com/accounts/emailsignup/"

            # Check email availability
            data = {
                "email": email,
                "username": "",
                "first_name": "",
                "opt_into_one_tap": "false"
            }

            response = await client.post(url, headers=headers, data=data, follow_redirects=True)

            if response.status_code == 200:
                result = response.json()
                # If email is available (errors about email being taken)
                if "errors" in result and "email" in result["errors"]:
                    error_msg = str(result["errors"]["email"])
                    if "Another account is using" in error_msg or "already in use" in error_msg.lower():
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
                else:
                    # No email error means it's available
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False
                    })
            else:
                # Rate limited or other error
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
