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
import {NikasDeviceAvailabilityPanel} from '/device-availability-panel.js?build=b003';
// Test-only icon host: production uses Home Assistant's registered ha-icon.
customElements.define('ha-icon', class extends HTMLElement {
  static get observedAttributes(){return ['icon'];}
  constructor(){super();this.attachShadow({mode:'open'});}
  connectedCallback(){this.render();} attributeChangedCallback(){this.render();}
  render(){const paths={
    'mdi:menu':'M3 6h18v2H3V6m0 5h18v2H3v-2m0 5h18v2H3v-2',
    'mdi:refresh':'M17.65 6.35A7.95 7.95 0 0 0 12 4a8 8 0 1 0 7.75 10h-2.08A6 6 0 1 1 12 6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35Z',
    'mdi:check':'m9 16.17-4.17-4.17-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17Z',
    'mdi:alert-circle-outline':'M11 7h2v6h-2V7m0 8h2v2h-2v-2m1-13a10 10 0 1 0 0 20 10 10 0 0 0 0-20m0 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16',
    'mdi:wifi':'M12 18.5 8.5 15a5 5 0 0 1 7 0L12 18.5M5.7 12.2l-2-2a12 12 0 0 1 16.6 0l-2 2a9 9 0 0 0-12.6 0M.9 7.4l2 2a13 13 0 0 1 18.2 0l2-2a16 16 0 0 0-22.2 0'};
    this.shadowRoot.innerHTML=`<style>:host{display:inline-flex;width:var(--mdc-icon-size,24px);height:var(--mdc-icon-size,24px)}svg{width:100%;height:100%;fill:currentColor}</style><svg viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[this.getAttribute('icon')] || 'M4 4h16v16H4V4m2 2v12h12V6H6'}"/></svg>`;
  }
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
window.hass={states,callService:async(...args)=>{
 calls.push(args);
 if(mode==='failure') throw Error('private details must not be shown');
 if(mode==='false') return false;
 if(mode==='pending') return await new Promise((resolve,reject)=>{window.finish=resolve;window.fail=reject;});
 return undefined;
}};
window.panel=new NikasDeviceAvailabilityPanel();
panel.panel={config:{parent_route:'/home/overview'}};
panel.hass=hass;document.querySelector('#host').append(panel);
window.ready=true;
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
    page = browser.new_page(viewport={"width": 393, "height": 852})
    page.clock.install(time=datetime(2026, 9, 15, tzinfo=timezone.utc))
    page.clock.pause_at(datetime(2026, 9, 15, 0, 0, 1, tzinfo=timezone.utc))
    # No browser-network access is required. Only the dependency specifier is
    # mapped to an in-memory URL; production JavaScript is otherwise unchanged.
    blob = "code => URL.createObjectURL(new Blob([code], {type:'text/javascript'}))"
    model_url = page.evaluate(blob, (FRONTEND / "device-availability-model.js").read_text())
    source = (FRONTEND / "device-availability-panel.js").read_text()
    source = re.sub(r'\./device-availability-model\.js\?build=[^"\s]+', model_url, source)
    module_url = page.evaluate(blob, source)
    page.set_content(HTML.replace('/device-availability-panel.js?build=b003', module_url))
    page.wait_for_function("window.ready === true")
    yield page
    page.close()


def click_refresh(page):
    page.locator("header #refresh").dispatch_event("click")


def button_state(page):
    return page.locator("header #refresh").evaluate("""button => ({
      disabled:button.disabled, busy:button.getAttribute('aria-busy'),
      label:button.getAttribute('aria-label'),
      icon:button.querySelector('ha-icon').getAttribute('icon'),
      color:getComputedStyle(button.querySelector('ha-icon')).color
    })""")


@pytest.mark.parametrize("width", [320, 359, 360, 393, 560, 768, 1024, 1440])
def test_header_geometry_at_each_host_width(page, width):
    page.set_viewport_size({"width": width, "height": 852})
    assert page.locator("header #menu").count() == 1
    dimensions = page.locator("header").evaluate("""header => {
      const box=e=>{const b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height}};
      const root=header.getRootNode(), title=root.querySelector('#title');
      return {header:box(header),title:box(title),menu:box(root.querySelector('#menu')),
       refresh:box(root.querySelector('#refresh')), rails:getComputedStyle(header).gridTemplateColumns,
       font:getComputedStyle(title.querySelector('strong')).fontSize,
       weight:getComputedStyle(title.querySelector('strong')).fontWeight,
       version:title.querySelector('small').textContent,
       refreshBg:getComputedStyle(root.querySelector('#refresh')).backgroundColor,
       border:getComputedStyle(title).borderRadius,
       overflow:document.documentElement.scrollWidth>innerWidth};
    }""")
    assert dimensions["header"]["h"] == 60
    assert dimensions["header"]["w"] == width
    assert dimensions["title"]["h"] == 52
    assert dimensions["title"]["w"] == min(360, width - 24 - (96 if width < 360 else 104))
    assert abs(dimensions["title"]["x"] + dimensions["title"]["w"] / 2 - width / 2) < 0.1
    for action in ("menu", "refresh"):
        assert dimensions[action]["w"] == 44
        assert dimensions[action]["h"] == 44
    assert dimensions["font"] == ("21px" if width < 360 else "23px")
    assert dimensions["weight"] == "800"
    assert dimensions["version"] == "UI v1.0.0-beta003"
    assert dimensions["refreshBg"] == "rgb(17, 20, 24)"
    assert dimensions["border"] == "16px"
    assert not dimensions["overflow"]


def test_header_follows_host_not_window_when_sidebar_takes_space(page):
    page.set_viewport_size({"width": 1024, "height": 768})
    page.locator("#host").evaluate("e => {e.style.left='260px';e.style.width='340px'}")
    assert page.locator("header").bounding_box()["width"] == 340
    assert page.locator("header #title strong").evaluate("e=>getComputedStyle(e).fontSize") == "21px"
    assert page.locator("header").bounding_box()["x"] == 260


def test_header_actions_are_wired_and_summary_has_no_duplicate(page):
    assert page.locator("#refresh").count() == 1
    assert page.locator("#content #refresh").count() == 0
    page.locator("header #menu").dispatch_event("click")
    assert page.evaluate("menuEvents") == [{"bubbles": True, "composed": True}]



def test_fast_success_minimum_duration_green_check_and_idle(page):
    click_refresh(page)
    assert button_state(page)["busy"] == "true"
    assert button_state(page)["disabled"]
    page.clock.run_for(899)
    assert button_state(page)["icon"] == "mdi:refresh"
    page.clock.run_for(1)
    assert button_state(page) == {"disabled": False, "busy": "false",
      "label": "Запрос обновления выполнен", "icon": "mdi:check", "color": "rgb(67, 160, 71)"}
    page.clock.run_for(1399)
    assert button_state(page)["icon"] == "mdi:check"
    page.clock.run_for(1)
    assert button_state(page)["label"] == "Обновить"
    assert button_state(page)["icon"] == "mdi:refresh"
    calls = page.evaluate("calls")
    assert calls == [["homeassistant", "update_entity", {"entity_id": [
      "sensor.entity_availability_okna_group_summary", "sensor.entity_availability_other_group_summary",
      "sensor.entity_availability_svet_group_summary"]}]]


def test_slow_refresh_and_duplicate_activation(page):
    page.evaluate("mode='pending'")
    click_refresh(page)
    page.evaluate("panel._refresh(); panel._refresh()")
    page.clock.run_for(2500)
    assert len(page.evaluate("calls")) == 1
    assert button_state(page)["disabled"]
    page.evaluate("finish()")
    assert button_state(page)["icon"] == "mdi:check"


@pytest.mark.parametrize("mode", ["failure", "false", "no_entities", "no_service"])
def test_failures_honor_busy_interval_and_show_visible_safe_error(page, mode):
    page.evaluate("value=>{mode=value;if(value==='no_entities')panel.hass={...hass,states:{}};if(value==='no_service')panel.hass={states}}", mode)
    click_refresh(page)
    page.clock.run_for(899)
    assert button_state(page)["busy"] == "true"
    page.clock.run_for(1)
    assert button_state(page)["icon"] == "mdi:alert-circle-outline"
    assert button_state(page)["color"] == "rgb(229, 57, 53)"
    assert not button_state(page)["disabled"]
    error = page.locator("#refresh-error")
    assert error.is_visible()
    assert "Не удалось обновить данные" in error.inner_text()
    assert "private" not in error.inner_text()
    page.clock.run_for(1400)
    assert button_state(page)["icon"] == "mdi:refresh"


def test_retry_during_result_cancels_previous_timer(page):
    click_refresh(page)
    page.clock.run_for(900)
    page.clock.run_for(500)
    page.evaluate("mode='pending'")
    click_refresh(page)
    page.clock.run_for(2000)
    assert button_state(page)["busy"] == "true"
    assert len(page.evaluate("calls")) == 2
    page.evaluate("finish()")
    assert button_state(page)["icon"] == "mdi:check"
    page.clock.run_for(1399)
    assert button_state(page)["icon"] == "mdi:check"
    page.clock.run_for(1)
    assert button_state(page)["icon"] == "mdi:refresh"


def test_telemetry_and_tabs_keep_header_and_original_result_deadline(page):
    page.evaluate("window.headerBefore=panel.shadowRoot.querySelector('header'); window.refreshBefore=panel.shadowRoot.querySelector('#refresh')")
    click_refresh(page)
    page.clock.run_for(900)
    page.clock.run_for(400)
    page.locator('[data-tab="devices"]').dispatch_event("click")
    page.evaluate("panel.hass={...hass}")
    page.locator('[data-tab="diagnostics"]').dispatch_event("click")
    assert page.evaluate("headerBefore===panel.shadowRoot.querySelector('header') && refreshBefore===panel.shadowRoot.querySelector('#refresh')")
    assert button_state(page)["icon"] == "mdi:check"
    page.clock.run_for(1000)
    assert button_state(page)["icon"] == "mdi:refresh"


def test_refresh_preserves_content_scroll_zoom_and_truthful_status(page):
    page.evaluate("""() => {
      const r=panel.shadowRoot;window.contentBefore=r.querySelector('#content').innerHTML;
      window.heroBefore=r.querySelector('.hero');r.querySelector('#viewport').scrollTop=120;
      window.scrollBefore=r.querySelector('#viewport').scrollTop;
      panel._zoom=1.2;r.querySelector('#canvas').style.transform='scale(1.2)';
    }""")
    click_refresh(page)
    page.clock.run_for(2300)
    assert page.evaluate("heroBefore===panel.shadowRoot.querySelector('.hero')")
    assert page.evaluate("contentBefore===panel.shadowRoot.querySelector('#content').innerHTML")
    assert page.evaluate("scrollBefore===panel.shadowRoot.querySelector('#viewport').scrollTop")
    assert page.evaluate("panel._zoom") == 1.2
    assert page.evaluate("panel._snapshot.status") == "problem"


def test_reduced_motion_has_static_busy_state_and_keyboard_works(page):
    page.emulate_media(reduced_motion="reduce")
    page.evaluate("mode='pending'")
    page.locator("header #refresh").focus()
    page.keyboard.press("Enter")
    assert button_state(page)["busy"] == "true"
    assert page.locator("header #refresh ha-icon").evaluate("e=>getComputedStyle(e).animationName") == "none"
    assert len(page.evaluate("calls")) == 1


def test_disconnect_ignores_late_completion(page):
    page.evaluate("mode='pending'")
    click_refresh(page)
    page.evaluate("""() => {
      panel.remove();window.lateWrites=0;
      new MutationObserver(records=>lateWrites+=records.length).observe(panel.shadowRoot,{subtree:true,attributes:true,childList:true,characterData:true});
    }""")
    page.evaluate("finish()")
    page.clock.run_for(5000)
    assert page.evaluate("lateWrites") == 0
    assert page.evaluate("panel._refreshTimer") is None
    assert page.evaluate("panel._refreshState") == "idle"
