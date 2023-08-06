import os

import rich
from postmarker.core import PostmarkClient

# Replace 'YOUR_SERVER_API_TOKEN' with your Postmark server API token
# Replace 'your-verified-email@example.com' with your verified sending email
# Replace 'recipient@example.com' with the recipient's email

POSTMARK_API_KEY = os.environ.get('POSTMARK_API_KEY')
FROM_EMAIL = 'verification@brewprice.watch'
TO_EMAIL = 'mail@brewprice.watch'

print(f"SERVER_API_TOKEN: {POSTMARK_API_KEY}")

postmark = PostmarkClient(server_token=POSTMARK_API_KEY)

response = postmark.emails.send(
    From=FROM_EMAIL,
    To=TO_EMAIL,
    Subject='Test Email from Postmark',
    HtmlBody='<strong>This is a test email sent through Postmark!</strong>',
    TextBody='This is a test email sent through Postmark!'
)

print(response)
