import dns.resolver

""" 
MX (Mail Exchange) Records
Purpose: Determines the mail servers responsible for handling emails for the domain.
Use Case: Verify if the domain has a valid setup to receive emails. If no MX record exists, the domain likely can't handle email traffic.
"""


def get_mx_records(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(mx.exchange) for mx in mx_records]
    except dns.resolver.NoAnswer:
        return None


# print(get_mx_records('gmail.com'))

"""
2. SPF (Sender Policy Framework) Records
Purpose: Ensures that only authorized servers can send emails on behalf of the domain.
Use Case: Check if the domain has a properly configured SPF record to prevent spoofing.

"""


def get_spf_record(domain):
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for txt in txt_records:
            if 'v=spf1' in str(txt):
                return str(txt)
    except dns.resolver.NoAnswer:
        return None


print(get_spf_record('theslimprep.com'))
