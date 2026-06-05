import os
import shutil

html_path = "templates/index.html"

if not os.path.exists("templates"):
    os.makedirs("templates")

if os.path.exists(html_path):
    shutil.copy(html_path, html_path + ".backup_new_ai_ui")

html = r'''
<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="UTF-8">
<title>JARVIS</title>
<style>
*{box-sizing:border-box}
body{
  margin:0;
  background:#02050a;
  color:white;
  font-family:Arial, sans-serif;
  overflow:hidden;
}
#app{
  width:100vw;
  height:100vh;
  background:
    radial-gradient(circle at center, rgba(0,255,255,.12), transparent 30%),
    linear-gradient(120deg,#02050a,#06111f,#02050a);
  position:relative;
}
.grid{
  position:absolute;
  inset:0;
  background-image:
    linear-gradient(rgba(0,255,255,.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,255,.06) 1px, transparent 1px);
  background-size:40px 40px;
}
.face{
  position:absolute;
  left:50%;
  top:43%;
  transform:translate(-50%,-50%);
  width:360px;
  height:470px;
  border-radius:45%;
  background:radial-gradient(circle,#0ff3,transparent 65%);
  filter:drop-shadow(0 0 35px #00eaff);
}
.face:before{
  content:"";
  position:absolute;
  inset:35px;
  border-radius:45%;
  border:1px solid rgba(0,255,255,.45);
  box-shadow:0 0 45px #00eaff inset;
}
.eye{
  position:absolute;
  top:190px;
  width:62px;
  height:18px;
  background:#dfffff;
  box-shadow:0 0 25px #00eaff;
  border-radius:50%;
}
.eye.left{left:92px}
.eye.right{right:92px}
.mouth{
  position:absolute;
  left:50%;
  bottom:110px;
  transform:translateX(-50%);
  width:130px;
  height:18px;
  border-bottom:3px solid #eaffff;
  box-shadow:0 0 16px #00eaff;
}
.node{
  position:absolute;
  width:18px;
  height:18px;
  border-radius:50%;
  background:#10202a;
  border:2px solid #00eaff;
  box-shadow:0 0 15px #00eaff;
}
.agent{
  position:absolute;
  width:190px;
  padding:14px;
  border:1px solid rgba(0,234,255,.45);
  background:rgba(0,20,35,.65);
  border-radius:16px;
  text-align:center;
  opacity:.45;
  transition:.4s;
}
.agent.active{
  opacity:1;
  box-shadow:0 0 30px #00eaff;
  transform:scale(1.05);
}
.agent small{color:#7ffcff}
.line{
  position:absolute;
  height:2px;
  background:rgba(0,234,255,.22);
  transform-origin:left center;
}
.spark{
  position:absolute;
  width:20px;
  height:20px;
  border-radius:50%;
  background:#eaffff;
  box-shadow:0 0 25px #00eaff,0 0 55px #00eaff;
  display:none;
  z-index:10;
}
.title{
  position:absolute;
  top:35px;
  width:100%;
  text-align:center;
  font-size:42px;
  letter-spacing:8px;
  text-shadow:0 0 25px #00eaff;
}
.subtitle{
  position:absolute;
  top:90px;
  width:100%;
  text-align:center;
  color:#93f7ff;
}
#tasks{
  position:absolute;
  left:40px;
  right:40px;
  bottom:35px;
  height:170px;
  background:rgba(0,0,0,.45);
  border:1px solid rgba(0,234,255,.35);
  border-radius:18px;
  padding:18px;
  overflow:auto;
  font-size:16px;
}
.hidden{display:none}
</style>
</head>
<body>
<div id="app">
  <div class="grid"></div>

  <div class="title">JARVIS</div>
  <div class="subtitle" id="status">Waiting for wake command...</div>

  <div class="face">
    <div class="eye left"></div>
    <div class="eye right"></div>
    <div class="mouth"></div>
  </div>

  <div id="spark" class="spark"></div>

  <div class="agent" id="a0" style="left:80px;top:170px;">Trend Agent<br><small>offline</small></div>
  <div class="agent" id="a1" style="right:80px;top:170px;">Script Agent<br><small>offline</small></div>
  <div class="agent" id="a2" style="left:130px;top:360px;">Visual Agent<br><small>offline</small></div>
  <div class="agent" id="a3" style="right:130px;top:360px;">Voice Agent<br><small>offline</small></div>
  <div class="agent" id="a4" style="left:80px;top:550px;">Character Agent<br><small>offline</small></div>
  <div class="agent" id="a5" style="right:80px;top:550px;">Video Agent<br><small>offline</small></div>
  <div class="agent" id="a6" style="left:370px;top:690px;">Analytics Agent<br><small>standby</small></div>
  <div class="agent" id="a7" style="right:370px;top:690px;">Learning Agent<br><small>standby</small></div>

  <div id="tasks">Agent log waiting...</div>
</div>

<script>
const agents=[...document.querySelectorAll(".agent")];
const spark=document.getElementById("spark");
const statusBox=document.getElementById("status");
let lastCount=0;

function center(el){
  const r=el.getBoundingClientRect();
  return {x:r.left+r.width/2,y:r.top+r.height/2}
}

function activateAgent(i){
  if(!agents[i])return;
  spark.style.display="block";
  const face={x:window.innerWidth/2,y:window.innerHeight/2};
  const target=center(agents[i]);
  spark.animate([
    {left:face.x+"px",top:face.y+"px"},
    {left:target.x+"px",top:target.y+"px"}
  ],{duration:500,fill:"forwards",easing:"ease-out"});
  setTimeout(()=>{
    agents[i].classList.add("active");
    agents[i].querySelector("small").innerText="online";
  },450);
}

function agentIndex(name){
  const map={
    "Trend Agent":0,
    "Script Agent":1,
    "Visual Agent":2,
    "Voice Agent":3,
    "Character Agent":4,
    "Video Agent":5,
    "Analytics Agent":6,
    "Learning Agent":7
  };
  return map[name];
}

async function poll(){
  try{
    const res=await fetch("/agent-tasks?x="+Date.now());
    const data=await res.json();

    if(data.length>lastCount){
      const fresh=data.slice(lastCount);
      fresh.forEach(t=>{
        const i=agentIndex(t.agent);
        if(i!==undefined) activateAgent(i);
        if(t.agent==="Jarvis") statusBox.innerText=t.detail;
      });
      lastCount=data.length;
    }

    document.getElementById("tasks").innerHTML=data.slice(-10).map(t=>
      `<div>[${t.time}] <b>${t.agent}</b> — ${t.status}: ${t.detail}</div>`
    ).join("");
  }catch(e){}
}
setInterval(poll,800);
poll();
</script>
</body>
</html>
'''

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Ny Jarvis HTML installerad:", html_path)
print("Backup finns:", html_path + ".backup_new_ai_ui")