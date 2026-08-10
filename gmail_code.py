
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email account details
GMAIL_USER = "emailfornewsbot1@gmail.com"
GMAIL_PASS = "vauf dray imwe plmk"

# Receiver email
RECEIVER_EMAIL = "atulkushwaha0112@gmail.com"


def send_email(subject="Hello", html_body="This is the message"):
    """Send one HTML email with subject + formatted body."""
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject

        # Attach HTML content (supports links, images, formatting)
        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Error:", e)


# -------- Write your subject & email body here --------

subject = "Test Email"

html_body =  """
<h1 style="color:blue;">Today's News Update</h1>

<p>Hello everyone, here is the latest update:</p>

<h2>🔥 Big Headline</h2>
<p>
This is a <b>long formatted paragraph</b> with HTML support,
including lists, hyperlinks, and images.
</p>

<ul>
    <li>Point One</li>
    <li>Point Two</li>
    <li>Point Three</li>
</ul>

<h3>🌐 Useful Link</h3>
<p>Click here: <a href="https://www.google.com">Open Google</a></p>

<h3>🖼️ Image Example</h3>
<p>
    <img
        src="https://blogger.googleusercontent.com/img/a/AVvXsEhcb-gzLVStqe9W3owcd1H8FjIPIMdV0NR4GYXHHVrjUic1cU_Q8-AreMOJURaMl_RZC0Q7y8RLkBS1pfzJnqnRsvpjY7W3Al-98dkPrFPh5YYzPsXjaZwdwZscQJ0EZx1GK2csvjPZyheVVWWFzMU-9cUqF9GimmrtXArtVwqN1PQVjPCansT0l46QYQYc=s150"
        alt="Example Image"
        style="width:300px;"
    >
</p>

<p>Thank you!</p>
"""

# -------- Send the email once --------
send_email(subject, html_body)
