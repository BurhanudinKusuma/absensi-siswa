from flask import Flask, render_template_string, request, redirect, Response, session
from werkzeug.security import check_password_hash
import psycopg2
import os
import secrets
import re
import csv
import io
from datetime import date, datetime

app = Flask(__name__)
def get_db():
    return psycopg2.connect(host="db", dbname=os.environ.get("POSTGRES_DB","absensi_db"), user=os.environ.get("POSTGRES_USER", "admin"), password=os.environ.get("POSTGRES_PASSWORD"))

HTML = """
<!DOCTYPE html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="dark light">
<title>SiCeria DARK - Nilai & Juara</title>
<script>
(function(){
  try{
    var t = localStorage.getItem('siceria-theme');
    if(!t){ t = (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) ? 'light' : 'dark'; }
    document.documentElement.setAttribute('data-theme', t);
  }catch(e){}
})();
</script>
<style>
:root{
  --bg:#f3f5fb; --bg2:#e9edf8; --surface:#ffffff; --surface2:#f2f5fb; --text:#0f172a; --muted:#64748b;
  --line:#e3e8f3; --brand:#6d5efc; --brand2:#e84fa5; --shadow:0 1px 2px rgba(15,23,42,.05),0 8px 30px rgba(15,23,42,.06);
  --ok:#16a34a; --ok-bg:#dcfce7; --ok-tx:#14532d;
  --warn:#d97706; --warn-bg:#fef3c7; --warn-tx:#78350f;
  --bad:#dc2626; --bad-bg:#fee2e2; --bad-tx:#7f1d1d;
  --neu:#64748b; --neu-bg:#e2e8f0; --neu-tx:#334155;
  --gold:#f5b50a; --radius:20px;
}
[data-theme="dark"]{
  --bg:#080c18; --bg2:#0c1122; --surface:#111729; --surface2:#171f36; --text:#e8edf8; --muted:#8a96b4;
  --line:#222b45; --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 40px rgba(0,0,0,.35);
  --ok-bg:rgba(34,197,94,.16); --ok-tx:#86efac;
  --warn-bg:rgba(245,158,11,.16); --warn-tx:#fcd34d;
  --bad-bg:rgba(239,68,68,.16); --bad-tx:#fca5a5;
  --neu-bg:rgba(148,163,184,.16); --neu-tx:#cbd5e1;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  background:var(--bg); color:var(--text); line-height:1.5; min-height:100vh;
  background-image:
    radial-gradient(900px 500px at 85% -10%, color-mix(in srgb, var(--brand) 16%, transparent), transparent 60%),
    radial-gradient(700px 400px at -5% 10%, color-mix(in srgb, var(--brand2) 10%, transparent), transparent 60%);
  background-attachment:fixed;
}
button,input,select{font:inherit;color:inherit}
.muted{color:var(--muted)}
.small{font-size:.8rem}

/* ===== Layout ===== */
.app{display:grid;grid-template-columns:264px minmax(0,1fr);min-height:100vh}
.sidebar{
  position:sticky;top:0;height:100vh;padding:22px 16px;display:flex;flex-direction:column;gap:22px;
  background:color-mix(in srgb, var(--surface) 80%, transparent);
  backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-right:1px solid var(--line);
}
.brand{display:flex;align-items:center;gap:12px;padding:4px 8px}
.logo{
  width:44px;height:44px;border-radius:14px;display:grid;place-items:center;font-size:22px;flex-shrink:0;
  background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 8px 24px color-mix(in srgb, var(--brand) 50%, transparent);
}
.brand-name{font-weight:800;font-size:1.1rem;letter-spacing:-.01em;display:flex;align-items:center;gap:8px}
.tag{font-size:.62rem;font-weight:800;letter-spacing:.08em;padding:3px 8px;border-radius:999px;color:#fff;background:linear-gradient(90deg,var(--brand),var(--brand2))}
.nav{display:flex;flex-direction:column;gap:4px}
.nav a{
  display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:12px;color:var(--muted);
  text-decoration:none;font-weight:600;font-size:.93rem;transition:background .2s,color .2s;
}
.nav a:hover{background:var(--surface2);color:var(--text)}
.nav a.active{background:color-mix(in srgb, var(--brand) 14%, transparent);color:var(--brand)}
[data-theme="dark"] .nav a.active{color:#b4abff}
.nav .ico{font-size:1.1rem;width:24px;text-align:center}
.side-foot{margin-top:auto;display:flex;flex-direction:column;gap:12px}
.clock-card{background:var(--surface2);border:1px solid var(--line);border-radius:16px;padding:14px}
.clock-card b{display:block;font-size:1.4rem;letter-spacing:-.02em}
.theme-btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;cursor:pointer;
  background:var(--surface2);border:1px solid var(--line);border-radius:12px;padding:10px 14px;font-weight:600;font-size:.88rem;
  transition:transform .15s,border-color .2s;
}
.theme-btn:hover{border-color:var(--brand)}
.theme-btn:active{transform:scale(.97)}

.main{padding:28px clamp(16px,3vw,40px) 48px;min-width:0}
.mobilebar{display:none}
.bottomnav{display:none}
.wrap{max-width:1280px;margin:0 auto}

/* ===== Hero ===== */
.hero{
  position:relative;overflow:hidden;border-radius:28px;padding:clamp(22px,3.5vw,38px);color:#fff;
  background:linear-gradient(125deg,#3b1d9c 0%,#6d3df0 45%,#d6409f 100%);
  box-shadow:0 20px 60px color-mix(in srgb, var(--brand) 35%, transparent);
  display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:center;
  animation:rise .6s cubic-bezier(.2,.8,.2,1) both;
}
.hero::before,.hero::after{content:"";position:absolute;border-radius:50%;pointer-events:none}
.hero::before{width:340px;height:340px;right:-80px;top:-140px;background:radial-gradient(circle,rgba(255,255,255,.28),transparent 65%)}
.hero::after{width:260px;height:260px;left:30%;bottom:-160px;background:radial-gradient(circle,rgba(255,255,255,.16),transparent 65%)}
.hero > *{position:relative;z-index:1}
.eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;opacity:.85}
.hero h1{font-size:clamp(1.7rem,4vw,2.6rem);line-height:1.12;letter-spacing:-.025em;margin:8px 0 10px;font-weight:800}
.hero p{max-width:52ch;opacity:.92;font-size:.98rem}
.pills{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.pill{
  background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.22);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  border-radius:999px;padding:8px 14px;font-size:.85rem;font-weight:700;
}
.juara{
  display:inline-flex;align-items:center;gap:10px;margin-top:14px;padding:11px 16px;border-radius:16px;
  background:rgba(8,10,24,.55);border:1px solid rgba(250,204,21,.65);color:#fde047;font-weight:800;font-size:.92rem;
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
}
.hero-ring{
  width:150px;height:150px;border-radius:50%;display:grid;place-items:center;text-align:center;
  background:conic-gradient(#fde047 var(--deg,0deg), rgba(255,255,255,.18) 0);
  position:relative;
}
.hero-ring::before{content:"";position:absolute;inset:10px;border-radius:50%;background:rgba(14,10,50,.72);backdrop-filter:blur(6px)}
.hero-ring div{position:relative;line-height:1.15}
.hero-ring b{font-size:2rem;font-weight:800;display:block}
.hero-ring span{font-size:.65rem;letter-spacing:.1em;opacity:.8;font-weight:700}

/* ===== Stats ===== */
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-top:20px}
.stat{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow);
  position:relative;overflow:hidden;transition:transform .25s,border-color .25s;animation:rise .6s .08s cubic-bezier(.2,.8,.2,1) both;
}
.stat:hover{transform:translateY(-3px);border-color:color-mix(in srgb, var(--brand) 45%, var(--line))}
.stat .icon{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:1.2rem;background:color-mix(in srgb, var(--brand) 16%, transparent)}
.stat.s2 .icon{background:var(--ok-bg)} .stat.s3 .icon{background:var(--warn-bg)}
.stat h3{font-size:clamp(1.6rem,3vw,2.1rem);font-weight:800;letter-spacing:-.03em;margin-top:12px;line-height:1.1}
.stat small{color:var(--muted);font-weight:600;font-size:.82rem}
.stat.hot{background:linear-gradient(135deg,#f97316,#ea580c);border-color:transparent;color:#fff}
.stat.hot .icon{background:rgba(255,255,255,.22)} .stat.hot small{color:rgba(255,255,255,.85)}
.stat:nth-child(2){animation-delay:.14s}.stat:nth-child(3){animation-delay:.2s}.stat:nth-child(4){animation-delay:.26s}

/* ===== Cards ===== */
.grid{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:20px;margin-top:20px;align-items:start}
.col{display:flex;flex-direction:column;gap:20px;min-width:0}
.card{
  background:var(--surface);border:1px solid var(--line);border-radius:24px;padding:clamp(16px,2.2vw,26px);box-shadow:var(--shadow);
  scroll-margin-top:90px;animation:rise .6s .2s cubic-bezier(.2,.8,.2,1) both;
}
.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.card-head h2{font-size:1.15rem;font-weight:800;letter-spacing:-.015em}
.card-head p{color:var(--muted);font-size:.86rem;margin-top:2px}
.badge-top{background:var(--warn-bg);color:var(--warn-tx);padding:6px 11px;border-radius:999px;font-size:.68rem;font-weight:800;letter-spacing:.04em;white-space:nowrap}

/* ===== Forms ===== */
label.lbl{display:block;font-size:.78rem;font-weight:700;color:var(--muted);margin:0 0 6px;letter-spacing:.02em}
.field{
  width:100%;background:var(--surface2);border:1px solid var(--line);border-radius:14px;padding:12px 14px;font-size:1rem;
  outline:none;transition:border-color .2s,box-shadow .2s,background .2s;appearance:none;-webkit-appearance:none;
}
select.field{
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238a96b4' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><path d='M6 9l6 6 6-6'/></svg>");
  background-repeat:no-repeat;background-position:right 14px center;padding-right:40px;
}
.field::placeholder{color:var(--muted);opacity:.7}
.field:focus{border-color:var(--brand);box-shadow:0 0 0 4px color-mix(in srgb, var(--brand) 20%, transparent)}
.field option{background:var(--surface);color:var(--text)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stack{display:flex;flex-direction:column;gap:14px}
.btn{
  position:relative;width:100%;border:0;cursor:pointer;border-radius:14px;padding:14px 18px;font-weight:800;color:#fff;font-size:.98rem;
  background:linear-gradient(90deg,var(--brand),var(--brand2));box-shadow:0 10px 28px color-mix(in srgb, var(--brand2) 38%, transparent);
  transition:transform .15s,box-shadow .2s,filter .2s;
}
.btn:hover{filter:brightness(1.08);box-shadow:0 14px 34px color-mix(in srgb, var(--brand2) 48%, transparent)}
.btn:active{transform:scale(.985)}
.btn.loading{pointer-events:none;opacity:.8}
.btn.loading::after{
  content:"";position:absolute;right:18px;top:50%;width:16px;height:16px;margin-top:-8px;border-radius:50%;
  border:2px solid rgba(255,255,255,.4);border-top-color:#fff;animation:spin .7s linear infinite;
}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{
  border:1px solid var(--line);background:var(--surface2);color:var(--muted);border-radius:999px;padding:6px 12px;cursor:pointer;
  font-size:.8rem;font-weight:700;transition:all .15s;
}
.chip:hover{color:var(--text);border-color:var(--brand)}
.chip:active{transform:scale(.95)}
.grade{display:inline-flex;align-items:center;gap:8px;font-size:.82rem;font-weight:700;color:var(--muted);min-height:26px}
.grade i{font-style:normal;padding:3px 10px;border-radius:999px;background:var(--neu-bg);color:var(--neu-tx);transition:all .2s}
.grade i.g-a{background:var(--ok-bg);color:var(--ok-tx)} .grade i.g-b{background:color-mix(in srgb, var(--brand) 18%, transparent);color:var(--brand)}
.grade i.g-c{background:var(--warn-bg);color:var(--warn-tx)} .grade i.g-d{background:var(--bad-bg);color:var(--bad-tx)}

/* ===== User bar & Logout ===== */
.userbar{display:flex;justify-content:flex-end;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px}
.userbar .hi{font-size:.88rem;color:var(--muted);font-weight:600}
.userbar .hi b{color:var(--text)}
.btn-logout{
  cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--text);border-radius:12px;
  padding:9px 14px;font-weight:700;font-size:.82rem;transition:border-color .15s,background .15s,transform .15s;
}
.btn-logout:hover{border-color:var(--bad);background:var(--bad-bg)}
.btn-logout:active{transform:scale(.96)}

/* ===== Tanggal & Riwayat Nilai ===== */
input[type="date"].field{min-height:48px}
[data-theme="dark"] input[type="date"].field{color-scheme:dark}
.tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:16px;-webkit-overflow-scrolling:touch}
.tbl{width:100%;border-collapse:collapse;min-width:680px;font-size:.88rem}
.tbl th{
  text-align:left;font-size:.7rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
  background:var(--surface2);padding:12px 14px;white-space:nowrap;
}
.tbl td{padding:11px 14px;border-top:1px solid var(--line);vertical-align:middle}
.tbl tbody tr{transition:background .15s}
.tbl tbody tr:hover{background:var(--surface2)}
.tbl .num{text-align:right}
.tbl td.num b{color:var(--brand);font-size:1rem}
[data-theme="dark"] .tbl td.num b{color:#a5b4fc}
.tbl .tgl{white-space:nowrap}
.nrow[hidden]{display:none}

/* ===== Tambah Siswa ===== */
.addrow{display:grid;grid-template-columns:minmax(0,1fr) 150px auto;gap:12px;align-items:end}
.addrow .btn{width:auto;white-space:nowrap}
@media (max-width:700px){
  .addrow{grid-template-columns:minmax(0,1fr)}
  .addrow .btn{width:100%}
}

/* ===== Absensi ===== */
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.btn-dl{
  display:inline-flex;align-items:center;gap:6px;text-decoration:none;font-weight:700;font-size:.8rem;white-space:nowrap;
  padding:10px 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface2);color:var(--text);
  transition:border-color .15s,transform .15s,background .15s;
}
.btn-dl:hover{border-color:var(--brand);transform:translateY(-1px)}
.btn-dl:active{transform:scale(.97)}
.toolbar .filter{flex:0 0 auto;width:auto;min-width:140px}
@media (max-width:700px){.toolbar .filter{flex:1 1 100%;width:100%}}
.search{position:relative;flex:1 1 200px}
.search span{position:absolute;left:14px;top:50%;transform:translateY(-50%);opacity:.6;pointer-events:none}
.search .field{padding-left:40px}
.quick{display:flex;gap:6px;flex-wrap:wrap}
.counter{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 14px}
.cnt{font-size:.78rem;font-weight:700;padding:5px 11px;border-radius:999px}
.cnt.h{background:var(--ok-bg);color:var(--ok-tx)} .cnt.i{background:var(--warn-bg);color:var(--warn-tx)}
.cnt.s{background:var(--bad-bg);color:var(--bad-tx)} .cnt.a{background:var(--neu-bg);color:var(--neu-tx)}
.list{display:flex;flex-direction:column;gap:8px}
.stu{
  display:grid;grid-template-columns:minmax(0,1fr) minmax(250px,320px);gap:14px;align-items:center;
  padding:10px 12px;border:1px solid var(--line);background:var(--surface2);border-radius:16px;transition:border-color .2s,transform .2s;
}
.stu:hover{border-color:color-mix(in srgb, var(--brand) 40%, var(--line))}
.stu[hidden]{display:none}
.who{display:flex;align-items:center;gap:12px;min-width:0}
.avatar{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;font-weight:800;color:#fff;flex-shrink:0;font-size:.95rem}
.av0{background:linear-gradient(135deg,#6d5efc,#8b5cf6)} .av1{background:linear-gradient(135deg,#ec4899,#f43f5e)}
.av2{background:linear-gradient(135deg,#0ea5e9,#6366f1)} .av3{background:linear-gradient(135deg,#10b981,#0d9488)}
.av4{background:linear-gradient(135deg,#f59e0b,#ef4444)}
.who b{display:block;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.who .nm{flex:1;min-width:0}
.acts{display:flex;gap:6px;flex-shrink:0}
.ibtn{
  width:34px;height:34px;border-radius:10px;border:1px solid var(--line);background:var(--surface);cursor:pointer;
  display:grid;place-items:center;font-size:.9rem;transition:border-color .15s,background .15s,transform .15s;
}
.ibtn:hover{border-color:var(--brand);transform:translateY(-1px)}
.ibtn.del:hover{border-color:var(--bad);background:var(--bad-bg)}
.ibtn:active{transform:scale(.92)}
dialog.modal{
  border:1px solid var(--line);border-radius:24px;background:var(--surface);color:var(--text);padding:24px;
  width:min(440px,calc(100vw - 28px));margin:auto;box-shadow:0 30px 80px rgba(0,0,0,.5);
}
dialog.modal::backdrop{background:rgba(4,6,16,.62);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
dialog.modal[open]{animation:rise .25s cubic-bezier(.2,.8,.2,1) both}
dialog.modal h3{font-size:1.1rem;font-weight:800;letter-spacing:-.01em;margin-bottom:4px}
dialog.modal p.msg{color:var(--muted);font-size:.92rem;margin-top:6px}
.mact{display:flex;gap:10px;margin-top:20px}
.mact .btn{width:auto;flex:1}
.btn.ghost{background:var(--surface2);color:var(--text);box-shadow:none;border:1px solid var(--line)}
.btn.ghost:hover{filter:none;border-color:var(--brand);box-shadow:none}
.btn.danger{background:linear-gradient(90deg,#dc2626,#e11d48);box-shadow:0 10px 28px rgba(220,38,38,.35)}
.kelas{display:inline-block;font-size:.72rem;font-weight:700;color:var(--muted);background:var(--surface);border:1px solid var(--line);padding:1px 9px;border-radius:999px;margin-top:2px}
.seg{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:4px}
.seg label{position:relative;cursor:pointer;min-width:0}
.seg input{position:absolute;opacity:0;inset:0;width:100%;height:100%;cursor:pointer;margin:0}
.seg span{
  display:block;text-align:center;padding:8px 2px;border-radius:9px;font-size:.78rem;font-weight:700;color:var(--muted);
  transition:background .18s,color .18s,transform .15s;user-select:none;
}
.seg label:hover span{color:var(--text)}
.seg input:focus-visible + span{outline:2px solid var(--brand);outline-offset:1px}
.seg input:active + span{transform:scale(.94)}
.seg .h input:checked + span{background:var(--ok);color:#fff}
.seg .i input:checked + span{background:var(--warn);color:#fff}
.seg .s input:checked + span{background:var(--bad);color:#fff}
.seg .a input:checked + span{background:var(--neu);color:#fff}
.empty{padding:22px;text-align:center;color:var(--muted);font-size:.9rem;border:1px dashed var(--line);border-radius:14px}
.savebar{position:sticky;bottom:12px;margin-top:16px;z-index:5}
.divider{height:1px;background:var(--line);margin:22px 0 18px;border:0}
.done-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px}
.done-head h3{font-size:.98rem;font-weight:800}
.done{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:11px 4px;border-bottom:1px solid var(--line)}
.done:last-child{border-bottom:0}
.badge-hadir,.badge-izin,.badge-sakit,.badge-alpa{padding:5px 13px;border-radius:999px;font-weight:700;font-size:.76rem;white-space:nowrap}
.badge-hadir{background:var(--ok-bg);color:var(--ok-tx)}
.badge-izin{background:var(--warn-bg);color:var(--warn-tx)}
.badge-sakit{background:var(--bad-bg);color:var(--bad-tx)}
.badge-alpa{background:var(--neu-bg);color:var(--neu-tx)}

/* ===== Juara ===== */
.board{display:flex;flex-direction:column;gap:10px}
.juara-row{
  position:relative;overflow:hidden;display:flex;align-items:center;gap:14px;padding:12px 14px;border-radius:18px;
  background:var(--surface2);border:1px solid var(--line);transition:transform .2s,border-color .2s;
}
.juara-row:hover{transform:translateX(3px);border-color:color-mix(in srgb, var(--brand) 40%, var(--line))}
.juara-row.top1{border-color:color-mix(in srgb, var(--gold) 60%, var(--line));background:linear-gradient(90deg,color-mix(in srgb, var(--gold) 14%, var(--surface2)),var(--surface2))}
.medal{width:44px;height:44px;border-radius:50%;display:grid;place-items:center;font-weight:800;font-size:1.25rem;flex-shrink:0}
.m1{background:linear-gradient(135deg,#fde047,#f59e0b);color:#422006}
.m2{background:linear-gradient(135deg,#f1f5f9,#cbd5e1);color:#1e293b}
.m3{background:linear-gradient(135deg,#fed7aa,#fb923c);color:#431407}
.m4{background:var(--surface);color:var(--muted);border:1px solid var(--line);font-size:.9rem}
.info{flex:1;min-width:0}
.info b{display:block;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar{height:6px;border-radius:999px;background:var(--line);margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;width:0;border-radius:inherit;background:linear-gradient(90deg,var(--brand),var(--brand2));transition:width 1.1s cubic-bezier(.2,.8,.2,1)}
.score{text-align:right;flex-shrink:0}
.score b{display:block;font-size:1.3rem;font-weight:800;color:var(--brand);letter-spacing:-.02em;line-height:1.1}
[data-theme="dark"] .score b{color:#a5b4fc}
.score small{font-size:.6rem;font-weight:700;letter-spacing:.08em;color:var(--muted)}

.footer{text-align:center;color:var(--muted);font-size:.8rem;margin-top:30px}

/* ===== Animations ===== */
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}

/* ===== Responsive ===== */
@media (max-width:1180px){.grid{grid-template-columns:minmax(0,1fr)}}
@media (max-width:991px){
  .app{grid-template-columns:minmax(0,1fr)}
  .sidebar{display:none}
  .mobilebar{
    display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:20;padding:12px 16px;padding-top:calc(12px + env(safe-area-inset-top));
    background:color-mix(in srgb, var(--surface) 85%, transparent);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--line);
  }
  .mobilebar .logo{width:38px;height:38px;font-size:19px;border-radius:12px}
  .mobilebar .theme-btn{margin-left:auto;padding:8px 12px}
  .main{padding:18px 14px calc(96px + env(safe-area-inset-bottom))}
  .bottomnav{
    display:flex;position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:30;
    padding:6px;border-radius:22px;gap:4px;
    background:color-mix(in srgb, var(--surface) 88%, transparent);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
    border:1px solid var(--line);box-shadow:0 12px 40px rgba(0,0,0,.35);
  }
  .bottomnav a{
    flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 4px;border-radius:16px;text-decoration:none;
    color:var(--muted);font-size:.68rem;font-weight:700;transition:background .2s,color .2s;
  }
  .bottomnav a span{font-size:1.15rem;line-height:1}
  .bottomnav a.active{background:color-mix(in srgb, var(--brand) 16%, transparent);color:var(--brand)}
  [data-theme="dark"] .bottomnav a.active{color:#b4abff}
  .card{scroll-margin-top:76px}
}
@media (max-width:700px){
  .stats{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
  .hero{grid-template-columns:minmax(0,1fr);border-radius:24px}
  .hero-ring{display:none}
  .stu{grid-template-columns:minmax(0,1fr);gap:10px}
  .savebar{bottom:calc(88px + env(safe-area-inset-bottom))}
}
@media (max-width:420px){
  .row2{grid-template-columns:1fr}
  .stat{padding:14px}
}
</style>
</head>
<body>
<div class="app">

  <aside class="sidebar">
    <div class="brand">
      <div class="logo">🎓</div>
      <div>
        <div class="brand-name">SiCeria <span class="tag">DARK</span></div>
        <small class="muted">Sistem Absensi & Nilai SD</small>
      </div>
    </div>
    <nav class="nav" id="sidenav">
      <a href="#beranda" class="active"><span class="ico">🏠</span>Beranda</a>
      <a href="#absensi"><span class="ico">📝</span>Absensi</a>
      <a href="#nilai"><span class="ico">🚀</span>Input Nilai</a>
      <a href="#juara"><span class="ico">🏆</span>Papan Juara</a>
    </nav>
    <div class="side-foot">
      <div class="clock-card">
        <small class="muted" data-date>Hari ini</small>
        <b data-clock>--:--</b>
      </div>
      <button type="button" class="theme-btn" data-theme-toggle aria-label="Ganti tema"><span data-theme-icon>🌙</span><span data-theme-label>Mode Gelap</span></button>
    </div>
  </aside>

  <div style="min-width:0">
    <header class="mobilebar">
      <div class="logo">🎓</div>
      <div>
        <div class="brand-name">SiCeria <span class="tag">DARK</span></div>
        <small class="muted">Sistem Absensi & Nilai SD</small>
      </div>
      <button type="button" class="theme-btn" data-theme-toggle aria-label="Ganti tema"><span data-theme-icon>🌙</span></button>
    </header>

    <main class="main">
      <div class="wrap">

        <div class="userbar">
          <span class="hi">👤 Halo, <b>{{ guru }}</b></span>
          <form method="post" action="/logout" style="margin:0">
            <button type="submit" class="btn-logout">🚪 Logout ({{ guru }})</button>
          </form>
        </div>

        <section class="hero" id="beranda">
          <div>
            <div class="eyebrow" data-date>Dashboard Guru</div>
            <h1>Selamat Datang, Bu<br>Guru! 👋</h1>
            <p>Kelola absensi & nilai siswa dalam satu tempat. Cepat, cantik, dan otomatis kehitung!</p>
            <div class="pills">
              <span class="pill">👥 {{ total }} Siswa</span>
              <span class="pill">📝 {{ total_nilai }} Nilai Masuk</span>
            </div>
            <div class="juara">🏆 Juara: {{ juara_nama }} - {{ juara_nilai }}</div>
          </div>
          <div class="hero-ring" data-score="{{ juara_nilai }}">
            <div><b>{{ juara_nilai }}</b><span>TERTINGGI</span></div>
          </div>
        </section>

        <section class="stats" aria-label="Ringkasan">
          <div class="stat"><div class="icon">👥</div><h3 data-count>{{ total }}</h3><small>Total Siswa</small></div>
          <div class="stat s2"><div class="icon">✅</div><h3 data-count>{{ sudah|length }}</h3><small>Data Absensi</small></div>
          <div class="stat s3"><div class="icon">📝</div><h3 data-count>{{ total_nilai }}</h3><small>Total Nilai</small></div>
          <div class="stat hot"><div class="icon">📈</div><h3 data-count>{{ juara_nilai }}</h3><small>Rata-rata Tertinggi</small></div>
        </section>

        <div class="grid">

          <div class="col">
            <section class="card" id="tambah-siswa">
              <div class="card-head">
                <div><h2>➕ Tambah Siswa Baru</h2><p>Siswa baru langsung muncul di daftar absensi dan input nilai.</p></div>
              </div>
              <form method="post" action="/tambah-siswa" id="formSiswa">
                <div class="addrow">
                  <div>
                    <label class="lbl" for="nama_siswa">Nama Siswa</label>
                    <input name="nama" id="nama_siswa" class="field" required maxlength="100" placeholder="Contoh: Budi Santoso" autocomplete="off">
                  </div>
                  <div>
                    <label class="lbl" for="kelas_siswa">Kelas</label>
                    <select name="kelas" id="kelas_siswa" class="field">
                      <option value="1A">Kelas 1A</option>
                      <option value="1B">Kelas 1B</option>
                      <option value="1C">Kelas 1C</option>
                      <option value="2A">Kelas 2A</option>
                      <option value="2B">Kelas 2B</option>
                      <option value="2C">Kelas 2C</option>
                      <option value="3A">Kelas 3A</option>
                      <option value="3B">Kelas 3B</option>
                      <option value="3C">Kelas 3C</option>
                      <option value="4A">Kelas 4A</option>
                      <option value="4B">Kelas 4B</option>
                      <option value="4C">Kelas 4C</option>
                      <option value="5A" selected>Kelas 5A</option>
                      <option value="5B">Kelas 5B</option>
                      <option value="5C">Kelas 5C</option>
                      <option value="6A">Kelas 6A</option>
                      <option value="6B">Kelas 6B</option>
                      <option value="6C">Kelas 6C</option>
                    </select>
                  </div>
                  <button class="btn" type="submit">➕ Tambah Siswa</button>
                </div>
              </form>
            </section>

            <section class="card" id="absensi">
              <div class="card-head">
                <div><h2 id="judulAbsensi">📝 Absensi Hari Ini</h2><p>Pilih status tiap siswa, lalu simpan.</p></div>
              </div>

              <form method="post" action="/absen" id="formAbsen">
                <div class="toolbar">
                  <select id="filterKelas" class="field filter" aria-label="Filter per kelas">
                    <option value="">Semua Kelas</option>
                    <option value="1A">1A</option>
                    <option value="1B">1B</option>
                    <option value="1C">1C</option>
                    <option value="2A">2A</option>
                    <option value="2B">2B</option>
                    <option value="2C">2C</option>
                    <option value="3A">3A</option>
                    <option value="3B">3B</option>
                    <option value="3C">3C</option>
                    <option value="4A">4A</option>
                    <option value="4B">4B</option>
                    <option value="4C">4C</option>
                    <option value="5A">5A</option>
                    <option value="5B">5B</option>
                    <option value="5C">5C</option>
                    <option value="6A">6A</option>
                    <option value="6B">6B</option>
                    <option value="6C">6C</option>
                  </select>
                  <div class="quick">
                    <a class="btn-dl" id="dlAbsensi" href="/download-absensi" title="Unduh rekap absensi (CSV, bisa dibuka di Excel)">📥 Download Absensi (Excel/CSV)</a>
                    <a class="btn-dl" id="dlNilai" href="/download-nilai" title="Unduh rekap nilai (CSV, bisa dibuka di Excel)">📥 Download Nilai (Excel/CSV)</a>
                  </div>
                  <div class="search"><span>🔍</span><input type="search" id="cari" class="field" placeholder="Cari nama siswa..." autocomplete="off"></div>
                  <div class="quick">
                    <button type="button" class="chip" data-all="Hadir">Semua Hadir</button>
                    <button type="button" class="chip" data-all="Alpa">Reset Alpa</button>
                  </div>
                </div>
                <div class="counter" aria-live="polite">
                  <span class="cnt h">Hadir <b data-c="Hadir">0</b></span>
                  <span class="cnt i">Izin <b data-c="Izin">0</b></span>
                  <span class="cnt s">Sakit <b data-c="Sakit">0</b></span>
                  <span class="cnt a">Alpa <b data-c="Alpa">0</b></span>
                </div>

                <div class="list" id="listSiswa">
                  {% for s in siswa %}
                  <div class="stu" data-id="{{ s[0] }}" data-nama-asli="{{ s[1] }}" data-nama="{{ s[1]|lower }}" data-kelas="{{ s[2]|lower }}">
                    <div class="who">
                      <div class="avatar av{{ s[0] % 5 }}">{{ s[1][:1]|upper }}</div>
                      <div class="nm"><b>{{ s[1] }}</b><span class="kelas kls">{{ s[2] }}</span></div>
                      <div class="acts">
                        <button type="button" class="ibtn" data-edit title="Edit siswa" aria-label="Edit {{ s[1] }}">✏️</button>
                        <button type="button" class="ibtn del" data-hapus title="Hapus siswa" aria-label="Hapus {{ s[1] }}">🗑️</button>
                      </div>
                    </div>
                    <div class="seg" role="radiogroup" aria-label="Status {{ s[1] }}">
                      <label class="h"><input type="radio" name="status_{{ s[0] }}" value="Hadir" checked><span>Hadir</span></label>
                      <label class="i"><input type="radio" name="status_{{ s[0] }}" value="Izin"><span>Izin</span></label>
                      <label class="s"><input type="radio" name="status_{{ s[0] }}" value="Sakit"><span>Sakit</span></label>
                      <label class="a"><input type="radio" name="status_{{ s[0] }}" value="Alpa"><span>Alpa</span></label>
                    </div>
                  </div>
                  {% endfor %}
                </div>
                <div class="empty" id="kosong" hidden>Tidak ada siswa yang cocok.</div>

                <div class="savebar"><button class="btn" type="submit">💾 Simpan Absensi</button></div>
              </form>

              <hr class="divider">
              <div class="done-head">
                <h3>✅ Sudah Diabsen Hari Ini ({{ sudah|length }})</h3>
              </div>
              <div>
                {% for a in sudah %}
                <div class="done"><span>{{ a[0] }}</span><span class="badge-{{ a[1]|lower }}">{{ a[1] }}</span></div>
                {% endfor %}
              </div>
            </section>
          </div>

          <div class="col">
            <section class="card" id="nilai">
              <div class="card-head">
                <div><h2>🚀 Input Nilai Baru</h2><p>Masukkan nilai, langsung masuk Papan Juara.</p></div>
              </div>
              <form method="post" action="/nilai" class="stack" id="formNilai">
                <div>
                  <label class="lbl" for="siswa_id">Nama Siswa</label>
                  <select name="siswa_id" id="siswa_id" class="field">
                    {% for s in siswa %}<option value="{{ s[0] }}">{{ s[1] }} - {{ s[2] }}</option>{% endfor %}
                  </select>
                </div>
                <div class="row2">
                  <div>
                    <label class="lbl" for="jenis">Jenis</label>
                    <select name="jenis" id="jenis" class="field">
                      <option>Ulangan Harian</option><option>UTS</option><option>UAS</option><option>Tugas</option>
                    </select>
                  </div>
                  <div>
                    <label class="lbl" for="nilai_in">Nilai 0-100</label>
                    <input name="nilai" id="nilai_in" type="number" min="0" max="100" required class="field" placeholder="0-100" inputmode="numeric">
                  </div>
                </div>
                <div>
                  <div class="chips" id="chipNilai">
                    <button type="button" class="chip" data-v="60">60</button>
                    <button type="button" class="chip" data-v="70">70</button>
                    <button type="button" class="chip" data-v="80">80</button>
                    <button type="button" class="chip" data-v="90">90</button>
                    <button type="button" class="chip" data-v="100">100</button>
                  </div>
                  <div class="grade" style="margin-top:8px">Predikat: <i id="predikat">-</i></div>
                </div>
                <div>
                  <label class="lbl" for="tgl_nilai">📅 Tanggal Nilai</label>
                  <input type="date" name="tanggal" id="tgl_nilai" class="field">
                </div>
                <div>
                  <label class="lbl" for="ket">Keterangan</label>
                  <input name="ket" id="ket" class="field" placeholder="Keterangan, contoh: Ulangan 1">
                </div>
                <button class="btn" type="submit">🚀 Simpan Nilai</button>
              </form>
            </section>

            <section class="card" id="juara">
              <div class="card-head">
                <h2>🏆 Papan Juara -<br>Rata-rata Nilai</h2>
                <span class="badge-top">TOP 3 DAPAT MEDALI</span>
              </div>
              <div class="board">
                {% for j in leaderboard %}
                <div class="juara-row {% if loop.index==1 %}top1{% endif %}">
                  <div class="medal {% if loop.index==1 %}m1{% elif loop.index==2 %}m2{% elif loop.index==3 %}m3{% else %}m4{% endif %}">{% if loop.index==1 %}🥇{% elif loop.index==2 %}🥈{% elif loop.index==3 %}🥉{% else %}#{{ loop.index }}{% endif %}</div>
                  <div class="info">
                    <b>{{ j[0] }}</b>
                    <small class="muted">Kelas {{ j[1] }} • {{ j[3] }} nilai</small>
                    <div class="bar"><i data-w="{{ '%.1f'|format(j[2]) }}"></i></div>
                  </div>
                  <div class="score"><b>{{ "%.1f"|format(j[2]) }}</b><small>RATA-RATA</small></div>
                </div>
                {% else %}<div class="empty">Belum ada nilai. Input nilai di atas dulu ya Bu!</div>{% endfor %}
              </div>
            </section>
          </div>

        </div>

        <section class="card" id="riwayat-nilai" style="margin-top:20px">
          <div class="card-head">
            <div><h2>📋 Riwayat Nilai</h2><p>Mengikuti filter kelas di Absensi. Menampilkan maksimal 200 nilai terbaru.</p></div>
            <span class="cnt a"><b id="jmlNilai">0</b> data</span>
          </div>
          <div class="tbl-wrap">
            <table class="tbl">
              <thead>
                <tr><th>Nama Siswa</th><th>Kelas</th><th>Jenis Nilai</th><th class="num">Nilai</th><th>Tanggal</th><th>Keterangan</th></tr>
              </thead>
              <tbody>
                {% for r in riwayat_nilai %}
                <tr class="nrow" data-kelas="{{ r[2]|lower }}">
                  <td><b>{{ r[1] }}</b></td>
                  <td><span class="kelas kls">{{ r[2] }}</span></td>
                  <td>{{ r[3] }}</td>
                  <td class="num"><b>{{ "%.1f"|format(r[4]) if r[4] is not none else '-' }}</b></td>
                  <td class="tgl">{{ r[5].strftime('%d-%m-%Y') if r[5] else '-' }}</td>
                  <td class="muted">{{ r[6] or '-' }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          <div class="empty" id="kosongNilai" style="margin-top:12px" {% if riwayat_nilai %}hidden{% endif %}>Belum ada nilai.</div>
        </section>

        <p class="footer">SiCeria DARK 2026 • Flask + PostgreSQL + Docker</p>
      </div>
    </main>
  </div>
</div>

<nav class="bottomnav" id="bottomnav" aria-label="Navigasi bawah">
  <a href="#beranda" class="active"><span>🏠</span>Beranda</a>
  <a href="#absensi"><span>📝</span>Absensi</a>
  <a href="#nilai"><span>🚀</span>Nilai</a>
  <a href="#juara"><span>🏆</span>Juara</a>
</nav>

<dialog class="modal" id="dlgEdit" aria-labelledby="editJudul">
  <form method="post" action="/edit-siswa/0" id="formEdit" class="stack">
    <div><h3 id="editJudul">✏️ Edit Siswa</h3><p class="msg" style="margin-top:0">Ubah nama atau kelas siswa.</p></div>
    <input type="hidden" name="next" id="editNext" value="/">
    <div>
      <label class="lbl" for="editNama">Nama Siswa</label>
      <input name="nama" id="editNama" class="field" required maxlength="100" autocomplete="off">
    </div>
    <div>
      <label class="lbl" for="editKelas">Kelas</label>
      <select name="kelas" id="editKelas" class="field">
        <option value="1A">Kelas 1A</option>
        <option value="1B">Kelas 1B</option>
        <option value="1C">Kelas 1C</option>
        <option value="2A">Kelas 2A</option>
        <option value="2B">Kelas 2B</option>
        <option value="2C">Kelas 2C</option>
        <option value="3A">Kelas 3A</option>
        <option value="3B">Kelas 3B</option>
        <option value="3C">Kelas 3C</option>
        <option value="4A">Kelas 4A</option>
        <option value="4B">Kelas 4B</option>
        <option value="4C">Kelas 4C</option>
        <option value="5A" selected>Kelas 5A</option>
        <option value="5B">Kelas 5B</option>
        <option value="5C">Kelas 5C</option>
        <option value="6A">Kelas 6A</option>
        <option value="6B">Kelas 6B</option>
        <option value="6C">Kelas 6C</option>
      </select>
    </div>
    <div class="mact">
      <button type="button" class="btn ghost" data-tutup>Batal</button>
      <button type="submit" class="btn">💾 Simpan</button>
    </div>
  </form>
</dialog>

<dialog class="modal" id="dlgHapus" aria-labelledby="hapusJudul">
  <form method="post" action="/hapus-siswa/0" id="formHapus">
    <h3 id="hapusJudul">🗑️ Hapus Siswa</h3>
    <p class="msg" id="hapusTeks">Yakin hapus siswa ini? Semua absensi & nilainya juga akan terhapus.</p>
    <div class="mact">
      <button type="button" class="btn ghost" data-tutup>Batal</button>
      <button type="submit" class="btn danger">Ya, Hapus</button>
    </div>
  </form>
</dialog>

<script>
(function(){
  var $ = function(s, c){ return (c || document).querySelector(s); };
  var $$ = function(s, c){ return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---- Tema ---- */
  function applyThemeUI(){
    var t = document.documentElement.getAttribute('data-theme');
    $$('[data-theme-icon]').forEach(function(e){ e.textContent = t === 'dark' ? '🌙' : '☀️'; });
    $$('[data-theme-label]').forEach(function(e){ e.textContent = t === 'dark' ? 'Mode Gelap' : 'Mode Terang'; });
  }
  $$('[data-theme-toggle]').forEach(function(b){
    b.addEventListener('click', function(){
      var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try{ localStorage.setItem('siceria-theme', next); }catch(e){}
      applyThemeUI();
    });
  });
  applyThemeUI();

  /* ---- Tanggal & jam ---- */
  function tick(){
    var d = new Date();
    var tgl = d.toLocaleDateString('id-ID', {weekday:'long', day:'numeric', month:'long', year:'numeric'});
    $$('[data-date]').forEach(function(e){ e.textContent = tgl; });
    $$('[data-clock]').forEach(function(e){ e.textContent = d.toLocaleTimeString('id-ID', {hour:'2-digit', minute:'2-digit'}).replace('.', ':'); });
  }
  tick(); setInterval(tick, 20000);

  /* ---- Count-up angka statistik ---- */
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  $$('[data-count]').forEach(function(el){
    var raw = el.textContent.trim();
    var target = parseFloat(raw);
    if(isNaN(target) || reduce){ return; }
    var dec = (raw.split('.')[1] || '').length;
    var t0 = null, dur = 900;
    function step(ts){
      if(!t0){ t0 = ts; }
      var p = Math.min((ts - t0) / dur, 1);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * e).toFixed(dec);
      if(p < 1){ requestAnimationFrame(step); } else { el.textContent = raw; }
    }
    requestAnimationFrame(step);
  });

  /* ---- Ring nilai tertinggi ---- */
  var ring = $('.hero-ring');
  if(ring){
    var sc = parseFloat(ring.getAttribute('data-score')) || 0;
    sc = Math.max(0, Math.min(100, sc));
    setTimeout(function(){ ring.style.setProperty('--deg', (sc * 3.6) + 'deg'); }, 150);
  }

  /* ---- Bar papan juara ---- */
  setTimeout(function(){
    $$('.bar i[data-w]').forEach(function(b){
      var w = Math.max(0, Math.min(100, parseFloat(b.getAttribute('data-w')) || 0));
      b.style.width = w + '%';
    });
  }, 250);

  /* ---- Absensi: counter, cari, set semua ---- */
  var form = $('#formAbsen');
  function hitung(){
    var c = {Hadir:0, Izin:0, Sakit:0, Alpa:0};
    $$('input[type=radio]:checked', form).forEach(function(r){
      var row = r.closest('.stu');
      if(row && row.hidden){ return; }
      if(c.hasOwnProperty(r.value)){ c[r.value]++; }
    });
    Object.keys(c).forEach(function(k){
      var el = $('[data-c="' + k + '"]');
      if(el){ el.textContent = c[k]; }
    });
  }
  if(form){
    form.addEventListener('change', hitung);
    hitung();

    $$('[data-all]', form).forEach(function(btn){
      btn.addEventListener('click', function(){
        var v = btn.getAttribute('data-all');
        $$('.stu', form).forEach(function(row){
          if(row.hidden){ return; }
          var r = row.querySelector('input[value="' + v + '"]');
          if(r){ r.checked = true; }
        });
        hitung();
      });
    });

    var cari = $('#cari'), kosong = $('#kosong');
    var fk = $('#filterKelas'), judul = $('#judulAbsensi');
    var VALID = ['1A','1B','1C','2A','2B','2C','3A','3B','3C','4A','4B','4C','5A','5B','5C','6A','6B','6C'];

    /* Normalisasi kelas: "5A", "Kelas 5A", "5", kosong, dll -> kode valid. Tidak terbaca = 5A (siswa lama). */
    function normKelas(raw){
      var m = /([1-6])[^0-9A-Za-z]*([A-Ca-c])?/.exec(String(raw || ''));
      if(!m){ return '5A'; }
      var k = m[1] + (m[2] ? m[2].toUpperCase() : 'A');
      return VALID.indexOf(k) > -1 ? k : '5A';
    }
    $$('.stu', form).forEach(function(row){
      var k = normKelas(row.getAttribute('data-kelas'));
      row.setAttribute('data-k', k);
      var b = row.querySelector('.kls');
      if(b){ b.textContent = k; }
    });
    $$('.nrow').forEach(function(row){
      var k = normKelas(row.getAttribute('data-kelas'));
      row.setAttribute('data-k', k);
      var b = row.querySelector('.kls');
      if(b){ b.textContent = k; }
    });

    /* Pilihan filter: dari URL ?kelas=1A, kalau tidak ada pakai pilihan terakhir yang tersimpan */
    var sel = '';
    var qp = new URLSearchParams(window.location.search);
    if(qp.has('kelas')){
      var pv = (qp.get('kelas') || '').toUpperCase();
      sel = VALID.indexOf(pv) > -1 ? pv : '';
    } else {
      var sv = '';
      try{ sv = localStorage.getItem('siceria-kelas') || ''; }catch(e){}
      sel = VALID.indexOf(sv) > -1 ? sv : '';
    }
    function simpanFilter(){
      try{ localStorage.setItem('siceria-kelas', sel); }catch(e){}
      try{
        var u = new URL(window.location.href);
        if(sel){ u.searchParams.set('kelas', sel); } else { u.searchParams.delete('kelas'); }
        history.replaceState(null, '', u.pathname + u.search + u.hash);
      }catch(e){}
    }

    function terapkan(){
      var q = cari.value.trim().toLowerCase(), n = 0;
      $$('.stu', form).forEach(function(row){
        var k = row.getAttribute('data-k');
        var okK = !sel || k === sel;
        var okQ = !q || row.getAttribute('data-nama').indexOf(q) > -1 || k.toLowerCase().indexOf(q) > -1;
        var ok = okK && okQ;
        row.hidden = !ok;
        if(ok){ n++; }
      });
      kosong.hidden = n > 0;
      kosong.textContent = (sel && !q) ? 'Belum ada siswa di Kelas ' + sel + '.' : 'Tidak ada siswa yang cocok.';
      if(judul){ judul.textContent = '📝 Absensi Hari Ini' + (sel ? ' - Kelas ' + sel : ''); }
      var nv = 0;
      $$('.nrow').forEach(function(row){
        var ok = !sel || row.getAttribute('data-k') === sel;
        row.hidden = !ok;
        if(ok){ nv++; }
      });
      var kn = $('#kosongNilai'), jn = $('#jmlNilai');
      if(jn){ jn.textContent = nv; }
      if(kn){
        kn.hidden = nv > 0;
        kn.textContent = sel ? 'Belum ada nilai untuk Kelas ' + sel + '.' : 'Belum ada nilai.';
      }
      var qs = sel ? '?kelas=' + encodeURIComponent(sel) : '';
      var dla = $('#dlAbsensi'), dln = $('#dlNilai');
      if(dla){ dla.href = '/download-absensi' + qs; }
      if(dln){ dln.href = '/download-nilai' + qs; }
      hitung();
    }

    fk.value = sel;
    fk.addEventListener('change', function(){
      sel = fk.value;
      simpanFilter();
      terapkan();
    });
    cari.addEventListener('input', terapkan);
    simpanFilter();
    terapkan();
    cari.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ e.preventDefault(); } });

    form.addEventListener('submit', function(){
      var b = form.querySelector('.btn'); if(b){ b.classList.add('loading'); }
    });
  }

  /* ---- Edit & Hapus siswa ---- */
  var dEdit = $('#dlgEdit'), dDel = $('#dlgHapus');
  function halamanIni(){ return window.location.pathname + window.location.search; }

  function bukaEdit(row){
    var id = row.getAttribute('data-id');
    var nama = row.getAttribute('data-nama-asli') || '';
    var kelas = row.getAttribute('data-k') || '5A';
    if(!dEdit || typeof dEdit.showModal !== 'function'){
      window.location.href = '/edit-siswa/' + encodeURIComponent(id) + '?next=' + encodeURIComponent(halamanIni());
      return;
    }
    $('#formEdit').action = '/edit-siswa/' + encodeURIComponent(id);
    $('#editNama').value = nama;
    $('#editKelas').value = kelas;
    $('#editNext').value = halamanIni();
    dEdit.showModal();
    setTimeout(function(){ var n = $('#editNama'); n.focus(); n.select(); }, 60);
  }

  function bukaHapus(row){
    var id = row.getAttribute('data-id');
    var nama = row.getAttribute('data-nama-asli') || 'siswa ini';
    var teks = 'Yakin hapus ' + nama + '? Semua absensi & nilainya juga akan terhapus.';
    var url = '/hapus-siswa/' + encodeURIComponent(id);
    if(!dDel || typeof dDel.showModal !== 'function'){
      if(window.confirm(teks)){
        var f = document.createElement('form');
        f.method = 'post'; f.action = url;
        document.body.appendChild(f); f.submit();
      }
      return;
    }
    $('#hapusTeks').textContent = teks;
    $('#formHapus').action = url;
    dDel.showModal();
  }

  document.addEventListener('click', function(e){
    var t = e.target;
    if(!t || !t.closest){ return; }
    var be = t.closest('[data-edit]'), bh = t.closest('[data-hapus]');
    if(be || bh){
      var row = (be || bh).closest('.stu');
      if(row){ e.preventDefault(); if(be){ bukaEdit(row); } else { bukaHapus(row); } }
      return;
    }
    var bt = t.closest('[data-tutup]');
    if(bt){ var dlg = bt.closest('dialog'); if(dlg){ dlg.close(); } return; }
    if(t.tagName === 'DIALOG' && t.classList.contains('modal')){ t.close(); }
  });

  [dEdit, dDel].forEach(function(d){
    if(!d){ return; }
    var f = d.querySelector('form');
    if(f){
      f.addEventListener('submit', function(){
        var b = f.querySelector('button[type=submit]'); if(b){ b.classList.add('loading'); }
      });
    }
  });

  /* ---- Tambah siswa: loading state ---- */
  var fs = $('#formSiswa');
  if(fs){
    fs.addEventListener('submit', function(){
      var b = fs.querySelector('.btn'); if(b){ b.classList.add('loading'); }
    });
  }

  /* ---- Tanggal nilai: default hari ini (waktu perangkat), boleh diganti ---- */
  var tgNilai = $('#tgl_nilai');
  if(tgNilai && !tgNilai.value){
    var dn0 = new Date();
    var p2 = function(n){ return (n < 10 ? '0' : '') + n; };
    tgNilai.value = dn0.getFullYear() + '-' + p2(dn0.getMonth() + 1) + '-' + p2(dn0.getDate());
  }

  /* ---- Input nilai: chip & predikat ---- */
  var nIn = $('#nilai_in'), pred = $('#predikat');
  function predikat(){
    var v = parseFloat(nIn.value);
    pred.className = '';
    if(isNaN(v)){ pred.textContent = '-'; return; }
    if(v >= 90){ pred.textContent = 'A - Sangat Baik'; pred.className = 'g-a'; }
    else if(v >= 80){ pred.textContent = 'B - Baik'; pred.className = 'g-b'; }
    else if(v >= 70){ pred.textContent = 'C - Cukup'; pred.className = 'g-c'; }
    else { pred.textContent = 'D - Perlu Bimbingan'; pred.className = 'g-d'; }
  }
  if(nIn){
    nIn.addEventListener('input', predikat);
    $$('#chipNilai .chip').forEach(function(c){
      c.addEventListener('click', function(){ nIn.value = c.getAttribute('data-v'); predikat(); nIn.focus(); });
    });
    var fn = $('#formNilai');
    fn.addEventListener('submit', function(){
      var b = fn.querySelector('.btn'); if(b){ b.classList.add('loading'); }
    });
  }

  /* ---- Navigasi aktif saat scroll ---- */
  var ids = ['beranda','absensi','nilai','juara'];
  var links = $$('#sidenav a, #bottomnav a');
  function setActive(id){
    links.forEach(function(a){ a.classList.toggle('active', a.getAttribute('href') === '#' + id); });
  }
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(en){ if(en.isIntersecting){ setActive(en.target.id); } });
    }, {rootMargin:'-35% 0px -55% 0px'});
    ids.forEach(function(id){ var s = document.getElementById(id); if(s){ io.observe(s); } });
  }
})();
</script>
</body>
</html>
"""

# ====================== LOGIN GURU ======================
# Secret key untuk session. Acak setiap aplikasi dijalankan (semua guru perlu login ulang setelah restart).
# Kalau ingin session tetap bertahan setelah restart, set environment variable SECRET_KEY.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Akun guru: username -> HASH password (bukan password polos).
# Akun awal: username "admin" (ganti password setelah login pertama).
# Cara membuat hash baru (jalankan di terminal):
#   python -c "from werkzeug.security import generate_password_hash as g; print(g('PASSWORD_BARU', method='pbkdf2:sha256'))"
GURU = {
    "admin": "scrypt:32768:8:1$kL96Yq0gywOeMjgv$4314a910236d48c43a43ab06f19ee4b071b22c884ab7d1fff7bb3bcb5adbf27925d0d168ef31f2109086f1baa34b5e4e35d189fb8d25f622e31924424f233b8b",
}
_HASH_PALSU = GURU["admin"]

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Masuk - SiCeria</title>
<script>(function(){try{var t=localStorage.getItem('siceria-theme');if(t){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();</script>
<style>
:root{--bg:#f3f5fb;--surface:#fff;--surface2:#f2f5fb;--text:#0f172a;--muted:#64748b;--line:#e3e8f3;--brand:#6d5efc;--brand2:#e84fa5}
[data-theme="dark"]{--bg:#080c18;--surface:#111729;--surface2:#171f36;--text:#e8edf8;--muted:#8a96b4;--line:#222b45}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--text);
  min-height:100vh;display:grid;place-items:center;padding:16px;
  background-image:radial-gradient(800px 460px at 85% -10%,rgba(109,94,252,.22),transparent 60%),radial-gradient(640px 380px at -5% 10%,rgba(232,79,165,.14),transparent 60%);
}
.box{width:min(400px,100%);background:var(--surface);border:1px solid var(--line);border-radius:26px;padding:30px 26px;box-shadow:0 24px 70px rgba(0,0,0,.28)}
.brand{display:flex;flex-direction:column;align-items:center;gap:10px;margin-bottom:22px;text-align:center}
.logo{width:58px;height:58px;border-radius:18px;display:grid;place-items:center;font-size:28px;background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 10px 30px rgba(109,94,252,.5)}
.name{font-weight:800;font-size:1.4rem;letter-spacing:-.02em}
.sub{color:var(--muted);font-size:.88rem}
label{display:block;font-size:.78rem;font-weight:700;color:var(--muted);margin:14px 0 6px}
.inp{width:100%;background:var(--surface2);color:var(--text);border:1px solid var(--line);border-radius:14px;padding:13px 14px;font:inherit;font-size:1rem;outline:none;transition:border-color .2s,box-shadow .2s}
.inp:focus{border-color:var(--brand);box-shadow:0 0 0 4px rgba(109,94,252,.2)}
.pw{position:relative}
.pw .inp{padding-right:48px}
.eye{position:absolute;right:6px;top:50%;transform:translateY(-50%);width:38px;height:38px;border:0;background:transparent;cursor:pointer;font-size:1.05rem;border-radius:10px;color:var(--muted)}
.eye:hover{background:var(--line)}
.err{margin-top:16px;padding:11px 14px;border-radius:12px;background:rgba(239,68,68,.14);border:1px solid rgba(239,68,68,.45);color:#ef4444;font-weight:700;font-size:.9rem;text-align:center}
[data-theme="dark"] .err{color:#fca5a5}
.btn{width:100%;margin-top:22px;border:0;cursor:pointer;border-radius:14px;padding:14px 18px;font:inherit;font-weight:800;font-size:1rem;color:#fff;background:linear-gradient(90deg,var(--brand),var(--brand2));box-shadow:0 10px 28px rgba(232,79,165,.35);transition:transform .15s,filter .2s}
.btn:hover{filter:brightness(1.08)}
.btn:active{transform:scale(.985)}
.foot{text-align:center;color:var(--muted);font-size:.78rem;margin-top:18px}
</style>
</head>
<body>
<form class="box" method="post" action="/login" autocomplete="on">
  <div class="brand">
    <div class="logo">🎓</div>
    <div class="name">SiCeria</div>
    <div class="sub">Sistem Absensi &amp; Nilai SD — Login Guru</div>
  </div>
  <label for="username">Username</label>
  <input class="inp" id="username" name="username" type="text" required autofocus autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="Username">
  <label for="password">Password</label>
  <div class="pw">
    <input class="inp" id="password" name="password" type="password" required autocomplete="current-password" placeholder="Password">
    <button type="button" class="eye" id="eye" aria-label="Tampilkan password">👁️</button>
  </div>
  {% if error %}<div class="err" role="alert">Username / Password Salah</div>{% endif %}
  <button class="btn" type="submit">Masuk</button>
  <div class="foot">SiCeria DARK 2026</div>
</form>
<script>
(function(){
  var p=document.getElementById('password'), e=document.getElementById('eye');
  e.addEventListener('click', function(){
    var show = p.type === 'password';
    p.type = show ? 'text' : 'password';
    e.setAttribute('aria-label', show ? 'Sembunyikan password' : 'Tampilkan password');
  });
})();
</script>
</body>
</html>
"""

@app.context_processor
def _inject_guru():
    return {"guru": session.get("guru")}

@app.before_request
def _wajib_login():
    # Semua halaman wajib login, kecuali /login dan file static.
    if request.endpoint in ("login", "static"):
        return None
    if not session.get("guru"):
        return redirect("/login")
    return None

@app.after_request
def _tanpa_cache(resp):
    # Supaya setelah logout, tombol Back tidak menampilkan halaman lama dari cache.
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route('/login', methods=["GET","POST"])
def login():
    if session.get("guru"):
        return redirect('/')
    error = False
    if request.method == "POST":
        u = (request.form.get("username") or "").strip().lower()
        p = request.form.get("password") or ""
        ok = check_password_hash(GURU.get(u, _HASH_PALSU), p) and (u in GURU)
        if ok:
            session.clear()
            session["guru"] = u
            return redirect('/')
        error = True
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout', methods=["GET","POST"])
def logout():
    session.clear()
    return redirect('/login')
# ==================== AKHIR LOGIN GURU ====================

TANGGAL_NILAI_LAMA = "2026-11-19"

def _migrasi_nilai_tanggal(conn, cur):
    # Tambah kolom tanggal ke tabel nilai (sekali saja). Nilai lama otomatis diisi 2026-11-19.
    cur.execute("CREATE TABLE IF NOT EXISTS nilai (id SERIAL PRIMARY KEY, siswa_id INT, nilai FLOAT, jenis VARCHAR(30), keterangan TEXT)")
    cur.execute("SELECT 1 FROM information_schema.columns WHERE table_name='nilai' AND column_name='tanggal'")
    if cur.fetchone() is None:
        cur.execute("ALTER TABLE nilai ADD COLUMN tanggal DATE")
        cur.execute("UPDATE nilai SET tanggal=%s WHERE tanggal IS NULL", (TANGGAL_NILAI_LAMA,))
        cur.execute("ALTER TABLE nilai ALTER COLUMN tanggal SET DEFAULT CURRENT_DATE")
    conn.commit()

def _parse_tanggal(val):
    try:
        return datetime.strptime((val or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return date.today()

@app.route('/')
def index():
    conn=get_db(); cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS absensi (id SERIAL PRIMARY KEY, siswa_id INT, tanggal DATE DEFAULT CURRENT_DATE, status VARCHAR(20))")
    cur.execute("CREATE TABLE IF NOT EXISTS nilai (id SERIAL PRIMARY KEY, siswa_id INT, nilai FLOAT, jenis VARCHAR(30), keterangan TEXT)")
    conn.commit()
    _migrasi_nilai_tanggal(conn, cur)
    cur.execute("SELECT id,nama,kelas FROM siswa ORDER BY nama"); siswa=cur.fetchall()
    cur.execute("SELECT s.nama,a.status FROM absensi a JOIN siswa s ON s.id=a.siswa_id WHERE a.tanggal=CURRENT_DATE ORDER BY s.nama"); sudah=cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM nilai"); total_nilai=cur.fetchone()[0]
    cur.execute("SELECT s.nama,s.kelas,AVG(n.nilai),COUNT(n.id) FROM nilai n JOIN siswa s ON s.id=n.siswa_id GROUP BY s.nama,s.kelas ORDER BY AVG(n.nilai) DESC")
    leaderboard=cur.fetchall()
    cur.execute("SELECT n.id,s.nama,s.kelas,n.jenis,n.nilai,n.tanggal,n.keterangan FROM nilai n JOIN siswa s ON s.id=n.siswa_id ORDER BY n.tanggal DESC NULLS LAST, n.id DESC LIMIT 200")
    riwayat_nilai=cur.fetchall()
    juara_nama=leaderboard[0][0] if leaderboard else "Selvy Deffya"
    juara_nilai=f"{leaderboard[0][2]:.1f}" if leaderboard else "93.0"
    conn.close()
    return render_template_string(HTML, siswa=siswa, sudah=sudah, total=len(siswa), total_nilai=total_nilai, juara_nama=juara_nama, juara_nilai=juara_nilai, leaderboard=leaderboard, riwayat_nilai=riwayat_nilai)

@app.route('/absen', methods=["POST"])
def absen():
    conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM absensi WHERE tanggal=CURRENT_DATE")
    cur.execute("SELECT id FROM siswa")
    for (sid,) in cur.fetchall():
        cur.execute("INSERT INTO absensi (siswa_id,status) VALUES (%s,%s)", (sid, request.form.get(f"status_{sid}")))
    conn.commit(); conn.close(); return redirect('/')

@app.route('/nilai', methods=["POST"])
def tambah_nilai():
    conn=get_db(); cur=conn.cursor()
    _migrasi_nilai_tanggal(conn, cur)
    tgl=_parse_tanggal(request.form.get("tanggal"))
    cur.execute("INSERT INTO nilai (siswa_id,nilai,jenis,keterangan,tanggal) VALUES (%s,%s,%s,%s,%s)", (request.form.get("siswa_id"), request.form.get("nilai"), request.form.get("jenis"), request.form.get("ket"), tgl))
    conn.commit(); conn.close(); return redirect('/')

@app.route('/tambah-siswa', methods=["POST"])
def tambah_siswa():
    nama=(request.form.get("nama") or "").strip()
    kelas=request.form.get("kelas")
    if nama:
        conn=get_db(); cur=conn.cursor()
        cur.execute("INSERT INTO siswa (nama,kelas) VALUES (%s,%s)", (nama, kelas))
        conn.commit(); conn.close()
    return redirect('/')

KELAS_VALID = [str(n) + h for n in range(1, 7) for h in "ABC"]

def _norm_kelas(raw):
    m = re.search(r'([1-6])[^0-9A-Za-z]*([A-Ca-c])?', str(raw or ''))
    if not m:
        return '5A'
    k = m.group(1) + (m.group(2).upper() if m.group(2) else 'A')
    return k if k in KELAS_VALID else '5A'

def _next_url(val):
    if val and val.startswith('/') and not val.startswith('//') and '\\' not in val and '\n' not in val and '\r' not in val:
        return val
    return '/'

EDIT_HTML = """
<!DOCTYPE html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Edit Siswa - SiCeria</title>
<script>(function(){try{var t=localStorage.getItem('siceria-theme');if(t){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();</script>
<style>
:root{--bg:#f3f5fb;--surface:#fff;--surface2:#f2f5fb;--text:#0f172a;--muted:#64748b;--line:#e3e8f3;--brand:#6d5efc;--brand2:#e84fa5}
[data-theme="dark"]{--bg:#080c18;--surface:#111729;--surface2:#171f36;--text:#e8edf8;--muted:#8a96b4;--line:#222b45}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:grid;place-items:center;padding:16px}
.box{width:min(460px,100%);background:var(--surface);border:1px solid var(--line);border-radius:24px;padding:26px;box-shadow:0 20px 60px rgba(0,0,0,.25)}
h1{font-size:1.2rem;font-weight:800;margin-bottom:4px}
p{color:var(--muted);font-size:.9rem;margin-bottom:18px}
label{display:block;font-size:.78rem;font-weight:700;color:var(--muted);margin:14px 0 6px}
input,select{width:100%;background:var(--surface2);color:var(--text);border:1px solid var(--line);border-radius:14px;padding:12px 14px;font:inherit;outline:none}
input:focus,select:focus{border-color:var(--brand);box-shadow:0 0 0 4px rgba(109,94,252,.2)}
.row{display:flex;gap:10px;margin-top:22px}
.btn{flex:1;text-align:center;text-decoration:none;border:0;cursor:pointer;border-radius:14px;padding:13px 16px;font:inherit;font-weight:800;color:#fff;background:linear-gradient(90deg,var(--brand),var(--brand2))}
.btn.ghost{background:var(--surface2);color:var(--text);border:1px solid var(--line)}
.top{position:fixed;top:14px;right:14px;display:flex;align-items:center;gap:10px;z-index:5}
.top span{font-size:.85rem;color:var(--muted);font-weight:600}
.top b{color:var(--text)}
.top button{cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--text);border-radius:12px;padding:9px 14px;font:inherit;font-weight:700;font-size:.82rem}
.top button:hover{border-color:#ef4444}
</style>
</head>
<body>
<form class="top" method="post" action="/logout">
  <span>👤 Halo, <b>{{ guru }}</b></span>
  <button type="submit">🚪 Logout ({{ guru }})</button>
</form>
<form class="box" method="post" action="/edit-siswa/{{ s[0] }}">
  <h1>✏️ Edit Siswa</h1>
  <p>Ubah nama atau kelas siswa, lalu simpan.</p>
  <input type="hidden" name="next" value="{{ next_url }}">
  <label for="nama">Nama Siswa</label>
  <input name="nama" id="nama" value="{{ s[1] }}" required maxlength="100" autocomplete="off">
  <label for="kelas">Kelas</label>
  <select name="kelas" id="kelas">
    {% for k in kelas_list %}<option value="{{ k }}" {% if k == kelas_sel %}selected{% endif %}>Kelas {{ k }}</option>{% endfor %}
  </select>
  <div class="row">
    <a class="btn ghost" href="{{ next_url }}">Batal</a>
    <button class="btn" type="submit">💾 Simpan</button>
  </div>
</form>
</body>
</html>
"""

@app.route('/edit-siswa/<int:siswa_id>', methods=["GET","POST"])
def edit_siswa(siswa_id):
    if request.method == "POST":
        nama=(request.form.get("nama") or "").strip()
        kelas=(request.form.get("kelas") or "").strip().upper()
        nxt=_next_url(request.form.get("next"))
        if nama and kelas in KELAS_VALID:
            conn=get_db(); cur=conn.cursor()
            cur.execute("UPDATE siswa SET nama=%s, kelas=%s WHERE id=%s", (nama, kelas, siswa_id))
            conn.commit(); conn.close()
        return redirect(nxt)
    nxt=_next_url(request.args.get("next"))
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT id,nama,kelas FROM siswa WHERE id=%s", (siswa_id,))
    s=cur.fetchone(); conn.close()
    if not s:
        return redirect(nxt)
    return render_template_string(EDIT_HTML, s=s, kelas_list=KELAS_VALID, kelas_sel=_norm_kelas(s[2]), next_url=nxt)

@app.route('/hapus-siswa/<int:siswa_id>', methods=["POST"])
def hapus_siswa(siswa_id):
    conn=get_db(); cur=conn.cursor()
    cur.execute("DELETE FROM absensi WHERE siswa_id=%s", (siswa_id,))
    cur.execute("DELETE FROM nilai WHERE siswa_id=%s", (siswa_id,))
    cur.execute("DELETE FROM siswa WHERE id=%s", (siswa_id,))
    conn.commit(); conn.close()
    return redirect('/')

def _kelas_filter():
    k = (request.args.get("kelas") or "").strip().upper()
    return k if k in KELAS_VALID else ""

def _csv_aman(v):
    s = "" if v is None else str(v)
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s

def _fmt_angka(v):
    if v is None:
        return ""
    f = float(v)
    if f == int(f):
        return str(int(f))
    return str(round(f, 2)).replace(".", ",")

def _kirim_csv(prefix, header, rows, kelas):
    buf = io.StringIO()
    buf.write("\ufeff")
    buf.write("sep=;\r\n")
    w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    nama_kelas = ("Kelas-" + kelas) if kelas else "Semua-Kelas"
    fname = "%s_%s_%s.csv" % (prefix, nama_kelas, date.today().isoformat())
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="%s"' % fname})

@app.route('/download-absensi')
def download_absensi():
    kelas=_kelas_filter()
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT s.nama,s.kelas,a.tanggal,a.status FROM absensi a JOIN siswa s ON s.id=a.siswa_id ORDER BY a.tanggal, s.kelas, s.nama")
    data=cur.fetchall(); conn.close()
    rows=[]
    for nama,kls,tgl,status in data:
        k=_norm_kelas(kls)
        if kelas and k!=kelas:
            continue
        rows.append([_csv_aman(nama), k, tgl.isoformat() if tgl else "", _csv_aman(status)])
    return _kirim_csv("Absensi", ["Nama Siswa","Kelas","Tanggal","Status"], rows, kelas)

@app.route('/download-nilai')
def download_nilai():
    kelas=_kelas_filter()
    conn=get_db(); cur=conn.cursor()
    _migrasi_nilai_tanggal(conn, cur)
    cur.execute("SELECT s.nama,s.kelas,n.jenis,n.nilai,n.tanggal,n.keterangan FROM nilai n JOIN siswa s ON s.id=n.siswa_id ORDER BY s.kelas, s.nama, n.tanggal, n.id")
    data=cur.fetchall(); conn.close()
    rows=[]
    for nama,kls,jenis,nilai,tgl,ket in data:
        k=_norm_kelas(kls)
        if kelas and k!=kelas:
            continue
        rows.append([_csv_aman(nama), k, _csv_aman(jenis), _fmt_angka(nilai), tgl.isoformat() if tgl else "", _csv_aman(ket)])
    return _kirim_csv("Nilai", ["Nama Siswa","Kelas","Jenis Nilai","Nilai","Tanggal","Keterangan"], rows, kelas)

if __name__=='__main__': app.run(host='0.0.0.0', port=5000, debug=True)
