from argparse import ArgumentParser
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import Popen, PIPE
from termcolor import colored
import csv
import hashlib
import hmac
import httpx
import importlib
import json
import os
import pkgutil
import random
import re
import string
import sys
import time
import trio
import urllib.parse

from ignorant.localuseragent import ua
from ignorant.instruments import TrioProgress

DEBUG = False

__version__ = "1.2"


def import_submodules(package, recursive=True):
    """Get all the ignorant submodules"""
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results

def get_functions(modules, args=None):
    """Transform the modules objects to functions"""
    websites = []

    for module in modules:
        if len(module.split(".")) > 3:
            modu = modules[module]
            site = module.split(".")[-1]

            # Filter by platform if --platforms is specified
            if args and hasattr(args, 'platforms') and args.platforms:
                if site.lower() in [p.lower() for p in args.platforms]:
                    websites.append(modu.__dict__[site])
            else:
                websites.append(modu.__dict__[site])

    return websites


def validate_email(email):
    """Validate email format"""
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone, country_code):
    """Validate phone number and country code format"""
    # Country code should be numeric and 1-3 digits
    if not country_code.isdigit() or len(country_code) > 3:
        return False, "Country code must be numeric and 1-3 digits"

    # Phone should be numeric and reasonable length (4-15 digits)
    if not phone.isdigit():
        return False, "Phone number must be numeric"

    if len(phone) < 4 or len(phone) > 15:
        return False, "Phone number must be between 4 and 15 digits"

    return True, None

def check_update():
    """Check and update ignorant if not the last version"""
    check_version = httpx.get("https://pypi.org/pypi/ignorant/json")
    if check_version.json()["info"]["version"] != __version__:
        if os.name != 'nt':
            p = Popen(["pip3",
                       "install",
                       "--upgrade",
                       "ignorant"],
                      stdout=PIPE,
                      stderr=PIPE)
        else:
            p = Popen(["pip",
                       "install",
                       "--upgrade",
                       "ignorant"],
                      stdout=PIPE,
                      stderr=PIPE)
        (output, err) = p.communicate()
        p_status = p.wait()
        print("Ignorant has just been updated, you can restart it.")
        exit()

def credit():
    """Print Credit"""
    print('Twitter : @palenath')
    print('Github : https://github.com/megadose/ignorant')
    print('For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ')


def print_result(data, args, phone, country_code, email, username, start_time, websites):
    def print_color(text, color, args):
        if args.nocolor == False:
            return(colored(text, color))
        else:
            return(text)

    if username:
        description = print_color("[+] Username found", "green", args) + "," + print_color(" [-] Username not found", "magenta", args) + "," + print_color(" [x] Rate limit", "red", args)
        display_value = f"@{username}"
    elif email:
        description = print_color("[+] Email found", "green", args) + "," + print_color(" [-] Email not found", "magenta", args) + "," + print_color(" [x] Rate limit", "red", args)
        display_value = email
    else:
        description = print_color("[+] Phone number used", "green", args) + "," + print_color(" [-] Phone number not used", "magenta", args) + "," + print_color(" [x] Rate limit", "red", args)
        display_value = "+" + str(country_code) + " " + str(phone)

    if args.noclear==False:
        print("\033[H\033[J")
    else:
        print("\n")
    print("*" * (len(display_value) + 6))
    print("   " + display_value)
    print("*" * (len(display_value) + 6))

    for results in data:
        if results["rateLimit"] and args.onlyused == False:
            websiteprint = print_color("[x] " + results["domain"], "red",args)
            print(websiteprint)
        elif results["exists"] == False and args.onlyused == False:
            websiteprint = print_color("[-] " + results["domain"], "magenta",args)
            print(websiteprint)
        elif results["exists"] == True:
            toprint = ""
            websiteprint = print_color("[+] " + results["domain"] + toprint, "green",args)
            print(websiteprint)

    print("\n" + description)
    print(str(len(websites)) + " websites checked in " +
          str(round(time.time() - start_time, 2)) + " seconds")


async def launch_module(module, phone, country_code, email, username, client, out):
    data = {'amazon': 'amazon.com', 'instagram': 'instagram.com', 'snapchat': 'snapchat.com',
            'facebook': 'facebook.com', 'twitter': 'twitter.com', 'linkedin': 'linkedin.com',
            'tiktok': 'tiktok.com', 'pinterest': 'pinterest.com', 'github': 'github.com',
            'reddit': 'reddit.com', 'pinterest': 'pinterest.com', 'tumblr': 'tumblr.com'}
    try:
        await module(phone, country_code, email, username, client, out)
    except Exception as e:
        name = str(module).split('<function ')[1].split(' ')[0]
        out.append({"name": name, "domain": data.get(name, "unknown"),
                    "rateLimit": True,
                    "exists": False,
                    "error": str(type(e).__name__)})
async def maincore():
    parser = ArgumentParser(description=f"ignorant v{__version__}")
    parser.add_argument("input",
                    nargs='+', metavar='input',
                    help="Email, username, OR country code followed by phone number")
    parser.add_argument("--only-used", default=False, required=False, action="store_true", dest="onlyused",
                    help="Displays only the sites used by the target")
    parser.add_argument("--no-color", default=False, required=False, action="store_true", dest="nocolor",
                    help="Don't color terminal output")
    parser.add_argument("--no-clear", default=False, required=False, action="store_true", dest="noclear",
                    help="Do not clear the terminal to display the results")
    parser.add_argument("-T", "--timeout", default=10, required=False, dest="timeout", type=int,
                    help="Set max timeout value (default 10)")
    parser.add_argument("-p", "--platforms", required=False, dest="platforms",
                    help="Comma-separated list of platforms to check (e.g., 'facebook,twitter,instagram')")
    parser.add_argument("-u", "--username", default=False, required=False, action="store_true", dest="username_mode",
                    help="Treat input as username instead of email/phone")

    check_update()
    args = parser.parse_args()
    credit()

    # Parse --platforms argument
    if args.platforms:
        args.platforms = [p.strip().lower() for p in args.platforms.split(',')]
        print(f"Only checking platforms: {', '.join(args.platforms)}\n")

    # Parse input to determine if email, phone, or username
    input_list = args.input
    username = None

    if args.username_mode:
        # Username mode
        if len(input_list) != 1:
            print("Error: Username mode requires exactly one argument")
            sys.exit(1)
        username = input_list[0]
        email = None
        phone = None
        country_code = None
        input_type = 'username'
        print(f"Checking username: {username}\n")

    elif len(input_list) == 1 and '@' in input_list[0]:
        # Email mode
        email = input_list[0]

        # Validate email format
        if not validate_email(email):
            print(f"Error: Invalid email format: {email}")
            print("Expected format: user@example.com")
            sys.exit(1)

        phone = None
        country_code = None
        input_type = 'email'

    elif len(input_list) == 2:
        # Phone mode
        country_code = input_list[0]
        phone = input_list[1]

        # Validate phone format
        is_valid, error_msg = validate_phone(phone, country_code)
        if not is_valid:
            print(f"Error: {error_msg}")
            print(f"Provided: country_code={country_code}, phone={phone}")
            sys.exit(1)

        email = None
        input_type = 'phone'

    elif len(input_list) == 1:
        # Could be username or malformed input
        if input_list[0].startswith('+'):
            print("Error: Please provide country code and phone number separately")
            print("Example: ignorant 1 5551234567")
            sys.exit(1)
        else:
            print("Error: Invalid input format")
            print("Examples:")
            print("  Email:    ignorant user@example.com")
            print("  Phone:    ignorant 1 5551234567")
            print("  Username: ignorant --username johndoe123")
            sys.exit(1)
    else:
        print("Error: Too many arguments")
        print("Examples:")
        print("  Email:    ignorant user@example.com")
        print("  Phone:    ignorant 1 5551234567")
        print("  Username: ignorant --username johndoe123")
        sys.exit(1)

    # Import Modules
    modules = import_submodules("ignorant.modules")
    websites = get_functions(modules, args)

    if len(websites) == 0:
        print("Error: No platforms match your selection")
        if args.platforms:
            print(f"Available platforms: amazon, instagram, snapchat, facebook, twitter, linkedin, tiktok, github, reddit, pinterest, tumblr")
        sys.exit(1)

    timeout = args.timeout
    # Start time
    start_time = time.time()
    # Def the async client
    client = httpx.AsyncClient(timeout=timeout)
    # Launching the modules
    out = []
    instrument = TrioProgress(len(websites))
    trio.lowlevel.add_instrument(instrument)
    async with trio.open_nursery() as nursery:
        for website in websites:
            nursery.start_soon(launch_module, website, phone, country_code, email, username, client, out)
    trio.lowlevel.remove_instrument(instrument)
    # Sort by modules names
    out = sorted(out, key=lambda i: i['name'])
    # Close the client
    await client.aclose()
    # Print the result
    print_result(out, args, phone, country_code, email, username, start_time, websites)
    credit()
def main():
    trio.run(maincore)
