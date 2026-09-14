"""
reply_generator.py
Contextual automated response generator following Apple Support tone,
providing actionable troubleshooting steps, links, and escalation notices.
"""

from typing import Dict, Any, Optional

SUPPORT_RESPONSES = {
    "battery_issue": (
        "We're here to help get your battery performing at its best! "
        "Check your Battery Health & Usage under Settings > Battery to identify high-drain apps. "
        "For optimization tips, review our guide: https://apple.co/battery-tips. "
        "If you'd like us to run a remote diagnostic, please send us a DM with your device model."
    ),
    "billing_subscription": (
        "We understand billing questions are top priority. "
        "You can view all active subscriptions, cancellation options, and purchase history at https://reportaproblem.apple.com. "
        "To request a refund directly, sign in with your Apple ID on that page. "
        "If you suspect an unauthorized charge, DM us so we can secure your account immediately."
    ),
    "icloud_sync": (
        "Let's get your iCloud sync back on track! "
        "First, confirm your device is connected to reliable Wi-Fi and that you have sufficient iCloud storage under Settings > [Your Name] > iCloud. "
        "For step-by-step sync troubleshooting: https://apple.co/icloud-sync. "
        "Reach out via DM if you still see sync paused after toggling the service off and on."
    ),
    "hardware_defect": (
        "We are sorry to hear about the issue with your hardware. "
        "You can check your AppleCare+ coverage status and book an in-person Genius Bar appointment at https://getsupport.apple.com. "
        "Our certified technicians can examine your device display and internal components safely."
    ),
    "software_update": (
        "Let's get your update installed smoothly. "
        "Ensure you have at least 10GB of free space and your battery is above 50% or connected to power. "
        "If an update is stuck, try restarting your device or updating via your computer: https://apple.co/ios-update. "
        "DM us if your device remains in a restart loop."
    ),
    "airpods_audio": (
        "Audio issues can disrupt your listening experience—let's fix this! "
        "Try resetting your AirPods: place both in the case, keep the lid open, and hold the setup button for 15 seconds until the status light flashes amber, then white. "
        "More troubleshooting steps: https://apple.co/airpods-reset."
    ),
    "account_security": (
        "Account security is our highest priority. "
        "If you believe your Apple ID has been compromised or you are locked out, visit https://iforgot.apple.com to initiate recovery immediately. "
        "Please send us a private Direct Message so a senior security specialist can assist you directly."
    ),
    "general_inquiry": (
        "Thanks for reaching out to Apple Support! "
        "You can explore trade-in estimates, order statuses, and device guides anytime at https://www.apple.com/support. "
        "If you have specific details or order numbers, send us a DM and our team will gladly take a closer look."
    )
}


class ReplyGenerator:
    def __init__(self):
        self.templates = SUPPORT_RESPONSES

    def generate_reply(self, text: str, intent: str, escalation_meta: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a personalized, empathetic response based on the intent and escalation flags.
        """
        base_reply = self.templates.get(intent, self.templates["general_inquiry"])

        if escalation_meta and escalation_meta.get("escalate", False):
            urgency_banner = (
                "[ESCALATED TO SENIOR SUPPORT TEAM] "
                "Your issue has been flagged for prioritized agent assistance. "
            )
            return urgency_banner + base_reply

        return base_reply
