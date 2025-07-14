from twilio.rest import Client

# Twilio credentials (replace with your actual values)
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

# WhatsApp message
message = client.messages.create(
    body='Hello, this is a WhatsApp message from Python!',
    from_='whatsapp:+14155238886',  # Twilio sandbox number
    to='whatsapp:+919652203580'     # Your verified WhatsApp number
)

print("Message sent! SID:", message.sid)
