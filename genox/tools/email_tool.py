"""
Genox Email Automation Tool
Handles creating drafts, opening Gmail/Apple Mail, prefilling recipients and message bodies,
and human-in-the-loop sending verification.
"""

import subprocess
import urllib.parse
from genox.tools.base import registry

@registry.register
def compose_email_draft(to_email: str, subject: str, body: str, provider: str = "gmail") -> str:
    """Compose an email draft and open it in Gmail or Apple Mail for the user to review.
    
    Args:
        to_email: The destination email address (e.g. 'client@example.com').
        subject: The email subject line.
        body: The complete text content of the email body.
        provider: 'gmail' (opens web Gmail composer) or 'apple_mail' (opens native macOS Mail app).
    
    Returns:
        Status report and formatted draft preview for user verification.
    """
    clean_to = to_email.strip()
    clean_subj = subject.strip()
    clean_body = body.strip()
    
    if provider.lower() == "apple_mail":
        # Apple Mail via AppleScript
        subj_esc = clean_subj.replace('"', '\\"')
        body_esc = clean_body.replace('"', '\\"').replace("\n", "\\n")
        apple_script = f'''
        tell application "Mail"
            activate
            set newMsg to make new outgoing message with properties {{subject:"{subj_esc}", content:"{body_esc}", visible:true}}
            tell newMsg to make new to recipient with properties {{address:"{clean_to}"}}
        end tell
        '''
        try:
            res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                return (
                    f"Successfully created email draft in Apple Mail.\n"
                    f"To: {clean_to}\nSubject: {clean_subj}\n\nBody Preview:\n{clean_body}\n\n"
                    "Next step: Call ask_user_confirmation to ask the user to verify this draft before sending."
                )
            else:
                # Fallback to Gmail URL
                provider = "gmail"
        except Exception:
            provider = "gmail"
            
    if provider.lower() == "gmail":
        # Launch Gmail compose URL in default browser
        enc_to = urllib.parse.quote(clean_to)
        enc_subj = urllib.parse.quote(clean_subj)
        enc_body = urllib.parse.quote(clean_body)
        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={enc_to}&su={enc_subj}&body={enc_body}"
        
        subprocess.run(["open", gmail_url], capture_output=True)
        return (
            f"Opened Gmail Web Composer in your browser with prefilled draft:\n"
            f"- To: {clean_to}\n"
            f"- Subject: {clean_subj}\n"
            f"- Body:\n{clean_body}\n\n"
            "Action Required: Call ask_user_confirmation to prompt the user to verify the draft."
        )

@registry.register
def send_email_via_apple_mail(to_email: str, subject: str, body: str) -> str:
    """Send an email directly through the macOS Apple Mail client.
    ONLY call this tool AFTER the user has explicitly verified and approved the draft!
    
    Args:
        to_email: Destination recipient email.
        subject: Email subject.
        body: Email body text.
    
    Returns:
        Status message.
    """
    clean_to = to_email.strip()
    subj_esc = subject.strip().replace('"', '\\"')
    body_esc = body.strip().replace('"', '\\"').replace("\n", "\\n")
    
    apple_script = f'''
    tell application "Mail"
        set newMsg to make new outgoing message with properties {{subject:"{subj_esc}", content:"{body_esc}", visible:false}}
        tell newMsg to make new to recipient with properties {{address:"{clean_to}"}}
        send newMsg
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True, timeout=20)
        if res.returncode == 0:
            return f"Email successfully sent to '{clean_to}' via Apple Mail. Subject: '{subject}'."
        else:
            return f"Apple Mail send notice: {res.stderr.strip()}. If Mail is not configured with an active SMTP account, please instruct user to click Send in the browser Gmail tab."
    except Exception as e:
        return f"Send Error: {str(e)}"

