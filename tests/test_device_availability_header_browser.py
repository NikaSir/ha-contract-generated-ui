"""Real-browser checks for the registered production entrypoint.

Run with: NIKAS_CHROMIUM=/usr/bin/chromium python -m pytest -q
  tests/test_device_availability_header_browser.py
Playwright and a Chromium binary are optional browser-test dependencies. This
stand mocks only the HA host, icon component and API; it executes the real panel.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import re

import pytest

playwright_api = pytest.importorskip("playwright.sync_api")
ROOT = Path(__file__).parents[1]
FRONTEND = ROOT / "custom_components" / "contract_generated_ui" / "frontend"
HTML = """<!doctype html><html lang="ru"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
:root{--primary-color:#03a9d9;--primary-background-color:#f8f8f8;--card-background-color:#fff;--divider-color:#dfe3e8;--primary-text-color:#17191c;--secondary-text-color:#68737d}
body{margin:0}#host{position:absolute;inset:0;overflow:hidden}
ha-icon{display:inline-block}
</style><div id="host"></div><script type="module">
import {NikasDeviceAvailabilityPanel} from '/device-availability-panel.js?build=b004';
customElements.define('ha-icon', class extends HTMLElement {
  static get observedAttributes(){return ['icon'];}
  constructor(){super();this.attachShadow({mode:'open'});}
  connectedCallback(){this.render();} attributeChangedCallback(){this.render();}
  render(){this.shadowRoot.innerHTML=`<style>:host{display:inline-flex;width:var(--mdc-icon-size,24px);height:var(--mdc-icon-size,24px)}</style>`;}
});
window.calls=[];window.menuEvents=[];window.locationEvents=[];window.mode='success';
window.addEventListener('hass-toggle-menu',e=>menuEvents.push({bubbles:e.bubbles,composed:e.composed}));
window.addEventListener('location-changed',()=>locationEvents.push(location.pathname));
window.states={};
for (const [slug,name,total,online,offline,extra] of [
 ['okna','Окна',12,11,1,0], ['svet','Свет',12,9,0,3], ['other','Другое',12,10,0,2]
]) {
 states[`sensor.entity_availability_${slug}_group_summary`]={state:String(total),attributes:{
  group_name:name,total_entities:total,essential:total-extra,online,offline,
  non_essential:extra,non_essential_online:extra,non_essential_offline:0,
  stale:0,low_battery:0,poor_signal:0,
  entities:['sensor.'+slug],display_names:{['sensor.'+slug]:name}
 }};
}
window.hass={states,callService:async(...args)=>{calls.push(args);return undefined;}};
window.panel=new NikasDeviceAvailabilityPanel();
panel.panel={config:{parent_route:'/home/overview'}};
panel.hass=hass;document.querySelector('#host').append(panel);window.ready=true;
</script></html>"""

@pytest.fixture(scope="module")
def browser():
    binary = os.environ.get("NIKAS_CHROMIUM") or shutil.which("chromium")
    with playwright_api.sync_playwright() as tool:
        if not binary and not Path(tool.chromium.executable_path).exists():
            pytest.skip("Install Chromium or set NIKAS_CHROMIUM for browser acceptance")
        browser = tool.chromium.launch(executable_path=binary, args=["--no-sandbox"])
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page(viewport={"width":393,"height":852})
    blob="code => URL.createObjectURL(new Blob([code], {type:'text/javascript'}))"
    model_url=page.evaluate(blob,(FRONTEND/"device-availability-model.js").read_text())
    source=(FRONTEND/"device-availability-panel.js").read_text()
    source=re.sub(r'\./device-availability-model\.js\?build=[^"\s]+',model_url,source)
    module_url=page.evaluate(blob,source)
    page.set_content(HTML.replace('/device-availability-panel.js?build=b004',module_url))
    page.wait_for_function("window.ready === true")
    yield page
    page.close()

def test_beta004_header_matches_ui22_refresh_and_full_title(page):
    result=page.locator("header").evaluate("""header=>{const r=header.getRootNode(),b=r.querySelector('#refresh'),i=b.querySelector('ha-icon'),t=r.querySelector('#title');return {version:t.querySelector('small').textContent,title:t.querySelector('strong').textContent,titleIcon:t.querySelector('.title-heading ha-icon')!==null,bg:getComputedStyle(b).backgroundColor,color:getComputedStyle(i).color,w:b.getBoundingClientRect().width,h:b.getBoundingClientRect().height,radius:getComputedStyle(b).borderRadius}}""")
    assert result=={"version":"UI v1.0.0-beta004","title":"Доступность устройств","titleIcon":False,"bg":"rgb(255, 255, 255)","color":"rgb(3, 169, 217)","w":44,"h":44,"radius":"16px"}

def test_device_filters_survive_hass_updates_without_replacement(page):
    page.locator('[data-tab="devices"]').click()
    page.evaluate("""()=>{const r=panel.shadowRoot;window.groupBefore=r.querySelector('#group-filter');window.conditionBefore=r.querySelector('#condition-filter');groupBefore.focus();}""")
    page.evaluate("panel.hass={...hass,states:{...states}}")
    assert page.evaluate("groupBefore===panel.shadowRoot.querySelector('#group-filter')")
    assert page.evaluate("conditionBefore===panel.shadowRoot.querySelector('#condition-filter')")
    assert page.evaluate("panel.shadowRoot.activeElement===groupBefore")

def test_summary_hass_update_preserves_dom_and_scroll_position(page):
    page.locator('[data-tab="summary"]').click()
    page.evaluate("""()=>{const r=panel.shadowRoot,v=r.querySelector('#viewport');window.heroBefore=r.querySelector('.hero');window.groupsBefore=r.querySelector('.groups');v.scrollTop=180;window.scrollBefore=v.scrollTop;}""")
    page.evaluate("panel.hass={...hass,states:{...states}}")
    assert page.evaluate("heroBefore===panel.shadowRoot.querySelector('.hero')")
    assert page.evaluate("groupsBefore===panel.shadowRoot.querySelector('.groups')")
    assert page.evaluate("scrollBefore===panel.shadowRoot.querySelector('#viewport').scrollTop")
