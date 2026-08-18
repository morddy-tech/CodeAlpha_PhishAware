"""Seed modules 5-8 for PhishAware. Educational, defensive content only."""

MODULES_B = [
    {
        "title": "Smishing and Vishing",
        "category": "Smishing & Vishing",
        "difficulty": "intermediate",
        "estimated_minutes": 10,
        "featured": False,
        "order": 5,
        "description": (
            "Phishing is not limited to email. Learn how attackers target you "
            "through text messages and phone calls."
        ),
        "lessons": [
            {
                "title": "Smishing: Phishing by Text",
                "content": (
                    "Smishing (SMS phishing) sends fraudulent text messages that "
                    "try to trick you into clicking a link, downloading an app, or "
                    "replying with personal information.\n\n"
                    "Common smishing hooks include fake delivery notifications, "
                    "bogus bank alerts, and 'you have won a prize' messages. "
                    "The link inside usually leads to a fake website or an app "
                    "that steals data.\n\n"
                    "Treat unexpected text messages the same way you treat "
                    "suspicious email: do not click, and verify with the real "
                    "organization through an official channel."
                ),
            },
            {
                "title": "Vishing: Phishing by Phone",
                "content": (
                    "Vishing (voice phishing) uses phone calls or voicemail to "
                    "extract information. Callers may claim to be from your bank, "
                    "your internet provider, or your company's IT desk.\n\n"
                    "Attackers often use caller ID spoofing, so the number you see "
                    "is not proof of who is calling. They may also sound urgent and "
                    "demand immediate action, such as 'confirm your details or your "
                    "account will be frozen'.\n\n"
                    "Never give passwords, card numbers, or one-time codes over an "
                    "unsolicited call. Hang up and call the official number yourself."
                ),
            },
            {
                "title": "MFA Code Scams",
                "content": (
                    "Multi-factor authentication (MFA) dramatically improves "
                    "security, so attackers try to defeat it. In an MFA code scam, "
                    "the attacker first obtains your password (often from an earlier "
                    "breach), then calls or messages you claiming to be support and "
                    "asks you to read back the one-time code you just received.\n\n"
                    "That code is the second factor that would let them into your "
                    "account. A real support agent will never ask for your code.\n\n"
                    "If someone asks you to read back a verification code, that is "
                    "an attack. Do not share it."
                ),
            },
            {
                "title": "Safe Phone Habits",
                "content": (
                    "Build these safe habits:\n\n"
                    "- Never confirm personal or financial details to an inbound call.\n"
                    "- Hang up and call back using the official number from a statement or website.\n"
                    "- Do not trust caller ID alone; it can be spoofed.\n"
                    "- Never share one-time passcodes, even with 'support'.\n"
                    "- Report suspicious calls to your security or IT team.\n\n"
                    "A few seconds of verification can stop an attack that takes "
                    "seconds to start but months to fix."
                ),
            },
        ],
    },
    {
        "title": "Spear Phishing and Business Email Compromise",
        "category": "Business Email Compromise",
        "difficulty": "advanced",
        "estimated_minutes": 12,
        "featured": False,
        "order": 6,
        "description": (
            "Targeted attacks are the most dangerous. Learn how attackers "
            "customize their scams against specific people and organizations."
        ),
        "lessons": [
            {
                "title": "Spear Phishing Basics",
                "content": (
                    "Spear phishing is a targeted phishing attack aimed at a "
                    "specific person or company. Instead of a mass email, the "
                    "attacker researches the target and writes a message that "
                    "references real names, projects, and events.\n\n"
                    "Because the message is personalized, it is far harder to "
                    "spot. The attacker may use details from LinkedIn, the "
                    "company website, or news articles.\n\n"
                    "For high-value targets this is called whaling. Executives, "
                    "finance staff, and anyone with privileged access are "
                    "common targets."
                ),
            },
            {
                "title": "Business Email Compromise (BEC)",
                "content": (
                    "Business Email Compromise is a scam in which attackers "
                    "impersonate a legitimate sender to trick a company into "
                    "making unauthorized payments or sharing sensitive data.\n\n"
                    "Common BEC scenarios include:\n\n"
                    "- A fake CEO email asking finance to urgently pay an invoice\n"
                    "- A supplier's account is compromised and asks to change bank details\n"
                    "- An employee's email is hijacked and used to redirect payments\n\n"
                    "BEC losses run into billions of dollars per year, and the "
                    "fraud usually succeeds because the request looks normal."
                ),
            },
            {
                "title": "Fake Invoices and Payment Diversion",
                "content": (
                    "In payment diversion fraud, an attacker pretends to be a "
                    "legitimate supplier and asks you to update their bank details "
                    "for future payments. Money you send then goes to the attacker.\n\n"
                    "The message usually arrives at a busy moment and includes "
                    "plausible references such as an invoice number or a project "
                    "name.\n\n"
                    "Any request to change payment details must be verified "
                    "through a separate channel - for example, a phone call to a "
                    "number you already have on file, not the number in the message."
                ),
            },
            {
                "title": "CEO Fraud Defense",
                "content": (
                    "CEO fraud impersonates executives to pressure employees into "
                    "quick action, usually a wire transfer or the purchase of gift "
                    "cards. The fake executive is 'too busy' to talk and demands "
                    "secrecy.\n\n"
                    "Defenses:\n\n"
                    "- Always verify unusual payment requests with the person directly, in person or by phone.\n"
                    "- Never approve payments based on email alone.\n"
                    "- Use a second-person approval for large or unusual transfers.\n"
                    "- Remember: urgent and secret is a classic fraud combination.\n\n"
                    "When in doubt, slow down and verify out of band."
                ),
            },
        ],
    },
    {
        "title": "How to Respond to a Suspicious Message",
        "category": "Incident Reporting",
        "difficulty": "beginner",
        "estimated_minutes": 10,
        "featured": True,
        "order": 7,
        "description": (
            "The exact steps to take when you suspect you have received a "
            "phishing message - or when you have already clicked."
        ),
        "lessons": [
            {
                "title": "The STOP-THINK-VERIFY Framework",
                "content": (
                    "When a message triggers even a small alarm, use this simple "
                    "framework:\n\n"
                    "STOP: Do not click, reply, open attachments, or act on pressure.\n\n"
                    "THINK: Ask 'was I expecting this? Who really sent it? Why does "
                    "it need my action right now?'\n\n"
                    "VERIFY: Contact the sender or company through an official "
                    "channel you already know, and inspect the address and links.\n\n"
                    "Most phishing fails the moment you refuse to act quickly."
                ),
            },
            {
                "title": "Verifying a Message Out of Band",
                "content": (
                    "Out-of-band verification means confirming a request through a "
                    "channel other than the one the message came from. If the email "
                    "looks like it is from your bank, call the bank using the "
                    "number on the back of your card or the official website. Do "
                    "not use a phone number included in the suspicious message.\n\n"
                    "If a colleague asks for something unusual, walk to their desk "
                    "or call them on a known number.\n\n"
                    "Verification takes one minute. Cleaning up a breach takes weeks."
                ),
            },
            {
                "title": "Reporting Suspicious Messages",
                "content": (
                    "Reporting is a key defensive action. If your organization has "
                    "a report-phishing button, use it. Otherwise forward the message "
                    "to your IT or security team or to the real company's abuse "
                    "department.\n\n"
                    "You can also report phishing to anti-abuse organisations such "
                    "as APWG (reportphishing@apwg.org) or your national CERT.\n\n"
                    "Reporting helps protect everyone, not just you. Keep the "
                    "suspicious message intact - do not delete it until the report "
                    "is complete."
                ),
            },
            {
                "title": "If You Already Clicked",
                "content": (
                    "If you clicked a link, opened an attachment, or entered "
                    "credentials on a suspicious page:\n\n"
                    "1. Do not panic, but act promptly.\n"
                    "2. Disconnect the device from the network if you suspect malware.\n"
                    "3. Change the password for the affected account, and any "
                    "account that shares that password, from a trusted device.\n"
                    "4. Enable or reset multi-factor authentication.\n"
                    "5. Report the incident to your security team right away - "
                    "they would rather hear from you than discover it later.\n\n"
                    "Speed matters. The faster you report, the more damage can be "
                    "prevented."
                ),
            },
        ],
    },
    {
        "title": "Building Strong Security Habits",
        "category": "Best Practices",
        "difficulty": "beginner",
        "estimated_minutes": 10,
        "featured": True,
        "order": 8,
        "description": (
            "Good security is a set of everyday habits. Learn the fundamentals "
            "that keep you safe across all your accounts."
        ),
        "lessons": [
            {
                "title": "Password Hygiene",
                "content": (
                    "Use a unique, strong password for every account. A long "
                    "passphrase made of several random words is both strong and "
                    "easy to remember.\n\n"
                    "A password manager creates and stores strong passwords so "
                    "you never need to reuse one. If a service is breached, a "
                    "unique password means your other accounts stay safe.\n\n"
                    "Never share passwords. If you must hand over access, most "
                    "services offer secure sharing or guest accounts instead."
                ),
            },
            {
                "title": "Multi-Factor Authentication (MFA)",
                "content": (
                    "MFA adds a second check beyond your password: a code from an "
                    "app, a hardware key, or a biometric. Even if an attacker "
                    "steals your password, they still cannot get in without the "
                    "second factor.\n\n"
                    "Prefer authenticator apps or hardware keys over SMS codes "
                    "where possible. SMS codes can be intercepted.\n\n"
                    "Enable MFA on your email, banking, and social media accounts "
                    "first - email is the master key to your digital life."
                ),
            },
            {
                "title": "Keeping Software Updated",
                "content": (
                    "Attackers exploit known weaknesses in outdated software. "
                    "Updates close those holes, so keep your operating system, "
                    "browser, apps, and devices on the latest versions.\n\n"
                    "Enable automatic updates wherever possible, and restart "
                    "when prompted.\n\n"
                    "Do not download 'updates' from pop-ups or links in messages. "
                    "Always update from the official app store or the vendor's site."
                ),
            },
            {
                "title": "A Security Mindset",
                "content": (
                    "Security is not a product you buy; it is a set of habits you "
                    "practice:\n\n"
                    "- Default to skepticism about unexpected requests.\n"
                    "- Verify before you trust.\n"
                    "- Keep personal information private online.\n"
                    "- Lock your devices and screens.\n"
                    "- Back up important data regularly.\n"
                    "- Report suspicious activity without embarrassment.\n\n"
                    "Each small habit makes you a much harder target. This is the "
                    "whole point of PhishAware: learn to detect, learn to defend."
                ),
            },
        ],
    },
]