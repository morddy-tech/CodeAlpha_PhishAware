"""Seed scenarios for PhishAware.

All scenarios use clearly fictional organizations and domains (example.com
and friends). This is defensive, educational material only - no real
credentials, payments, or targets are involved.
"""

SCENARIOS = [
    {
        "title": "Urgent Invoice Payment Required",
        "scenario_type": "email",
        "difficulty": "beginner",
        "description": (
            "A fictional email claims a vendor invoice is overdue and asks the "
            "recipient to wire payment immediately to a new account."
        ),
        "sender": "Accounts Payable",
        "source": "billing@invoice-center.example.net",
        "recipient": "you@example.com",
        "subject": "URGENT: Overdue Invoice 88231 - Payment Due Today",
        "simulated_content": "Simulated phishing email",
        "body": (
            "Dear Customer,\n\n"
            "This is a final notice that invoice #88231 in the amount of "
            "$4,850.00 is now overdue. To avoid late fees and disruption of "
            "your service, please arrange payment immediately.\n\n"
            "Payment must be completed within 24 hours. Use the secure link "
            "below to review the invoice and pay now.\n\n"
            "Click here to pay your invoice securely\n"
            "https://secure-pay.invoice-center.example.net/pay\n\n"
            "If the link does not work, paste it into your browser. Do not "
            "ignore this message.\n\n"
            "Accounts Payable\n"
            "Invoice Center"
        ),
        "links": [
            {"label": "Click here to pay your invoice securely", "url": "https://secure-pay.invoice-center.example.net/pay"}
        ],
        "attachment_name": "invoice_88231.docm",
        "explanation": (
            "This message is a phishing simulation. The sender domain does not "
            "match a known vendor, the message creates false urgency, the link "
            "points to an unusual domain, and an unexpected attachment is "
            "included. The correct action is to verify the invoice with your "
            "finance team or the vendor using an official channel, then report "
            "the message. Never pay a bill from an unsolicited email."
        ),
        "indicators": [
            {
                "title": "Sender domain does not match the claimed vendor",
                "indicator_type": "domain",
                "location": "sender",
                "severity": "high",
                "description": "billing@invoice-center.example.net is not a known, official vendor domain.",
            },
            {
                "title": "Urgent 24-hour payment demand",
                "indicator_type": "urgency",
                "location": "subject/body",
                "severity": "high",
                "description": "Legitimate invoices rarely demand payment within 24 hours via email.",
            },
            {
                "title": "Link leads to an unusual lookalike domain",
                "indicator_type": "link",
                "location": "body",
                "severity": "high",
                "description": "https://secure-pay.invoice-center.example.net is not the official payment site.",
            },
            {
                "title": "Unexpected document attachment",
                "indicator_type": "attachment",
                "location": "attachment",
                "severity": "medium",
                "description": "invoice_88231.docm is an unsolicited Office attachment that could carry macros.",
            },
            {
                "title": "Generic greeting addressed to 'Customer'",
                "indicator_type": "spoof",
                "location": "body",
                "severity": "low",
                "description": "Real vendors address you by name or account reference.",
            },
            {
                "title": "Politely worded reminder",
                "indicator_type": "other",
                "location": "body",
                "severity": "low",
                "is_distractor": True,
                "description": "This is benign text; tone alone is not a red flag.",
            },
        ],
        "response_options": [
            {
                "text": "Verify the invoice with the vendor and finance team, then report the email",
                "is_correct": True,
                "explanation": "Verify out of band through an official channel and report the suspicious message.",
            },
            {
                "text": "Click the link and pay now to avoid late fees",
                "is_correct": False,
                "explanation": "Clicking the link could lead to a fake payment page or malware. Never act on an unsolicited payment demand.",
            },
            {
                "text": "Open the attachment to check the invoice",
                "is_correct": False,
                "explanation": "Unexpected attachments are a common malware delivery method. Do not open them.",
            },
            {
                "text": "Reply to the email asking for more details",
                "is_correct": False,
                "explanation": "Replying confirms your address is active and gives attackers more material. Verify out of band instead.",
            },
        ],
    },
    {
        "title": "Your Account Will Be Suspended",
        "scenario_type": "email",
        "difficulty": "beginner",
        "description": (
            "A fictional message claims an online account will be suspended and "
            "asks the recipient to sign in on a lookalike page."
        ),
        "sender": "CloudSafe Security",
        "source": "alerts@cloudsafe-security.example.com",
        "recipient": "you@example.com",
        "subject": "Action Required: Your Account Will Be Suspended",
        "simulated_content": "Simulated phishing email",
        "body": (
            "Dear Valued User,\n\n"
            "We detected unusual activity on your account. As a security "
            "precaution, your access will be suspended within 24 hours unless "
            "you confirm your identity.\n\n"
            "Confirm now to keep your account active:\n"
            "https://cloudsafe-security.example-verify.net/confirm\n\n"
            "If you do nothing, your account and data will be permanently "
            "locked. This is the final warning.\n\n"
            "CloudSafe Security Team"
        ),
        "links": [
            {"label": "Confirm now to keep your account active", "url": "https://cloudsafe-security.example-verify.net/confirm"}
        ],
        "attachment_name": "",
        "explanation": (
            "This is a simulated phishing email. The real company domain is "
            "cloudsafe-security.example.com, but the link points to "
            "cloudsafe-security.example-verify.net - a lookalike. The threat "
            "of suspension and the 24-hour deadline are classic urgency tactics. "
            "The correct response is to ignore the link and sign in by "
            "typing the official address yourself, then report the message."
        ),
        "indicators": [
            {
                "title": "Link domain does not match the official company domain",
                "indicator_type": "domain",
                "location": "body link",
                "severity": "high",
                "description": "example-verify.net is a lookalike domain, not the official cloudsafe-security.example.com.",
            },
            {
                "title": "Threat of account suspension within 24 hours",
                "indicator_type": "urgency",
                "location": "subject/body",
                "severity": "high",
                "description": "Real services do not force action through threatening emails.",
            },
            {
                "title": "Generic 'Valued User' greeting",
                "indicator_type": "spoof",
                "location": "body",
                "severity": "medium",
                "description": "A legitimate service would address you by name.",
            },
            {
                "title": "Generic warning subject line",
                "indicator_type": "other",
                "location": "subject",
                "severity": "low",
                "is_distractor": True,
                "description": "Subject lines that mention security are common but not red flags by themselves.",
            },
        ],
        "response_options": [
            {
                "text": "Ignore the link, sign in via the official website, and report the email",
                "is_correct": True,
                "explanation": "Navigate to the real site yourself, check for alerts, and report the suspicious message.",
            },
            {
                "text": "Click the confirmation link immediately",
                "is_correct": False,
                "explanation": "The link leads to a fake login page designed to capture your credentials.",
            },
            {
                "text": "Forward the email to a friend for advice",
                "is_correct": False,
                "explanation": "Report to your security team or the real company instead of forwarding to others.",
            },
            {
                "text": "Delete the email and change nothing",
                "is_correct": False,
                "explanation": "Deleting is fine, but you should report it so others are protected too.",
            },
        ],
    },
    {
        "title": "Fake Package Delivery Notification",
        "scenario_type": "email",
        "difficulty": "intermediate",
        "description": (
            "A fictional delivery company sends a tracking notice with a link "
            "and an attachment."
        ),
        "sender": "SwiftShip Logistics",
        "source": "no-reply@swiftship-delivery.example.co",
        "recipient": "you@example.com",
        "subject": "Your package could not be delivered",
        "simulated_content": "Simulated phishing email",
        "body": (
            "Hello,\n\n"
            "We attempted to deliver your package today but no one was "
            "available. To reschedule your delivery, open the attachment or "
            "use the link below.\n\n"
            "View tracking details: https://swiftship-delivery.example.co/trk\n"
            "Attachment: delivery_schedule.pdf.zip\n\n"
            "Reschedule within 48 hours to avoid returning the package to "
            "sender.\n\n"
            "SwiftShip Logistics - Customer Care"
        ),
        "links": [
            {"label": "View tracking details", "url": "https://swiftship-delivery.example.co/trk"}
        ],
        "attachment_name": "delivery_schedule.pdf.zip",
        "explanation": (
            "This simulated delivery notice is a phishing attempt. The sender "
            "domain swiftship-delivery.example.co is not an official delivery "
            "service, the zip attachment is a classic malware delivery method, "
            "and the 48-hour reschedule deadline creates urgency. Verify the "
            "tracking number on the courier's official website before doing "
            "anything."
        ),
        "indicators": [
            {
                "title": "Zip attachment conceals malware",
                "indicator_type": "attachment",
                "location": "attachment",
                "severity": "high",
                "description": "delivery_schedule.pdf.zip is an unsolicited archive - a common malware delivery method.",
            },
            {
                "title": "Sender domain is not an official courier",
                "indicator_type": "domain",
                "location": "sender",
                "severity": "high",
                "description": "no-reply@swiftship-delivery.example.co is not the official SwiftShip address.",
            },
            {
                "title": "48-hour reschedule deadline",
                "indicator_type": "urgency",
                "location": "body",
                "severity": "medium",
                "description": "Real couriers do not threaten to return packages in emails with links.",
            },
            {
                "title": "Addresses you by 'Hello' only",
                "indicator_type": "spoof",
                "location": "body",
                "severity": "low",
                "description": "A real courier would use your name and a tracking number.",
            },
            {
                "title": "The courier name is mentioned correctly",
                "indicator_type": "other",
                "location": "body",
                "severity": "low",
                "is_distractor": True,
                "description": "Correct branding in the text is not evidence of authenticity.",
            },
        ],
        "response_options": [
            {
                "text": "Check the tracking number on the official courier site, then report",
                "is_correct": True,
                "explanation": "Verify out of band with the real courier using a known website or app, then report the message.",
            },
            {
                "text": "Open the attachment to see the delivery schedule",
                "is_correct": False,
                "explanation": "Never open an unexpected archive attachment; it can install malware.",
            },
            {
                "text": "Click the tracking link to reschedule",
                "is_correct": False,
                "explanation": "The link may lead to credential theft or a malicious download.",
            },
            {
                "text": "Reply asking for your tracking number",
                "is_correct": False,
                "explanation": "Replying tells attackers your address is active. Verify out of band instead.",
            },
        ],
    },
    {
        "title": "Fake Webmail Login Page",
        "scenario_type": "website",
        "difficulty": "intermediate",
        "description": (
            "A simulated phishing page that imitates a webmail login. The "
            "learner must spot the domain mismatch and other clues. Any "
            "text typed into the simulated fields is discarded immediately - "
            "it is never stored or transmitted."
        ),
        "sender": "",
        "source": "https://webmail-secure.example.net/signin",
        "recipient": "",
        "subject": "",
        "site_name": "WebMail Secure Center",
        "simulated_content": (
            "SIMULATION: This page is a training exercise. Do not enter a real "
            "password. The form is decorative - your entry is discarded and "
            "never stored or sent anywhere."
        ),
        "body": (
            "Your mailbox requires verification. Recent security scans found "
            "unusual activity. You must re-verify your identity within 10 "
            "minutes or your mailbox will be locked permanently.\n\n"
            "Sign in below to continue:"
        ),
        "links": [],
        "attachment_name": "",
        "explanation": (
            "This simulated login page shows classic fake-website clues: the "
            "URL domain webmail-secure.example.net does not match your real "
            "webmail provider, the branding is generic and slightly off, the "
            "10-minute countdown manufactures urgency, and a login page should "
            "never threaten you with account locks. The correct action is to "
            "close the page and sign in through your real provider's known "
            "address. Remember: never enter a real password on a page you "
            "reached from a message."
        ),
        "indicators": [
            {
                "title": "Domain does not match your real webmail provider",
                "indicator_type": "domain",
                "location": "address bar",
                "severity": "high",
                "description": "webmail-secure.example.net is a lookalike domain, not your provider's official address.",
            },
            {
                "title": "10-minute countdown threatens account lock",
                "indicator_type": "urgency",
                "location": "page text",
                "severity": "high",
                "description": "Legitimate login pages do not threaten to lock your account.",
            },
            {
                "title": "Unexpected request to verify identity",
                "indicator_type": "credentials",
                "location": "login form",
                "severity": "high",
                "description": "You were not expecting this authentication request - that is a warning sign.",
            },
            {
                "title": "Generic branding and off colors",
                "indicator_type": "spoof",
                "location": "page design",
                "severity": "medium",
                "description": "The logo and styling are generic and differ from the real provider.",
            },
            {
                "title": "The page uses a secure HTTPS connection",
                "indicator_type": "other",
                "location": "address bar",
                "severity": "low",
                "is_distractor": True,
                "description": "HTTPS only proves encryption, not authenticity. Fake sites can have padlocks.",
            },
        ],
        "response_options": [
            {
                "text": "Close the page and sign in via your provider's official address",
                "is_correct": True,
                "explanation": "Never sign in on a page you reached from a message. Navigate to the real site yourself.",
            },
            {
                "text": "Enter your password to verify the account",
                "is_correct": False,
                "explanation": "Entering a real password here would hand it to attackers. The fields are simulated and nothing is stored.",
            },
            {
                "text": "Click the link in the original message that brought you here",
                "is_correct": False,
                "explanation": "That link is exactly how you were brought to a fake site. Go directly to the official address instead.",
            },
            {
                "text": "Submit any random text to test the page",
                "is_correct": False,
                "explanation": "Even testing can reveal data to attackers. Close the page and report it instead.",
            },
        ],
    },
    {
        "title": "Bank Account Suspension Text",
        "scenario_type": "sms",
        "difficulty": "beginner",
        "description": (
            "A simulated text message warns of bank account suspension and "
            "asks the recipient to call a number or follow a link."
        ),
        "sender": "NationalBank",
        "source": "+1 (555) 014-2290",
        "recipient": "",
        "subject": "NationalBank Alert",
        "simulated_content": "Simulated SMS message",
        "body": (
            "NATIONALBANK ALERT: Your debit card has been blocked due to "
            "suspicious activity. Call our fraud line immediately at "
            "+1 (555) 014-2290 to reactivate your card."
        ),
        "links": [{"label": "NationalBank SMS alert", "url": "https://nb-verify.example.net"}],
        "attachment_name": "",
        "explanation": (
            "This simulated SMS is smishing. The number is not NationalBank's "
            "official fraud line, and banks never ask you to call a random "
            "number to 'reactivate' a card. The correct action is to ignore "
            "the message, call the number on the back of your card or your "
            "official banking app, and report the SMS to your bank."
        ),
        "indicators": [
            {
                "title": "Unknown phone number not associated with your bank",
                "indicator_type": "domain",
                "location": "caller/sender",
                "severity": "high",
                "description": "+1 (555) 014-2290 is not your bank's official fraud line.",
            },
            {
                "title": "Threat of card blockage and urgent reactivation",
                "indicator_type": "urgency",
                "location": "message",
                "severity": "high",
                "description": "Fear of losing access is used to rush you into calling the attacker.",
            },
            {
                "title": "Request to call a provided number",
                "indicator_type": "social",
                "location": "message",
                "severity": "medium",
                "description": "Always use the number you already have, never one supplied in a suspicious message.",
            },
            {
                "title": "Shortened or unusual link attached",
                "indicator_type": "link",
                "location": "message",
                "severity": "medium",
                "description": "nb-verify.example.net is not a bank domain.",
            },
            {
                "title": "The message is written in a polite tone",
                "indicator_type": "other",
                "location": "message",
                "severity": "low",
                "is_distractor": True,
                "description": "Politeness is not evidence of legitimacy.",
            },
        ],
        "response_options": [
            {
                "text": "Ignore it, call your bank using the official number, and report the SMS",
                "is_correct": True,
                "explanation": "Verify using the number on your card or in your banking app, then report the text.",
            },
            {
                "text": "Call the number provided to reactivate your card",
                "is_correct": False,
                "explanation": "Calling the number puts you directly in contact with the attacker.",
            },
            {
                "text": "Reply STOP to the message",
                "is_correct": False,
                "explanation": "Replying confirms your number is active and in use. Do not engage.",
            },
            {
                "text": "Forward the text to your contacts to warn them",
                "is_correct": False,
                "explanation": "Report to your bank and carrier instead of forwarding to others.",
            },
        ],
    },
    {
        "title": "IT Support Requests Your MFA Code",
        "scenario_type": "phone",
        "difficulty": "advanced",
        "description": (
            "A simulated phone call from 'IT support' asks the employee to read "
            "back a one-time login code."
        ),
        "sender": "Danny from IT",
        "source": "+1 (555) 013-7721",
        "recipient": "",
        "subject": "Inbound call - Vishing simulation",
        "simulated_content": "Simulated phone conversation",
        "body": (
            "Hello, this is Danny from the IT Service Desk. We are running a "
            "security update and need to verify your account. You should have "
            "just received a text message with a 6-digit code. Please read it "
            "back to me so I can confirm your identity and keep your access "
            "active."
        ),
        "links": [],
        "attachment_name": "",
        "explanation": (
            "This simulated call is vishing combined with an MFA code scam. "
            "Legitimate IT support will never ask you to read back a one-time "
            "code. With your password and that code, an attacker can take over "
            "your account. The correct action is to hang up, then call the "
            "official IT helpdesk number to check whether the call was real, "
            "and never share the code."
        ),
        "indicators": [
            {
                "title": "Caller asks you to read back a one-time code",
                "indicator_type": "credentials",
                "location": "call",
                "severity": "high",
                "description": "A one-time code is a secret second factor. No legitimate support asks for it.",
            },
            {
                "title": "Unknown phone number for 'IT support'",
                "indicator_type": "domain",
                "location": "caller ID",
                "severity": "high",
                "description": "+1 (555) 013-7721 is not a known helpdesk number; caller ID can also be spoofed.",
            },
            {
                "title": "Caller pressures you to act right away",
                "indicator_type": "urgency",
                "location": "call",
                "severity": "medium",
                "description": "Real support teams do not pressure you to reveal codes during a call.",
            },
            {
                "title": "Generic reason: 'security update'",
                "indicator_type": "social",
                "location": "call",
                "severity": "medium",
                "description": "Vague justifications are used to make requests seem routine.",
            },
            {
                "title": "The caller uses a friendly tone",
                "indicator_type": "other",
                "location": "call",
                "severity": "low",
                "is_distractor": True,
                "description": "Friendliness is a social-engineering tool, not proof of identity.",
            },
        ],
        "response_options": [
            {
                "text": "Hang up and verify with the official IT helpdesk before acting",
                "is_correct": True,
                "explanation": "End the call and verify through a known channel. Never share codes with inbound callers.",
            },
            {
                "text": "Read back the code so your account stays active",
                "is_correct": False,
                "explanation": "Sharing the code lets the attacker log in as you. Real support never asks for it.",
            },
            {
                "text": "Ask the caller to email you confirmation first",
                "is_correct": False,
                "explanation": "The 'confirmation' email would come from the attacker too. Verify out of band instead.",
            },
            {
                "text": "Give them your password to prove who you are",
                "is_correct": False,
                "explanation": "Never share your password with anyone, for any reason.",
            },
        ],
    },
    {
        "title": "Your Manager Needs Gift Cards",
        "scenario_type": "social",
        "difficulty": "intermediate",
        "description": (
            "A message that appears to come from a senior manager asks an "
            "employee to urgently buy gift cards for a client."
        ),
        "sender": "Sarah Mitchell (Executive VP)",
        "source": "sarah.mitchell@executive-suite.example.net",
        "recipient": "you@example.com",
        "subject": "Quick favour needed",
        "simulated_content": "Simulated chat/email message",
        "body": (
            "Hi, are you free? I am in back-to-back meetings and need a quick "
            "favour. We need to send gift cards to a client as a thank-you, "
            "and the vendor only takes physical cards. Can you buy four $500 "
            "gift cards from the shop downstairs and send me the codes? I will "
            "sort the reimbursement as soon as I am out of meetings. Please "
            "keep this quiet - I do not want procurement to hold things up. "
            "It is urgent."
        ),
        "links": [],
        "attachment_name": "",
        "explanation": (
            "This simulated message is a social engineering attack, not a real "
            "request. It impersonates authority, demands urgency and secrecy, "
            "and asks for something unusual (gift card codes). Real managers "
            "verify such requests through official channels and never demand "
            "secrecy. The correct action is to verify the request with the "
            "person directly (in person or on a known number) and report it to "
            "your security team."
        ),
        "indicators": [
            {
                "title": "Request to buy gift cards and share the codes",
                "indicator_type": "payment",
                "location": "message",
                "severity": "high",
                "description": "Gift card codes are untraceable money - the classic final step of this scam.",
            },
            {
                "title": "Demand for urgency and secrecy",
                "indicator_type": "urgency",
                "location": "message",
                "severity": "high",
                "description": "'Keep this quiet' and 'it is urgent' are pressure tactics to bypass normal checks.",
            },
            {
                "title": "Sender address is not the real company domain",
                "indicator_type": "domain",
                "location": "sender",
                "severity": "high",
                "description": "executive-suite.example.net does not match your organization's official domain.",
            },
            {
                "title": "Out-of-character request from a senior leader",
                "indicator_type": "social",
                "location": "message",
                "severity": "medium",
                "description": "Unexpected personal favours with financial implications are a warning sign.",
            },
            {
                "title": "The manager's name is spelled correctly",
                "indicator_type": "other",
                "location": "message",
                "severity": "low",
                "is_distractor": True,
                "description": "Correct names are easy for attackers to find online.",
            },
        ],
        "response_options": [
            {
                "text": "Verify the request with the manager in person or on a known number, then report",
                "is_correct": True,
                "explanation": "Confirm through an official channel before spending anything, and report the request to security.",
            },
            {
                "text": "Buy the gift cards and send the codes right away",
                "is_correct": False,
                "explanation": "Sending gift card codes is irreversible and untraceable - the scam's end goal.",
            },
            {
                "text": "Reply asking for the exact client details",
                "is_correct": False,
                "explanation": "Engaging gives the attacker more material. Verify out of band first.",
            },
            {
                "text": "Forward the message to your colleagues for opinions",
                "is_correct": False,
                "explanation": "Report to security instead of spreading the message around the company.",
            },
        ],
    },
    {
        "title": "Supplier Requests New Bank Details",
        "scenario_type": "social",
        "difficulty": "advanced",
        "description": (
            "A message claiming to be from a known supplier asks the finance "
            "team to update payment details for all future invoices."
        ),
        "sender": "Acme Supplies Ltd",
        "source": "accounts@acme-supplies.example.com",
        "recipient": "finance@example.com",
        "subject": "IMPORTANT: Updated banking details for Acme Supplies",
        "simulated_content": "Simulated email (BEC scenario)",
        "body": (
            "Dear Finance Team,\n\n"
            "We are consolidating our banking with a new partner and our "
            "payment details have changed. Please update your records "
            "immediately so that future invoices are not delayed.\n\n"
            "New details:\n"
            "Bank: Example Fictional Bank\n"
            "Account: 00-1234 5678\n"
            "Sort/IBAN: FICB 001234567890\n\n"
            "Please confirm receipt of this change by replying to this email. "
            "Our contact person, Marcus Lee, is available on the number in "
            "your records if you have any questions.\n\n"
            "Best regards,\n"
            "Acme Supplies Ltd"
        ),
        "links": [],
        "attachment_name": "",
        "explanation": (
            "This simulated BEC email asks for a change of bank details - the "
            "classic payment-diversion scam. The domain acme-supplies.example.com "
            "looks plausible but is not the supplier's verified address. Any "
            "request to change payment details must be verified with the "
            "supplier through an already-known phone number, never by replying "
            "to the email. Report it to your security team."
        ),
        "indicators": [
            {
                "title": "Unrequested change of bank details",
                "indicator_type": "payment",
                "location": "message",
                "severity": "high",
                "description": "Payment-detail changes without prior agreement are a hallmark of BEC fraud.",
            },
            {
                "title": "Sender domain not confirmed as the supplier's official address",
                "indicator_type": "domain",
                "location": "sender",
                "severity": "high",
                "description": "acme-supplies.example.com must be verified against the supplier's known records.",
            },
            {
                "title": "Asks for immediate action on financial records",
                "indicator_type": "urgency",
                "location": "message",
                "severity": "medium",
                "description": "Pressure to 'update immediately' is designed to skip verification steps.",
            },
            {
                "title": "Changes payment details via email only",
                "indicator_type": "social",
                "location": "message",
                "severity": "medium",
                "description": "Legitimate suppliers confirm such changes through formal, verified channels.",
            },
            {
                "title": "The message references a real project name",
                "indicator_type": "other",
                "location": "message",
                "severity": "low",
                "is_distractor": True,
                "description": "Project names can be found publicly; they do not prove authenticity.",
            },
        ],
        "response_options": [
            {
                "text": "Verify the change by calling the supplier on a known number, then report",
                "is_correct": True,
                "explanation": "Confirm with the supplier using a number already in your records, and notify security.",
            },
            {
                "text": "Update the payment details and confirm receipt by reply",
                "is_correct": False,
                "explanation": "Replying confirms the change to the attacker, and your payments would be diverted.",
            },
            {
                "text": "Forward the details to the team to update them",
                "is_correct": False,
                "explanation": "Acting on the email without verification is exactly what the attacker wants.",
            },
            {
                "text": "Ask the sender to call you to confirm",
                "is_correct": False,
                "explanation": "The 'caller' would be the attacker. You must initiate verification out of band.",
            },
        ],
    },
]