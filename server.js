const http = require('http');
const fs = require('fs');
const path = require('path');
const { processTweet } = require('./cli.js');

const PORT = 3000;
const resultsPath = path.join(__dirname, 'results', 'metrics.json');
const cmImgPath = path.join(__dirname, 'results', 'confusion_matrix.png');
const goldenPath = path.join(__dirname, 'data', 'golden_set.csv');

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/') {
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Apple Support Agent - Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --apple-blue: #0071e3;
      --apple-blue-hover: #0077ed;
      --text: #f0f6fc;
      --text-muted: #8b949e;
      --escalate: #f85149;
      --success: #3fb950;
      --badge-bg: #21262d;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background-color: var(--bg); color: var(--text); padding: 24px; }
    .container { max-width: 1100px; margin: 0 auto; }
    header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
    h1 { font-size: 24px; display: flex; align-items: center; gap: 10px; }
    .badge { background: var(--badge-bg); border: 1px solid var(--border); padding: 4px 10px; border-radius: 12px; font-size: 13px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
    .card h2 { font-size: 17px; margin-bottom: 16px; color: #58a6ff; }
    textarea { width: 100%; height: 110px; background: #0d1117; border: 1px solid var(--border); color: #fff; border-radius: 8px; padding: 12px; font-size: 14px; resize: vertical; }
    button { background: var(--apple-blue); color: #fff; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 12px; transition: background 0.2s; }
    button:hover { background: var(--apple-blue-hover); }
    .pill { display: inline-block; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
    .pill-red { background: rgba(248, 81, 73, 0.2); color: var(--escalate); border: 1px solid var(--escalate); }
    .pill-green { background: rgba(63, 185, 80, 0.2); color: var(--success); border: 1px solid var(--success); }
    .pill-blue { background: rgba(0, 113, 227, 0.2); color: #58a6ff; border: 1px solid #58a6ff; }
    .metric-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d; font-size: 14px; }
    .metric-value { font-weight: bold; color: #58a6ff; }
    .sample-btn { background: #21262d; color: #c9d1d9; border: 1px solid var(--border); padding: 5px 10px; font-size: 12px; margin: 4px; border-radius: 4px; cursor: pointer; font-weight: normal; }
    .sample-btn:hover { background: #30363d; color: #fff; }
    #replyBox { margin-top: 16px; background: #0d1117; border-left: 3px solid var(--apple-blue); padding: 12px; border-radius: 4px; font-size: 14px; line-height: 1.5; }
    .matrix-container { text-align: center; margin-top: 12px; }
    .matrix-img { max-width: 100%; height: auto; border-radius: 6px; border: 1px solid var(--border); }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1> Apple Support Intelligent Agent</h1>
      <div class="badge">Production Ready • v1.0.0</div>
    </header>

    <div class="grid">
      <!-- Live Inference Tester -->
      <div class="card">
        <h2>Live Tweet Inference & Escalation</h2>
        <div style="margin-bottom: 10px;">
          <small style="color: var(--text-muted)">Try quick presets:</small><br>
          <button type="button" class="sample-btn" onclick="setTweet('@AppleSupport battery dying after 2 hours on iPhone 15 Pro, overheating!')">Battery Drain</button>
          <button type="button" class="sample-btn" onclick="setTweet('@AppleSupport Someone hacked my Apple ID and charged $450 in gift cards! URGENT!')">Hacked / Urgent</button>
          <button type="button" class="sample-btn" onclick="setTweet('@AppleSupport Can I trade in my cracked iPad Air in store?')">Trade-In Query</button>
        </div>
        <textarea id="tweetInput" placeholder="Enter an inbound customer tweet...">@AppleSupport my iPhone 14 Pro battery is dying so quickly after the new iOS update! From 100% to 20% in 3 hours!</textarea>
        <button onclick="analyzeTweet()">Classify & Generate Response</button>

        <div id="outputArea" style="margin-top: 20px; display: none;">
          <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px;">
            <span id="intentPill" class="pill pill-blue">Intent</span>
            <span id="escalatePill" class="pill">Escalation</span>
            <span id="confBadge" style="font-size: 13px; color: var(--text-muted);">Confidence: 95%</span>
          </div>
          <div id="reasonsDiv" style="font-size: 13px; color: var(--escalate); margin-bottom: 8px;"></div>
          <div style="font-weight: 600; font-size: 13px; margin-top: 10px; color: var(--text-muted);">GENERATED APPLE SUPPORT RESPONSE:</div>
          <div id="replyBox"></div>
        </div>
      </div>

      <!-- Evaluation Metrics & Confusion Matrix -->
      <div class="card">
        <h2>Benchmark Metrics (Golden Set: 200 items)</h2>
        <div class="metric-row"><span>Intent Accuracy</span><span class="metric-value" id="mAcc">77.50%</span></div>
        <div class="metric-row"><span>Intent Macro Precision</span><span class="metric-value" id="mPrec">86.73%</span></div>
        <div class="metric-row"><span>Intent Macro Recall</span><span class="metric-value" id="mRec">77.50%</span></div>
        <div class="metric-row"><span>Intent Macro F1 Score</span><span class="metric-value" id="mF1">78.70%</span></div>
        <div class="metric-row"><span>Escalation Detection Accuracy</span><span class="metric-value" id="mEscAcc">79.00%</span></div>

        <h2 style="margin-top: 24px;">Classification Heatmap</h2>
        <div class="matrix-container">
          <img src="/confusion_matrix.png" class="matrix-img" alt="Confusion Matrix Heatmap">
        </div>
      </div>
    </div>
  </div>

  <script>
    function setTweet(t) {
      document.getElementById('tweetInput').value = t;
      analyzeTweet();
    }

    async function analyzeTweet() {
      const text = document.getElementById('tweetInput').value;
      if (!text.trim()) return;

      const res = await fetch('/api/classify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();

      document.getElementById('outputArea').style.display = 'block';
      document.getElementById('intentPill').innerText = data.intent;
      document.getElementById('confBadge').innerText = 'Confidence: ' + (data.confidence * 100).toFixed(0) + '%';
      
      const escPill = document.getElementById('escalatePill');
      if (data.escalate) {
        escPill.className = 'pill pill-red';
        escPill.innerText = 'ESCALATE (' + data.urgency.toUpperCase() + ')';
      } else {
        escPill.className = 'pill pill-green';
        escPill.innerText = 'AUTO-RESOLVE';
      }

      const reasonsDiv = document.getElementById('reasonsDiv');
      if (data.escalationReasons && data.escalationReasons.length > 0) {
        reasonsDiv.innerText = '⚠ ' + data.escalationReasons.join(' | ');
      } else {
        reasonsDiv.innerText = '';
      }

      document.getElementById('replyBox').innerText = data.reply;
    }
  </script>
</body>
</html>`;
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
  } else if (req.method === 'GET' && req.url === '/confusion_matrix.png') {
    if (fs.existsSync(cmImgPath)) {
      const img = fs.readFileSync(cmImgPath);
      res.writeHead(200, { 'Content-Type': 'image/png' });
      res.end(img);
    } else {
      res.writeHead(404);
      res.end();
    }
  } else if (req.method === 'POST' && req.url === '/api/classify') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const parsed = JSON.parse(body);
        const result = processTweet(parsed.text || '');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`Apple Support Agent dashboard is running at http://localhost:${PORT}`);
});
