#!/usr/bin/env node
const readline = require('readline');
const fs = require('fs');
const path = require('path');

const INTENT_KEYWORDS = {
  battery_issue: ["battery", "drain", "draining", "dying", "overheating", "health", "charge", "charging", "hot"],
  billing_subscription: ["charged", "charge", "refund", "subscription", "billed", "bill", "payment", "card", "purchase", "renew"],
  icloud_sync: ["icloud", "sync", "syncing", "photos", "backup", "drive", "storage", "notes", "calendar"],
  hardware_defect: ["screen", "display", "flicker", "cracked", "broken", "speaker", "camera", "trackpad", "face id", "button", "loose", "port", "vibration", "haptic"],
  software_update: ["update", "ios", "updating", "verify", "verifying", "boot loop", "bricked", "restore", "error code", "patch", "install", "crashing"],
  airpods_audio: ["airpod", "airpods", "earbud", "audio", "noise cancellation", "anc", "static", "mic", "sound", "crackling", "earbuds"],
  account_security: ["apple id", "hacked", "stolen", "locked", "phishing", "unauthorized", "fraud", "password", "two-factor", "2fa"],
  general_inquiry: ["trade-in", "trade in", "esim", "transfer", "genius bar", "warranty", "store", "order", "delivery", "appointment", "family sharing", "recycling"]
};

const SUPPORT_RESPONSES = {
  battery_issue: "We're here to help get your battery performing at its best! Check your Battery Health & Usage under Settings > Battery to identify high-drain apps. For optimization tips, review our guide: https://apple.co/battery-tips. If you'd like us to run a remote diagnostic, please send us a DM with your device model.",
  billing_subscription: "We understand billing questions are top priority. You can view all active subscriptions, cancellation options, and purchase history at https://reportaproblem.apple.com. To request a refund directly, sign in with your Apple ID on that page. If you suspect an unauthorized charge, DM us so we can secure your account immediately.",
  icloud_sync: "Let's get your iCloud sync back on track! First, confirm your device is connected to reliable Wi-Fi and that you have sufficient iCloud storage under Settings > [Your Name] > iCloud. For step-by-step sync troubleshooting: https://apple.co/icloud-sync. Reach out via DM if you still see sync paused after toggling the service off and on.",
  hardware_defect: "We are sorry to hear about the issue with your hardware. You can check your AppleCare+ coverage status and book an in-person Genius Bar appointment at https://getsupport.apple.com. Our certified technicians can examine your device display and internal components safely.",
  software_update: "Let's get your update installed smoothly. Ensure you have at least 10GB of free space and your battery is above 50% or connected to power. If an update is stuck, try restarting your device or updating via your computer: https://apple.co/ios-update. DM us if your device remains in a restart loop.",
  airpods_audio: "Audio issues can disrupt your listening experience—let's fix this! Try resetting your AirPods: place both in the case, keep the lid open, and hold the setup button for 15 seconds until the status light flashes amber, then white. More troubleshooting steps: https://apple.co/airpods-reset.",
  account_security: "Account security is our highest priority. If you believe your Apple ID has been compromised or you are locked out, visit https://iforgot.apple.com to initiate recovery immediately. Please send us a private Direct Message so a senior security specialist can assist you directly.",
  general_inquiry: "Thanks for reaching out to Apple Support! You can explore trade-in estimates, order statuses, and device guides anytime at https://www.apple.com/support. If you have specific details or order numbers, send us a DM and our team will gladly take a closer look."
};

function cleanTweet(text) {
  return text
    .replace(/https?:\/\/\S+|www\.\S+/gi, '')
    .replace(/@\w+/g, '')
    .replace(/#(\w+)/g, '$1')
    .replace(/[^a-zA-Z0-9\s$%.?!]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

function classifyIntent(text) {
  const cleaned = cleanTweet(text);
  let bestIntent = "general_inquiry";
  let maxScore = 0;
  const scores = {};

  for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
    let score = 0;
    for (const kw of keywords) {
      if (cleaned.includes(kw)) score += 1;
    }
    scores[intent] = score;
    if (score > maxScore) {
      maxScore = score;
      bestIntent = intent;
    }
  }

  const total = Object.values(scores).reduce((a, b) => a + b, 0) || 1;
  const confidence = maxScore === 0 ? 0.35 : Math.round((maxScore / total) * 100) / 100;
  return { intent: bestIntent, confidence, scores };
}

function evaluateEscalation(text, intent) {
  const cleaned = cleanTweet(text);
  const reasons = [];
  let urgency = "low";
  let escalate = false;

  const highRisk = ["stolen", "hacked", "fraud", "unauthorized", "scam", "police", "legal", "bootloop", "boot loop", "bricked", "burning", "urgent", "lost phone"];
  for (const w of highRisk) {
    if (cleaned.includes(w)) {
      reasons.push(`High risk keyword detected: '${w}'`);
      escalate = true;
      urgency = "high";
      break;
    }
  }

  if (intent === "account_security") {
    reasons.push("Account security inquiry requires human verification");
    escalate = true;
    urgency = "high";
  }

  const frustration = ["ridiculous", "terrible", "worst", "unacceptable", "furious", "angry"];
  for (const w of frustration) {
    if (cleaned.includes(w)) {
      reasons.push(`Frustration sentiment detected: '${w}'`);
      escalate = true;
      if (urgency !== "high") urgency = "medium";
      break;
    }
  }

  const dollarMatch = cleaned.match(/\$(\d+(\.\d{2})?)/);
  if (dollarMatch && parseFloat(dollarMatch[1]) >= 100) {
    reasons.push(`High transaction amount ($${dollarMatch[1]})`);
    escalate = true;
    urgency = "high";
  }

  return { escalate, urgency, reasons };
}

function generateReply(text, intent, esc) {
  const base = SUPPORT_RESPONSES[intent] || SUPPORT_RESPONSES.general_inquiry;
  if (esc.escalate) {
    return `[PRIORITY ESCALATION - ${esc.urgency.toUpperCase()}] ${base}`;
  }
  return base;
}

function processTweet(text) {
  const classification = classifyIntent(text);
  const escalation = evaluateEscalation(text, classification.intent);
  const reply = generateReply(text, classification.intent, escalation);

  return {
    input: text,
    intent: classification.intent,
    confidence: classification.confidence,
    escalate: escalation.escalate,
    urgency: escalation.urgency,
    escalationReasons: escalation.reasons,
    reply
  };
}

module.exports = { processTweet, classifyIntent, evaluateEscalation, generateReply };

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length > 0) {
    const input = args.join(' ');
    console.log(JSON.stringify(processTweet(input), null, 2));
  } else {
    console.log("=== Apple Support Agent CLI ===");
    console.log("Enter a tweet to classify (or 'exit' to quit):\n");
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const promptUser = () => {
      rl.question("> ", (line) => {
        if (line.trim().toLowerCase() === 'exit') {
          rl.close();
          return;
        }
        if (line.trim()) {
          const res = processTweet(line);
          console.log("\n--- Analysis Result ---");
          console.log(`Intent:      ${res.intent} (Confidence: ${(res.confidence * 100).toFixed(0)}%)`);
          console.log(`Escalate:    ${res.escalate ? 'YES (' + res.urgency + ' urgency)' : 'NO'}`);
          if (res.escalationReasons.length > 0) {
            console.log(`Reasons:     ${res.escalationReasons.join(', ')}`);
          }
          console.log(`Apple Reply: ${res.reply}\n`);
        }
        promptUser();
      });
    };
    promptUser();
  }
}
