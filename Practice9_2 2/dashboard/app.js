const names = {vibration:"Вібрація",bearing_temp:"Температура",motor_current:"Струм",rpm:"Оберти",noise_db:"Шум",pressure:"Тиск"};
const format = value => value == null ? "—" : Number(value).toLocaleString("uk-UA",{maximumFractionDigits:2});
const element = id => document.getElementById(id);
const text = (id,value) => { element(id).textContent = value; };
async function getJSON(path) {
  const response = await fetch(path, {cache:"no-store"});
  if (!response.ok) throw new Error("HTTP " + response.status);
  return response.json();
}
function renderChart(history) {
  const values = history.map(row => row.values && row.values.bearing_temp).filter(value => typeof value === "number");
  const grid = element("grid-lines");
  grid.innerHTML = [32,72,112,152,192].map(y=>`<line x1="8" y1="${y}" x2="892" y2="${y}"/>`).join("");
  if (values.length < 2) {element("chart-line").setAttribute("points","");return;}
  const min = Math.min(35,...values)-6;
  const max = Math.max(75,...values)+6;
  const points = values.map((value,index)=>`${8+(884*index)/(values.length-1)},${200-(180*(value-min))/(max-min)}`).join(" ");
  element("chart-line").setAttribute("points",points);
}
function renderAlerts(items) {
  const target = element("alerts-list");
  if (!items.length) {target.innerHTML='<div class="empty">Аномалій поки не виявлено.</div>';return;}
  target.replaceChildren(...items.slice(0,8).map(item=>{
    const row=document.createElement("div");row.className="alert-row "+(item.level==="critical"?"critical":"warning");
    const info=document.createElement("div");const strong=document.createElement("strong");strong.textContent=names[item.sensor]||item.sensor;
    const detail=document.createElement("span");detail.textContent=`${format(item.value)} · Поріг ${format(item.limit)} · ${item.action}`;
    info.append(strong,detail);const time=document.createElement("time");time.textContent=new Date(item.timestamp).toLocaleTimeString("uk-UA");row.append(info,time);return row;
  }));
}
function renderActions(items){
  const target=element("actions-list");
  if(!items.length){target.textContent="Ще немає виконаних команд";return;}
  target.replaceChildren(...items.slice(0,5).map(item=>{
    const row=document.createElement("div");row.className="action";
    const name=document.createElement("b");name.textContent=item.command;
    const time=document.createElement("span");time.textContent=new Date(item.timestamp).toLocaleTimeString("uk-UA");row.append(name,time);return row;
  }));
}
async function refresh(){
  text("clock",new Date().toLocaleString("uk-UA"));
  try{
    const [summary,history,alerts,actions]=await Promise.all([
      getJSON("/api/summary"),getJSON("/api/history?limit=120"),getJSON("/api/alerts"),getJSON("/api/actions")
    ]);
    text("total",format(summary.events));text("alert-count",format(summary.alerts_recent));
    text("latency",format(summary.edge_latency_ms));text("last-update",summary.last_update?"Оновлено "+new Date(summary.last_update).toLocaleTimeString("uk-UA"):"Немає вимірювань");
    text("state-text",summary.latest?summary.latest.alerts.length?"Увага":"Норма":"Очікування");
    for(const sensor of Object.keys(names))text(sensor,format(summary.latest?.values?.[sensor]));
    renderChart(history);renderAlerts(alerts);renderActions(actions);
    const state=element("status");state.className="status";state.innerHTML="<i></i> Cloud підключено";
  }catch(error){const state=element("status");state.className="status disconnected";state.innerHTML="<i></i> Cloud недоступний";text("command-message","Немає з'єднання з Cloud API");}
}
for(const button of document.querySelectorAll("[data-command]")){
  button.addEventListener("click",async()=>{
    button.disabled=true;
    try{
      const response=await fetch("/api/commands",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({command:button.dataset.command})});
      if(!response.ok)throw new Error("HTTP "+response.status);
      text("command-message","Команду "+button.dataset.command+" надіслано. Очікується підтвердження Edge.");
      setTimeout(refresh,1500);
    }catch(error){text("command-message","Помилка надсилання: "+error.message);}finally{button.disabled=false;}
  });
}
refresh();setInterval(refresh,3000);
