"""Seed modules 1-4 for PhishAware. Educational, defensive content only."""

MODULES_A = [
    {
        "title": "What Is Phishing?",
        "category": "Phishing Fundamentals",
        "difficulty": "beginner",
        "estimated_minutes": 10,
        "featured": True,
        "order": 1,
        "description": (
            "A friendly introduction to phishing: what it is, how it works, "
            "and why attackers rely on it more than technical hacking."
        ),
        "lessons": [
            {
                "title": "Defining Phishing",
                "content": (
                    "Phishing is a type of social engineering attack in which a "
                    "criminal impersonates a trusted person or organization to "
                    "trick you into revealing sensitive information, clicking a "
                    "malicious link, opening an infected attachment, or moving money.\n\n"
                    "The word comes from the idea of 'fishing' for victims using "
                    "'bait' - a believable message that looks legitimate enough to "
                    "catch your attention and your trust.\n\n"
                    "Phishing is usually delivered by email, but attackers also use "
                    "text messages (smishing), phone calls (vishing), fake websites, "
                    "and even messages inside apps and collaboration tools."
                ),
            },
            {
                "title": "The Anatomy of a Phishing Attack",
                "content": (
                    "A typical phishing attack has four phases:\n\n"
                    "1. Bait preparation - the attacker copies real branding and "
                    "wording from a trusted company (your bank, an online store, your employer).\n\n"
                    "2. Delivery - the fake message is sent, often mass-distributed, "
                    "with a hook such as 'your account was suspended' or 'claim your reward'.\n\n"
                    "3. Action - the victim clicks a link, opens an attachment, or "
                    "answers with personal information.\n\n"
                    "4. Exploitation - the attacker uses what was collected to "
                    "steal money, gain access, or spread further attacks.\n\n"
                    "Your defense is to break the chain at the action step by "
                    "stopping, thinking, and verifying before clicking."
                ),
            },
            {
                "title": "Why Phishing Works",
                "content": (
                    "Phishing works because it targets human psychology, not "
                    "technology. Attackers exploit:\n\n"
                    "- Authority: messages that appear to come from your boss, your bank, or the police.\n"
                    "- Urgency: 'act within 24 hours or your account will be closed.'\n"
                    "- Fear and greed: threats of loss or promises of reward.\n"
                    "- Curiosity: subject lines such as 'unusual sign-in attempt' or 'new message'.\n"
                    "- Trust: attackers imitate people and brands you already trust.\n\n"
                    "The most important skill you can build is a healthy dose of "
                    "skepticism combined with calm verification."
                ),
            },
            {
                "title": "Real-World Impact",
                "content": (
                    "Phishing has real consequences. It is a leading cause of "
                    "data breaches and ransomware infections. Typical outcomes include:\n\n"
                    "- Compromised email and social media accounts\n"
                    "- Stolen financial information and identity theft\n"
                    "- Ransomware locking an entire organization's files\n"
                    "- Business Email Compromise (BEC) leading to large wire-transfer fraud\n\n"
                    "By learning to recognize phishing, you protect not only your own "
                    "accounts but also your employer, your family, and everyone "
                    "whose data you hold."
                ),
            },
        ],
    },
    {
        "title": "How Phishing Emails Work",
        "category": "Email Phishing",
        "difficulty": "beginner",
        "estimated_minutes": 12,
        "featured": True,
        "order": 2,
        "description": (
            "Dive into email-based attacks and learn the specific red flags that "
            "separate a real message from a fake one."
        ),
        "lessons": [
            {
                "title": "Email Spoofing Basics",
                "content": (
                    "Spoofing means making a message appear to come from someone "
                    "it does not. Attackers can fake the display name of a sender "
                    "('your CEO') while the actual email address is something "
                    "completely different, like an account at a free webmail provider.\n\n"
                    "Always check the real email address behind the display name. "
                    "In most email clients you can hover over the sender to reveal it.\n\n"
                    "Also check the domain: support@microsoft-example.com is not "
                    "the same as support@microsoft.com."
                ),
            },
            {
                "title": "Common Email Red Flags",
                "content": (
                    "Here are the most common clues that an email is phishing:\n\n"
                    "- The sender address does not match the company it claims to be.\n"
                    "- The greeting is generic: 'Dear Customer' instead of your name.\n"
                    "- The message creates urgency or threatens a consequence.\n"
                    "- It asks you to click a link or open an attachment you were not expecting.\n"
                    "- The writing has unusual spelling or grammar mistakes.\n"
                    "- It asks for information the real company would already have.\n\n"
                    "One red flag alone can be a false alarm. Two or more together "
                    "are a strong signal to stop and verify."
                ),
            },
            {
                "title": "Links and Attachments",
                "content": (
                    "Before clicking a link, hover over it (without clicking) and "
                    "inspect the real destination in the status bar. A link whose "
                    "visible text says 'https://secure-bank.com/login' might actually "
                    "point to an unrelated domain.\n\n"
                    "Attachments are equally dangerous. Files with extensions such "
                    "as .exe, .scr, .js, or .docm can carry malware. Even office "
                    "documents can contain macros that infect your computer.\n\n"
                    "Rule of thumb: never open an unexpected attachment, especially "
                    "from an address you cannot fully verify."
                ),
            },
            {
                "title": "Urgency and Fear Tactics",
                "content": (
                    "Attackers create false urgency to bypass your careful thinking. "
                    "Messages that say 'respond immediately', 'your account will be "
                    "closed', or 'you have 1 hour' are pressuring you to act without "
                    "verifying.\n\n"
                    "Legitimate companies rarely threaten account closure in an email "
                    "with a link to fix it. When you feel rushed, that is exactly the "
                    "moment to slow down.\n\n"
                    "Pause, breathe, and verify through an official channel you "
                    "know, such as the company's app or a phone number from its "
                    "official website."
                ),
            },
        ],
    },
    {
        "title": "Recognizing Fake Websites",
        "category": "Fake Websites",
        "difficulty": "intermediate",
        "estimated_minutes": 12,
        "featured": True,
        "order": 3,
        "description": (
            "Learn to inspect URLs and page details so you can spot a fraudulent "
            "website before you ever enter a password."
        ),
        "lessons": [
            {
                "title": "Reading a URL Correctly",
                "content": (
                    "The most important part of a URL is the domain, which sits "
                    "between the protocol and the first single slash. In "
                    "https://example.com/login, the domain is example.com.\n\n"
                    "Attackers build lookalike domains that are easy to misread:\n\n"
                    "- paypal.com is not paypal-security.com or paypa1.com (digit one)\n"
                    "- microsoft.com is not microsoft-login.com\n"
                    "- a long, confusing chain of words often hides the real site\n\n"
                    "Read the domain slowly, character by character, before you type "
                    "anything."
                ),
            },
            {
                "title": "HTTPS Is Not Enough",
                "content": (
                    "The padlock icon means the connection is encrypted, but it "
                    "does not mean the website is trustworthy. Attackers can buy "
                    "SSL certificates for their fake sites, so a padlock on a "
                    "lookalike domain proves nothing.\n\n"
                    "What matters is which domain is showing the padlock. "
                    "https://secure-login.example.net with a padlock is still a "
                    "fake site if you meant to visit example.com.\n\n"
                    "Treat the padlock as the floor, not the ceiling, of your trust."
                ),
            },
            {
                "title": "Lookalike and Typosquatted Domains",
                "content": (
                    "Typosquatting registers misspelled versions of popular domains "
                    "(gnail.com, facebok.com) hoping you will make a typo. Punycode "
                    "attacks use lookalike characters from other alphabets.\n\n"
                    "If the domain does not match the exact official address, do not "
                    "enter your credentials. Bookmark the real sites you use and "
                    "navigate from your bookmark rather than from links in messages."
                ),
            },
            {
                "title": "Visual Clues on Fake Sites",
                "content": (
                    "Fake sites often copy a real logo but get the details wrong:\n\n"
                    "- Low-resolution or stretched images\n"
                    "- Wrong colors or fonts compared with the real brand\n"
                    "- Missing pages, broken links, or unusual layouts\n"
                    "- Urgent warnings: 'Your account is compromised, sign in now'\n"
                    "- Requests for information a real site would never ask on that page\n\n"
                    "When in doubt, close the tab and navigate to the official "
                    "website yourself."
                ),
            },
        ],
    },
    {
        "title": "Social Engineering Tactics",
        "category": "Social Engineering",
        "difficulty": "intermediate",
        "estimated_minutes": 12,
        "featured": False,
        "order": 4,
        "description": (
            "Social engineering targets people instead of computers. Learn the "
            "common manipulation tactics and how to defend against them."
        ),
        "lessons": [
            {
                "title": "What Is Social Engineering?",
                "content": (
                    "Social engineering is the art of manipulating people into "
                    "breaking security procedures or sharing confidential information. "
                    "It often requires no technical skill at all - just a convincing "
                    "story and a sense of urgency.\n\n"
                    "Attackers research their targets using public information from "
                    "social media, company websites, and professional networks to "
                    "make their stories believable.\n\n"
                    "Because the attacker is attacking people, the defense is also "
                    "about people: awareness, procedure, and verification."
                ),
            },
            {
                "title": "Pretexting and Impersonation",
                "content": (
                    "Pretexting is creating a believable false scenario. An attacker "
                    "pretends to be IT support, a new hire, an auditor, or a supplier "
                    "and asks for what they need: passwords, access, or a money "
                    "transfer.\n\n"
                    "Impersonation can happen by phone, email, or even in person. "
                    "Attackers may use names and details found online to sound "
                    "completely legitimate.\n\n"
                    "The defense is to verify identity through a separate, known "
                    "channel and to follow your organization's verification procedures."
                ),
            },
            {
                "title": "Baiting and Tailgating",
                "content": (
                    "Baiting offers something tempting - a free USB stick, a prize, "
                    "or a download - to get you to introduce malware or reveal data. "
                    "That 'lost' USB drive in the parking lot is classic bait.\n\n"
                    "Tailgating is following an authorized person through a secure "
                    "door. The defense is to hold the door only for people you know, "
                    "and to challenge unknown visitors politely.\n\n"
                    "If an offer seems too good to be true, it is bait."
                ),
            },
            {
                "title": "Defending Against Social Engineering",
                "content": (
                    "Your strongest defenses are simple:\n\n"
                    "- Follow policy: know your organization's verification procedures and use them.\n"
                    "- Verify out of band: call the person back on a known number.\n"
                    "- Never share passwords or one-time codes with anyone.\n"
                    "- Slow down: social engineering depends on rushing you.\n"
                    "- Report: tell your security team about suspicious requests.\n\n"
                    "Politeness is not a security control. It is fine to say 'let me "
                    "verify this before I help'."
                ),
            },
        ],
    },
]