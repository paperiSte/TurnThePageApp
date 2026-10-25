"""Optional browser smoke check. Run from the repository root; requires Playwright Chromium."""
import subprocess,time,os
from playwright.sync_api import sync_playwright
server=subprocess.Popen(['python','-m','streamlit','run','app.py','--server.headless','true','--server.address','127.0.0.1','--server.port','8502','--browser.gatherUsageStats','false'],stdout=open('/tmp/turnthepage-server.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(4)
 with sync_playwright() as pw:
  b=pw.chromium.launch(args=['--no-sandbox']);p=b.new_page(viewport={'width':1200,'height':1000});errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8502');f=p.frame_locator('iframe');f.locator('#score svg').first.wait_for(timeout=90000);assert f.locator('#page').inner_text()=='Page 1 of 2';assert f.locator('g.active').count()==1
  f.locator('#play').click();p.wait_for_timeout(250);assert f.locator('#audio').evaluate('(a)=>!a.paused');f.locator('#play').click();t=f.locator('#audio').evaluate('(a)=>a.currentTime');p.wait_for_timeout(150);assert f.locator('#audio').evaluate('(a)=>a.currentTime')==t
  f.locator('#audio').evaluate('(a)=>{a.currentTime=2.4}');p.wait_for_timeout(150);assert f.locator('#preview').is_visible();assert f.locator('#page').inner_text()=='Page 1 of 2';p.screenshot(path='/tmp/turnthepage-app-preview.png',full_page=True)
  f.locator('#audio').evaluate('(a)=>{a.currentTime=3}');p.wait_for_timeout(150);assert f.locator('#page').inner_text()=='Page 2 of 2';f.locator('#previous').click();assert not f.locator('#auto').is_checked();assert f.locator('#page').inner_text()=='Page 1 of 2';f.locator('#auto').check();p.wait_for_timeout(100);assert f.locator('#page').inner_text()=='Page 2 of 2';f.locator('#restart').click();assert f.locator('#page').inner_text()=='Page 1 of 2';assert f.locator('#audio').evaluate('(a)=>a.currentTime')==0;assert not errors,errors;print('PASS: Streamlit, real alignment, playback, pause, preview, page turn, manual recovery, rejoin, restart; no browser errors');b.close()
finally:
 server.terminate();server.wait(timeout=10)
