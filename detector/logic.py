import re

import dns.resolver
from fuzzywuzzy import fuzz

# List of disposable email domains (you can expand this list)
DISPOSABLE_EMAIL_DOMAINS = [
    "mailinator.com", "10minutemail.com", "guerrillamail.com", "tempmail.com"
]

# List of popular email domains for typo-squatting detection
POPULAR_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"
]

# Regular expression for email syntax validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email_syntax(email):
    """Validate the email syntax using a regex."""
    return bool(EMAIL_REGEX.match(email))


def validate_email_domain(email):
    """Validate the domain's MX records."""
    domain = email.split('@')[-1]
    try:
        # Check for MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        return bool(mx_records)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
        return False


def is_disposable_email(email):
    """Check if the email is from a disposable email provider."""
    domain = email.split('@')[-1]
    return domain in DISPOSABLE_EMAIL_DOMAINS


def detect_typo_squatting(email):
    """Detect typo-squatting by comparing the domain with popular domains."""
    domain = email.split('@')[-1]
    for popular_domain in POPULAR_EMAIL_DOMAINS:
        similarity = fuzz.ratio(domain, popular_domain)
        if similarity > 80 and domain != popular_domain:  # Adjust threshold as needed
            return True
    return False


def validate_email(email):
    """Validate the email using all the above checks."""
    if not validate_email_syntax(email):
        return False, "Invalid email syntax."

    if is_disposable_email(email):
        return False, "Disposable email addresses are not allowed."

    if detect_typo_squatting(email):
        return False, "Suspected typo-squatting detected."

    if not validate_email_domain(email):
        return False, "Domain does not exist or has no MX records."

    return True, "Email is valid."
