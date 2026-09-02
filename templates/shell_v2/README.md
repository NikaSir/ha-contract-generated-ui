# NikaS Shell v2 source kit

This directory is the canonical build-time source for the NikaS application shell.
It is not a runtime dependency and is not loaded from Contract Generated UI.

Each owning panel repository copies `nikas-specialized-shell.js` into its frontend
source tree, verifies the canonical SHA-256 in CI and concatenates the copy into its
single autonomous production bundle. Domain cards, entities, commands, routes and
assets remain in the owning repository.

The kit provides:

- host-bound Header / optional peer selector / work viewport / Bottom Tab Bar geometry;
- an iOS-safe touch boundary guard that prevents Home Assistant pull-to-refresh and outer-page scrolling;
- the canonical `1280px` work-content frame and responsive gutters;
- the four current NikaS base-route normalizers;
- one-shot source hand-off, stable return-route capture and explicit Home Assistant navigation.

Adoption order starts with `NikaSir/ha-nikas-access`. A panel is conforming only
after its repository tests pass and the phone/tablet/desktop acceptance matrix is
verified against a real Home Assistant host.
