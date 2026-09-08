# Common generator toolkit

This package validates Architecture-as-Code sources, builds verified semantic
inventory, renders the panel-neutral reference Lovelace layout, computes semantic
diffs and applies fail-closed release gates.

Panel-specific renderers live in their owning repositories. Generated output is
review-only until the owner repository's tests and delivery checks pass.
