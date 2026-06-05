import re
import shutil

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

shutil.copy("main.py", "main_backup_before_glow_agents.py")

new_html = r'''HTML = """
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<title>JARVIS</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#02050a;color:white;font-family:Arial,sans-serif}
#app{width:100vw;height:100vh;position:relative;background:radial-gradient(circle at center,rgba(0,255,255,.18),transparent 28%),linear-gradient(120deg,#02050a,#071624,#02050a)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(0,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(0,255,255,.06) 1px,transparent 1px);background-size:38px 38px}
.title{position:absolute;top:28px;width:100%;text-align:center;font-size:48px;letter-spacing:12px;text-shadow:0 0 30px #00eaff}
.status{position:absolute;top:92px;width:100%;text-align:center;color:#8ffaff;font-size:18px}
.brain{position:absolute;left:50%;top:43%;transform:translate(-50%,-50%);width:390px;height:490px;border-radius:45%;background:radial-gradient(circle,rgba(0,234,255,.28),transparent 65%);filter:drop-shadow(0 0 40px #00eaff);z-index:5}
.brain:before{content:"";position:absolute;inset:34px;border-radius:45%;border:1px solid rgba(0,255,255,.5);box-shadow:0 0 55px #00eaff inset}
.eye{position:absolute;top:195px;width:70px;height:20px;background:#eaffff;border-radius:50%;box-shadow:0 0 28px #00eaff}
.eye.left{left:95px}.eye.right{right:95px}
.mouth{position:absolute;left:50%;bottom:110px;transform:translateX(-50%);width:140px;height:22px;border-bottom:3px solid #eaffff;box-shadow:0 0 18px #00eaff}
.agent{position:absolute;width:190px;padding:14px;border:1px solid rgba(0,234,255,.35);background:rgba(0,20,35,.55);border-radius:18px;text-align:center;opacity:.35;transition:.35s;z-index:6}
.agent.active{opacity:1;transform:scale(1.08);box-shadow:0 0 35px #00eaff,0 0 70px rgba(0,234,255,.35);border-color:#eaffff}
.agent small{color:#8ffaff}
svg#wires{position:absolute;inset:0;width:100vw;height:100vh;z-index:2;pointer-events:none}
.wire{stroke:rgba(0,234,255,.18);stroke-width:3;fill:none}
.wire.active{stroke:#eaffff;filter:drop-shadow(0 0 10px #00eaff);stroke-dasharray:1200;stroke-dashoffset:1200;animation:charge 700ms forwards}
@keyframes charge{to{stroke-dashoffset:0}}
.spark{position:absolute;width:22px;height:22px;border-radius:50%;background:#fff;box-shadow:0 0 30px #00eaff,0 0 80px #00eaff;display:none;z-index:20}
#tasks{position:absolute;left:40px;right:40px;bottom:30px;height:150px;background:rgba(0,0,0,.5);border:1px solid rgba(0,234,255,.4);border-radius:18px;padding:16px;overflow:auto;font-size:15px;z-index:8}
#chat{position:absolute;left:50%;bottom:195px;transform:translateX(-50%);width:620px;display:flex;gap:10px;z-index:9}
#text{flex:1;padding:14px;border-radius:14px;border:1px solid #00eaff;background:rgba(0,0,0,.45);color:white;font-size:16px}
button{padding:14px 22px;border-radius:14px;border:0;background:#00eaff;color:#001014;font-weight:bold}
</style>
</head>
<body>
<div id="app">
<div class="grid"></div>
<svg id="wires"></svg>
<div class="title">JARVIS</div>
<div class="status" id="status">Waiting for wake command...</div>

<div class="brain" id="brain">
  <div class="eye left"></div><div class="eye right"></div><div class="mouth"></div>
</div>

<div id="spark" class="spark"></div>

<div class="agent" id="a0" style="left:70px;top:145px;">Trend Agent<br><small>offline</small></div>
<div class="agent" id="a1" style="right:70px;top:145px;">Script Agent<br><small>offline</small></div>
<div class="agent" id="a2" style="left:100px;top:340px;">Visual Agent<br><small>offline</small></div>
<div class="agent" id="a3" style="right:100px;top:340px;">Voice Agent<br><small>offline</small></div>
<div class="agent" id="a4" style="left:70px;top:535px;">Character Agent<br><small>offline</small></div>
<div class="agent" id="a5" style="right:70px;top:535px;">Video Agent<br><small>offline</small></div>
<div class="agent" id="a6" style="left:330px;top:675px;">Analytics Agent<br><small>standby</small></div>
<div class="agent" id="a7" style="right:330px;top:675px;">Learning Agent<br><small>standby</small></div>

<div id="chat"><input id="text" placeholder="Skriv till Jarvis..."><button onclick="send()">Skicka</button></div>
<div id="tasks">Agent log waiting...</div>
</div>

<script>
const agents=[...document.querySelectorAll(".agent")];
const brain=document.getElementById("brain");
const wires=document.getElementById("wires");
const spark=document.getElementById("spark");
const statusBox=document.getElementById("status");
let lastCount=0;
let started=false;

function pt(el){const r=el.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2}}
function drawWires(){
  wires.innerHTML="";
  const b=pt(brain);
  agents.forEach((a,i)=>{
    const p=pt(a);
    const line=document.createElementNS("http://www.w3.org/2000/svg","path");
    const midX=(b.x+p.x)/2;
    line.setAttribute("d",`M ${b.x} ${b.y} C ${midX} ${b.y}, ${midX} ${p.y}, ${p.x} ${p.y}`);
    line.setAttribute("class","wire");
    line.setAttribute("id","w"+i);
    wires.appendChild(line);
  });
}
window.addEventListener("resize",drawWires);
setTimeout(drawWires,300);

function activateAgent(i,delay=0){
  setTimeout(()=>{
    drawWires();
    const wire=document.getElementById("w"+i);
    if(wire) wire.classList.add("active");

    const b=pt(brain), p=pt(agents[i]);
    spark.style.display="block";
    spark.animate([{left:b.x+"px",top:b.y+"px"},{left:p.x+"px",top:p.y+"px"}],
      {duration:650,fill:"forwards",easing:"ease-out"});

    setTimeout(()=>{
      agents[i].classList.add("active");
      agents[i].querySelector("small").innerText="online";
    },620);
  },delay);
}

function startFakeSequence(){
  if(started)return;
  started=true;
  statusBox.innerText="Agent network charging...";
  agents.forEach((a,i)=>activateAgent(i,i*550));
}

function agentIndex(name){
  return {"Trend Agent":0,"Script Agent":1,"Visual Agent":2,"Voice Agent":3,"Character Agent":4,"Video Agent":5,"Analytics Agent":6,"Learning Agent":7}[name];
}

async function poll(){
  try{
    const res=await fetch("/agent-tasks?x="+Date.now());
    const data=await res.json();

    if(data.length>0 && !started) startFakeSequence();

    if(data.length>lastCount){
      data.slice(lastCount).forEach(t=>{
        const i=agentIndex(t.agent);
        if(i!==undefined) activateAgent(i,0);
        if(t.agent==="Jarvis") statusBox.innerText=t.detail;
      });
      lastCount=data.length;
    }

    document.getElementById("tasks").innerHTML=data.slice(-10).map(t=>
      `<div>[${t.time}] <b>${t.agent}</b> — ${t.status}: ${t.detail}</div>`
    ).join("");
  }catch(e){}
}

async function send(){
  const input=document.getElementById("text");
  const text=input.value;
  input.value="";
  if(text.toLowerCase().includes("starta agenter")) startFakeSequence();
  await fetch("/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
}
document.getElementById("text").addEventListener("keydown",e=>{if(e.key==="Enter")send()});
setInterval(poll,800);
poll();
</script>
</body>
</html>
"""'''

code = re.sub(r'HTML\s*=\s*("""|\'\'\')[\s\S]*?\1', new_html, code, count=1)

with open("main.py","w",encoding="utf-8") as f:
    f.write(code)

print("Klar! Ny fullscreen UI + ljustrådar installerad.")