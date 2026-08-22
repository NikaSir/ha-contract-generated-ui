# Integration dashboard header standard — superseded

**Status:** Superseded  
**Superseded by:** `docs/INTEGRATION_DASHBOARD_UI_STANDARD.md` v1.2

The former header-only standard is no longer normative by itself.

The current required integration-owned dashboard UI standard now covers the complete mobile application shell:

- explicit Back control in the top Header;
- application title geometrically centered on the iPhone viewport;
- no decorative integration/device icon beside the Header title;
- optional short centered subtitle for model/context/version;
- optional global Refresh/overflow action on the right;
- full-width, edge-attached, fixed bottom Tab Bar for 3–5 primary in-app sections;
- no floating/pill primary navigation;
- iOS safe-area handling and content bottom clearance;
- explicit stable parent routes rather than browser-history Back behavior;
- preserved `unknown` / `unavailable` reliability semantics and domain-action safety.

See `docs/INTEGRATION_DASHBOARD_UI_STANDARD.md` for the normative requirements, application-specific corrections and acceptance criteria.
