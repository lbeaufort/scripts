"""
Using API umbrella API, get the keys with > 100 request IPs and non-FEC domains

API docs: https://api-umbrella.readthedocs.io/en/latest/admin/api.html
https://open.gsa.gov/api/apidatagov/

"""

import requests
import os
from datetime import date

today = date.today()

# Get this from your admin details
ADMIN_AUTH_TOKEN = os.environ.get("UMBRELLA_ADMIN_AUTH_TOKEN", "")
# Any API key, make sure it has enough requests/minute
API_KEY = os.environ.get("FEC_API_KEY", "")

# Today, can be any range
start_date = today.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

headers = {
    "X-Admin-Auth-Token": ADMIN_AUTH_TOKEN,
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json; charset=UTF-8",
}

active_users = """https://api.data.gov/admin/stats/users.json?start=0&length=1000&search=&start_at={0}&end_at={1}""".format(
    start_date, end_date
)

user_data = "https://api.data.gov/api-umbrella/v1/users/{}"

ip_aggregates = "https://api.data.gov/admin/stats/search.json?start_at={}&end_at={}&interval=day&query=%7B%22condition%22%3A%22AND%22%2C%22rules%22%3A%5B%7B%22field%22%3A%22gatekeeper_denied_code%22%2C%22id%22%3A%22gatekeeper_denied_code%22%2C%22input%22%3A%22select%22%2C%22operator%22%3A%22is_null%22%2C%22type%22%3A%22string%22%2C%22value%22%3Anull%7D%5D%7D&search=user_id%3A%22{}%22"

print("Getting active users from {} to {}".format(start_date, end_date))

response = requests.get(active_users, headers=headers)
data = response.json().get("data")

print("user_email,user_id,last_request,total_ips,total_hits")
count = 0

for result in data:
    user_id = result.get("id")
    domain = result.get("email").split("@")[1]
    last_request = result.get("last_request_at")

    # Get the details
    details = requests.get(user_data.format(user_id), headers=headers)
    body = details.json()
    user_email = body.get("user").get("email")
    # IP aggregates
    user_ip_aggregates = requests.get(
        ip_aggregates.format(start_date, end_date, user_id), headers=headers
    ).json()
    total_ips = user_ip_aggregates.get("stats").get("total_ips")
    total_hits = user_ip_aggregates.get("stats").get("total_hits")
    if int(total_ips) > 100 and domain != "fec.gov":
        print(
            '"{}","{}","{}","{}","{}"'.format(
                user_email, user_id, last_request, total_ips, total_hits
            )
        )
        count += 1

print(count)
