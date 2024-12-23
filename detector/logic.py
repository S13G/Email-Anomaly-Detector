import re
from email import message_from_string

import dns.resolver

""" 
MX (Mail Exchange) Records
Purpose: Determines the mail servers responsible for handling emails for the domain.
Use Case: Verify if the domain has a valid setup to receive emails. If no MX record exists, the domain likely can't handle email traffic.
"""


def get_mx_records(domain_name):
    try:
        mx_records = dns.resolver.resolve(domain_name, 'MX')
        return [str(mx.exchange) for mx in mx_records]  # noqa
    except dns.resolver.NoAnswer:
        return None


# print(get_mx_records('gmail.com'))

"""
2. SPF (Sender Policy Framework) Records
Purpose: Ensures that only authorized servers can send emails on behalf of the domain.
Use Case: Check if the domain has a properly configured SPF record to prevent spoofing.
Though for automatic validation pyspf2 can be used though you must provide the sender's ip address, you can extract
this from the raw email content header.
"""


def get_spf_record(domain_name):
    try:
        txt_records = dns.resolver.resolve(domain_name, 'TXT')
        for txt in txt_records:
            if 'v=spf1' in str(txt):
                return str(txt)
    except dns.resolver.NoAnswer:
        return None


def parse_spf(spf_record):
    mechanisms = spf_record.split()  # Split the SPF record into components
    parsed = {}
    for mech in mechanisms:
        if '=' in mech:
            key, value = mech.split('=', 1)
            parsed[key] = value
        elif mech.startswith('ip4:') or mech.startswith('ip6:'):
            parsed[mech.split(':')[0]] = mech.split(':')[1]
        elif mech.startswith('include:'):
            parsed['include'] = mech.split(':')[1]
    return parsed


spf = get_spf_record('theslimprep.com')
if spf:
    parsed_spf = parse_spf(spf)
    print(parsed_spf)

"""
The code above parses the SPF record but does not fully validate it. 
Parsing an SPF record is just the first step in SPF validation. Full validation involves checking whether a 
given sender's IP address is authorized according to the SPF mechanisms and qualifiers in the record.

Example of retrieving sender email IP Address
"""


def extract_sender_ip(raw_email):  # noqa
    msg = message_from_string(raw_email)
    received_headers = msg.get_all("Received")

    if not received_headers:
        return None, "No 'Received' headers found"

    # Check the first 'Received' header for the sender's IP
    sender_ip = None  # noqa
    for header in received_headers:
        # Regex to find an IP address in the header
        match = re.search(r"\[([0-9]{1,3}(?:\.[0-9]{1,3}){3})\]", header)  # noqa
        if match:
            sender_ip = match.group(1)  # noqa
            break

    return sender_ip or "IP not found", received_headers


# Example
raw_email = """
Received: from sender.example.com ([192.0.2.1]) by recipient.example.com;
Received: from internal.mailserver (10.0.0.1) by sender.example.com;
Subject: Test Email
From: sender@example.com
To: recipient@example.com
Date: Fri, 23 Dec 2024 10:00:00 -0000
"""
sender_ip, headers = extract_sender_ip(raw_email)
# print(f"Sender's IP: {sender_ip}")


"""
Validation Code for SPF
"""


def validate_spf(spf_record, sender_ip):  # noqa
    parsed = parse_spf(spf_record)

    # Validate against `ip4` mechanisms
    for key, value in parsed.items():
        if key == 'ip4' and sender_ip.startswith(value.split('/')[0]):
            return 'Pass'
        if key == 'all':
            return 'Neutral'

    # Handle include or redirect logic (simplified)
    if 'include' in parsed:
        included_spf = get_spf_record(parsed['include'])
        if included_spf:
            return validate_spf(included_spf, sender_ip)

    return 'Fail'


# Example Usage
domain = "example.com"
sender_ip = "192.0.2.1"  # Replace with the actual sender's IP address  # noqa
spf = get_spf_record(domain)

if spf:
    result = validate_spf(spf, sender_ip)
    print(f"SPF Validation Result: {result}")
else:
    print("No SPF record found")
