# Specialized Panel UI Standard — compatibility entry

This historical filename is retained for links only. It is not an independent standard.

The current normative documents are:

- `INTEGRATION_DASHBOARD_UI_STANDARD.md` v1.5;
- `SPECIALIZED_PANEL_SHELL_STANDARD.md` v1.4;
- `SPECIALIZED_PANEL_ZOOM_STANDARD.md` v1.4;
- `SPECIALIZED_PANEL_FRONTEND_DELIVERY_STANDARD.md` v1.2;
- `NIKAS_INTEGRATION_PANEL_TEMPLATE_V1.md` v1.2.

Non-negotiable summary:

- permanent left Header rail is Home Assistant `☰` via `hass-toggle-menu`, never Back/integration drawer/device action;
- Header, peer selector and Bottom Tab remain native scale;
- work content uses one fixed transform-owned canvas;
- transform/state is `translate3d(x,y,0) scale(s)` plus `{scale,x,y}`;
- CSS `zoom`, `scrollLeft`, `scrollTop` and native overflow scrolling are not the canvas engine;
- no permanent zoom controls;
- two-finger reset, 97–103% snap and `Масштаб 100%` feedback are required;
- telemetry rerender restores transform before paint;
- gesture guards block accidental `more-info`/graphs/clicks while stationary long press remains valid.

On conflict, the versioned normative documents above win.

