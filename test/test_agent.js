const assert = require('assert');
const { processTweet, classifyIntent, evaluateEscalation } = require('../cli.js');

console.log("Running Apple Support Agent Test Suite...");

// 1. Test battery classification
const batteryRes = processTweet("@AppleSupport battery dying after 2 hours on iPhone 15 Pro");
assert.strictEqual(batteryRes.intent, "battery_issue", "Should classify battery issue correctly");
console.log("✔ Battery intent classification passed");

// 2. Test account security and escalation
const securityRes = processTweet("@AppleSupport someone hacked my Apple ID and changed password!");
assert.strictEqual(securityRes.intent, "account_security", "Should classify account security");
assert.strictEqual(securityRes.escalate, true, "Should escalate security issue");
assert.strictEqual(securityRes.urgency, "high", "Security issue urgency should be high");
console.log("✔ Account security classification & high-urgency escalation passed");

// 3. Test billing fraud escalation
const fraudRes = processTweet("@AppleSupport unauthorized charge of $150 on my credit card");
assert.strictEqual(fraudRes.escalate, true, "Should escalate unauthorized financial charges");
console.log("✔ Financial fraud threshold escalation passed");

// 4. Test AirPods audio issue
const airpodsRes = processTweet("@AppleSupport left AirPod has buzzing crackling sound and ANC fails");
assert.strictEqual(airpodsRes.intent, "airpods_audio", "Should classify AirPods audio defect");
console.log("✔ AirPods audio intent classification passed");

console.log("\nAll 4 test suites passed successfully! (100% assertions verified)");
