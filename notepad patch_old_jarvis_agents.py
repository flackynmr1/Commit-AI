import os
import shutil

HTML_CANDIDATES = [
    "templates/index.html",
    "index.html",
    "static/index.html"
]

html_path = None
for p in HTML_CANDIDATES:
    if os.path.exists(p):
        html_path = p
        break

if not html_path:
    print("Hittar inte din gamla HTML. Kolla om den ligger i templates/index.html")
    raise SystemExit

shutil.copy(html_path, html_path + ".backup_agents")

agent_css_js = r'''
<style>
#agentModePanel{
  display:none;
  position:fixed;
  inset:0;
  background:radial-gradient(circle at top,#132b55,#05060c 70%);
  color:white;
  z-index:9999;
  font-family:Arial,sans-serif;
  padding:35px;
}
.agent-title{
  font-size:52px;
  text-align:center;
  letter-spacing:4px;
  text-shadow:0 0 25px #00eaff;
}
.agent-grid{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:18px;
  margin-top:35px;
}
.agent-card{
  background:rgba(255,255,255,.08);
  border:1px solid rgba(0,234,255,.45);
  border-radius:22px;
  padding:22px;
  text-align:center;
  box-shadow:0 0 22px rgba(0,234,255,.15);
}
.agent-dot{
  width:14px;
  height:14px;
  border-radius:50%;
  background:#00ff9d;
  margin:14px auto 0;
  animation:pulse 1s infinite alternate;
}
@keyframes pulse{from{transform:scale(1);opacity:.5}to{transform:scale(1.7);opacity:1}}
#agentTasks{
  margin-top:30px;
  height:260px;
  overflow:auto;
  background:rgba(0,0,0,.35);
  border-radius:20px;
  padding:20px;
  font-size:18px;
}
</style>

<div id="agentModePanel">
  <div class="agent-title">JARVIS AGENT MODE</div>
  <p style="text-align:center;">YouTube Shorts Factory Online</p>

  <div class="agent-grid">
    <div class="agent-card">Trend Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Script Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Visual Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Voice Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Character Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Video Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Analytics Agent<div class="agent-dot"></div></div>
    <div class="agent-card">Learning Agent<div class="agent-dot"></div></div>
  </div>

  <div id="agentTasks">Waiting for agents...</div>
</div>

<script>
window.showAgentMode = function(){
  document.getElementById("agentModePanel").style.display = "block";
}

window.hideAgentMode = function(){
  document.getElementById("agentModePanel").style.display = "none";
}

async function refreshAgentTasks(){
  try{
    const res = await fetch("/agent-tasks?x=" + Date.now());
    const data = await res.json();
    const box = document.getElementById("agentTasks");
    if(!box) return;
    box.innerHTML = data.slice(-12).map(t =>
      `<div>[${t.time}] <b>${t.agent}</b> — ${t.status}: ${t.detail}</div>`
    ).join("");
  }catch(e){}
}
setInterval(refreshAgentTasks,1000);
</script>
'''

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

if "agentModePanel" not in html:
    html = html.replace("</body>", agent_css_js + "\n</body>")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Klart! Patchade:", html_path)
print("Backup:", html_path + ".backup_agents")