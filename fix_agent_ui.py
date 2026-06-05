import re
import shutil

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

shutil.copy("main.py", "main_backup_before_agent_ui_fix.py")

# 1. Lägg till route för tasks om den saknas
if '@app.route("/agent-tasks")' not in code:
    route = r'''

@app.route("/agent-tasks")
def agent_tasks():
    import json
    import os

    path = "content_factory/logs/tasks.json"

    if not os.path.exists(path):
        return jsonify([])

    try:
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])
'''
    code = code.replace('# =========================\n# START', route + '\n\n# =========================\n# START')

# 2. Gör browser-start mer fullscreen
code = code.replace(
    f'f"--app={{URL}}",',
    f'f"--app={{URL}}",\n            "--start-fullscreen",\n            "--start-maximized",'
)

# 3. Byt HTML
new_html = r'''HTML = """
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<title>JARVIS</title>
<style>
html,body{
  margin:0;
  width:100%;
  height:100%;
  overflow:hidden;
  background:#01040a;
  color:white;
  font-family:Arial,sans-serif;
}
#app{
  width:100vw;
  height:100vh;
  position:relative;
  background:
    radial-gradient(circle at center,rgba(0,234,255,.18),transparent 30%),
    linear-gradient(130deg,#01040a,#071827,#01040a);
}
.grid{
  position:absolute;
  inset:0;
  background-image:
    linear-gradient(rgba(0,234,255,.07) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,234,255,.07) 1px,transparent 1px);
  background-size:40px 40px;
}
.title{
  position:absolute;
  top:28px;
  width:100%;
  text-align:center;
  font-size:50px;
  letter-spacing:12px;
  text-shadow:0 0 30px #00eaff;
}
.status{
  position:absolute;
  top:92px;
  width:100%;
  text-align:center;
  color:#90faff;
}
.brain{
  position:absolute;
  left:50%;
  top:43%;
  transform:translate(-50%,-50%);
  width:390px;
  height:500px;
  border-radius:46%;
  background:radial-gradient(circle,rgba(0,234,255,.28),transparent 67%);
  filter:drop-shadow(0 0 45px #00eaff);
  z-index:5;
}
.brain:before{
  content:"";
  position:absolute;
  inset:34px;
  border-radius:46%;
  border:1px solid rgba(0,255,255,.5);
  box-shadow:0 0 60px #00eaff inset;
}
.eye{
  position:absolute;
  top:198px;
  width:72px;
  height:20px;
  background:#eaffff;
  border-radius:50%;
  box-shadow:0 0 30px #00eaff;
}
.eye.left{left:96px}
.eye.right{right:96px}
.mouth{
  position:absolute;
  left:50%;
  bottom:112px;
  transform:translateX(-50%);
  width:145px;
  border-bottom:3px solid #eaffff;
  box-shadow:0 0 20px #00eaff;
}
.agent{
  position:absolute;
  width:190px;
  padding:14px;
  border:1px solid rgba(0,234,255,.28);
  background:rgba(0,20,35,.55);
  border-radius:18px;
  text-align:center;
  opacity:.25;
  transition:.35s;
  z-index:6;
}
.agent.on{
  opacity:1;
  transform:scale(1.08);
  border-color:#eaffff;
  box-shadow:0 0 35px #00eaff,0 0 85px rgba(0,234,255,.45);
}
.agent small{color:#89faff}
#wires{
  position:absolute;
  inset:0;
  width:100vw;
  height:100vh;
  z-index:2;
  pointer-events:none;
}
.wire{
  stroke:rgba(0,234,255,.15);
  stroke-width:3;
  fill:none;
}
.wire.on{
  stroke:#eaffff;
  filter:drop-shadow(0 0 12px #00eaff);
  stroke-dasharray:1600;
  stroke-dashoffset:1600;
  animation:charge .8s forwards;
}
@keyframes charge{to{stroke-dashoffset:0}}
.spark{
  position:absolute;
  width:24px;
  height:24px;
  border-radius:50%;
  background:white;
  box-shadow:0 0 30px #00eaff,0 0 90px #00eaff;
  display:none;
  z-index:20;
}
#tasks{
  position:absolute;
  left:40px;
  right:40px;
  bottom:30px;
  height:155px;
  background:rgba(0,0,0,.52);
  border:1px solid rgba(0,234,255,.4);
  border-radius:18px;
  padding:16px;
  overflow:auto;
  z-index:8;
  font-size:15px;
}
#chat{
  position:absolute;
  left:50%;
  bottom:205px;
  transform:translateX(-50%);
  width:620px;
  display:flex;
  gap:10px;
  z-index:9;
}
#text{
  flex:1;
  padding:14px;
  border-radius:14px;
  border:1px solid #00eaff;
  background:rgba(0,0,0,.45);
  color:white;
}
button{
  padding:14px 22px;
  border-radius:14px;
  border:0;
  background:#00eaff;
  color:#001014;
  font-weight:bold;
}
</style>
</head>
<body>
<div id="app">
<div class="grid"></div>
<svg id="wires"></svg>

<div class="title">JARVIS</div>
<div class="status" id="status">Waiting for wake command...</div>

<div class="brain" id="brain">
  <div class="eye left"></div>
  <div class="eye right"></div>
  <div class="mouth"></div>
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

<div id="chat">
  <input id="text" placeholder="Skriv till Jarvis...">
  <button onclick="send()">Skicka</button>
</div>

<div id="tasks">Agent log waiting...</div>
</div>

<script>
const agents=[...document.querySelectorAll(".agent")];
const brain=document.getElementById("brain");
const wires=document.getElementById("wires");
const spark=document.getElementById("spark");
const statusBox=document.getElementById("status");
let sequenceStarted=false;
let lastCount=0;

function point(el){
  const r=el.getBoundingClientRect();
  return {x:r.left+r.width/2,y:r.top+r.height/2};
}

function drawWires(){
  wires.innerHTML="";
  const b=point(brain);

  agents.forEach((agent,i)=>{
    const p=point(agent);
    const path=document.createElementNS("http://www.w3.org/2000/svg","path");
    const mid=(b.x+p.x)/2;
    path.setAttribute("d",`M ${b.x} ${b.y} C ${mid} ${b.y}, ${mid} ${p.y}, ${p.x} ${p.y}`);
    path.setAttribute("class","wire");
    path.setAttribute("id","wire"+i);
    wires.appendChild(path);
  });
}

function lightAgent(i,delay){
  setTimeout(()=>{
    drawWires();

    const wire=document.getElementById("wire"+i);
    if(wire){
      wire.classList.remove("on");
      void wire.offsetWidth;
      wire.classList.add("on");
    }

    const b=point(brain);
    const p=point(agents[i]);

    spark.style.display="block";
    spark.animate(
      [{left:b.x+"px",top:b.y+"px"},{left:p.x+"px",top:p.y+"px"}],
      {duration:700,fill:"forwards",easing:"ease-out"}
    );

    setTimeout(()=>{
      agents[i].classList.add("on");
      agents[i].querySelector("small").innerText="online";
    },650);

  },delay);
}

function startAgentAnimation(){
  if(sequenceStarted) return;
  sequenceStarted=true;
  statusBox.innerText="Agent network charging...";

  agents.forEach((a)=>{
    a.classList.remove("on");
    a.querySelector("small").innerText="offline";
  });

  setTimeout(drawWires,100);

  for(let i=0;i<agents.length;i++){
    lightAgent(i,i*650);
  }

  setTimeout(()=>{
    statusBox.innerText="All agents online.";
  },agents.length*650+500);
}

async function poll(){
  try{
    const res=await fetch("/agent-tasks?x="+Date.now());
    const data=await res.json();

    if(data.length>0 && !sequenceStarted){
      startAgentAnimation();
    }

    if(data.length>lastCount){
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

  if(text.toLowerCase().includes("starta agenter")){
    startAgentAnimation();
  }

  await fetch("/ask",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({text})
  });
}

document.getElementById("text").addEventListener("keydown",e=>{
  if(e.key==="Enter") send();
});

window.addEventListener("resize",drawWires);
setTimeout(drawWires,300);
setInterval(poll,800);
poll();
</script>
</body>
</html>
"""'''

code = re.sub(r'HTML\s*=\s*("""|\'\'\')[\s\S]*?\1', new_html, code, count=1)

with open("main.py","w",encoding="utf-8") as f:
    f.write(code)

print("Fixad: agentljus + wires + fullscreen UI.")