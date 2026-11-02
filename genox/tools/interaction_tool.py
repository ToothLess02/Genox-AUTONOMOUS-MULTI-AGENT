"""
Genox User Interaction & Confirmation Tool
Provides native human-in-the-loop verification prompts via macOS dialogs and HUD events.
"""

import subprocess
from typing import Optional
from genox.tools.base import registry

@registry.register
def ask_user_confirmation(question: str, details: str = "", default_button: str = "Yes") -> str:
    """Prompt the user for explicit confirmation before taking an action (e.g. verifying an email address,
    approving an email draft before sending, or confirming an order/purchase).
    
    Args:
        question: The main verification question (e.g. 'Is this the email: john@example.com?').
        details: Optional supporting details (e.g. 'Subject: Proposal\nBody: Hello John...').
        default_button: 'Yes' or 'No' as default selected button.
    
    Returns:
        String indicating whether user confirmed ('Confirmed: Yes') or declined ('Cancelled: No').
    """
    clean_question = question.replace('"', '\\"').replace("'", "\\'")
    clean_details = details.replace('"', '\\"').replace("'", "\\'")
    
    display_text = clean_question
    if clean_details:
        display_text = f"{clean_question}\\n\\n{clean_details}"
        
    apple_script = f'''
    display dialog "{display_text}" with title "GENOX Autopilot Confirmation" buttons {{"Cancel", "No", "Yes"}} default button "{default_button}" giving up after 120
    '''
    
    try:
        res = subprocess.run(
            ["osascript", "-e", apple_script],
            capture_output=True,
            text=True,
            timeout=130
        )
        output = res.stdout.strip()
        if "button returned:Yes" in output:
            return f"Confirmed: User clicked YES. You may proceed with the next step. Details: {details or question}"
        elif "button returned:No" in output:
            return "Denied: User clicked NO. Do NOT proceed with this action. Ask the user for corrected information or alternate instructions."
        elif "gave up:true" in output:
            return "Timeout: User did not respond within 120 seconds. Action paused."
        else:
            return "Cancelled: User dismissed the confirmation prompt. Stop execution or ask for clarification."
    except Exception as e:
        return f"Interaction Notice: User prompt dialog completed with: {str(e)}"

@registry.register
def ask_user_text_input(prompt: str, default_text: str = "") -> str:
    """Ask the user to type or provide specific input (e.g. an email address, contact name, or clarification).
    
    Args:
        prompt: The prompt label to display to the user.
        default_text: Default prefilled text in input field.
    
    Returns:
        The text entered by the user.
    """
    clean_prompt = prompt.replace('"', '\\"').replace("'", "\\'")
    clean_default = default_text.replace('"', '\\"').replace("'", "\\'")
    
    apple_script = f'''
    display dialog "{clean_prompt}" default answer "{clean_default}" with title "GENOX Input Request" buttons {{"Cancel", "OK"}} default button "OK"
    '''
    try:
        res = subprocess.run(
            ["osascript", "-e", apple_script],
            capture_output=True,
            text=True,
            timeout=130
        )
        output = res.stdout.strip()
        if "text returned:" in output:
            parts = output.split("text returned:")
            text = parts[1].strip() if len(parts) > 1 else ""
            return f"User Input: {text}"
        return "Cancelled: User cancelled input."
    except Exception as e:
        return f"Input Notice: {str(e)}"

