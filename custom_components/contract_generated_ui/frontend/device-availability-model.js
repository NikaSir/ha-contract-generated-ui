const GROUP_SUMMARY = /^sensor\.entity_availability_(.+)_group_summary$/;

const asObject = (value) => value && typeof value === "object" && !Array.isArray(value)
  ? value
  : {};
const asList = (value) => Array.isArray(value) ? value.filter((item) => typeof item === "string") : [];
const asNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
};

function groupDisplayName(slug, attributes) {
  const explicit = attributes.group_name;
  if (typeof explicit === "string" && explicit.trim()) return explicit.trim();
  const friendly = typeof attributes.friendly_name === "string"
    ? attributes.friendly_name
    : "";
  const cleaned = friendly
    .replace(/^Entity Availability\s*-\s*/i, "")
    .replace(/\s*(Group summary|Сводка группы)\s*$/i, "")
    .trim();
  if (cleaned) return cleaned;
  return slug.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}

export function discoverAvailabilityGroups(states = {}) {
  return Object.entries(asObject(states))
    .map(([entityId, state]) => {
      const match = entityId.match(GROUP_SUMMARY);
      if (!match) return null;
      const attributes = asObject(state?.attributes);
      return {
        entityId,
        slug: match[1],
        name: groupDisplayName(match[1], attributes),
        state: String(state?.state ?? "unavailable"),
        attributes,
      };
    })
    .filter(Boolean)
    .sort((left, right) => left.name.localeCompare(right.name, "ru"));
}

function conditionFor(entityId, attributes) {
  const offline = new Set(asList(attributes.offline_entities));
  const offlineNonEssential = new Set(asList(attributes.offline_entities_non_essential));
  const stale = new Set([
    ...asList(attributes.stale_entities),
    ...asList(attributes.stale_entities_non_essential),
  ]);
  const lowBattery = new Set([
    ...asList(attributes.low_battery_entities),
    ...asList(attributes.low_battery_entities_non_essential),
  ]);
  const poorSignal = new Set([
    ...asList(attributes.poor_signal_entities),
    ...asList(attributes.poor_signal_entities_non_essential),
  ]);
  const suppressed = asObject(attributes.suppressed_until);
  if (offline.has(entityId) || offlineNonEssential.has(entityId)) return "offline";
  if (stale.has(entityId)) return "stale";
  if (lowBattery.has(entityId)) return "low_battery";
  if (poorSignal.has(entityId)) return "poor_signal";
  if (Object.hasOwn(suppressed, entityId)) return "suppressed";
  return "online";
}

const CONDITION_WEIGHT = Object.freeze({
  offline: 0,
  stale: 1,
  low_battery: 2,
  poor_signal: 3,
  suppressed: 4,
  online: 5,
});

function buildGroup(source) {
  const attributes = source.attributes;
  const unavailable = ["unavailable", "unknown"].includes(source.state);
  if (unavailable) {
    return {
      slug: source.slug,
      name: source.name,
      sourceEntityId: source.entityId,
      condition: "no_data",
      total: 0,
      essential: 0,
      nonEssential: 0,
      nonEssentialOnline: 0,
      nonEssentialOffline: 0,
      nonEssentialSuppressed: 0,
      online: 0,
      offline: 0,
      stale: 0,
      lowBattery: 0,
      poorSignal: 0,
      suppressed: 0,
      items: [],
    };
  }

  const entities = asList(attributes.entities_collapsed).length
    ? asList(attributes.entities_collapsed)
    : asList(attributes.entities);
  const names = asObject(attributes.display_names);
  const battery = asObject(attributes.battery_levels);
  const signal = asObject(attributes.signal_levels);
  const signalUnits = asObject(attributes.signal_units);
  const offlineSince = asObject(attributes.offline_since);
  const lastSeen = asObject(attributes.last_seen);
  const nonEssential = new Set(asList(attributes.non_essential_entities));
  const rowMembers = asObject(attributes.row_members);
  const items = entities.map((entityId) => ({
    entityId,
    memberEntityIds: asList(rowMembers[entityId]).length
      ? asList(rowMembers[entityId])
      : [entityId],
    name: typeof names[entityId] === "string" ? names[entityId] : entityId,
    group: source.slug,
    groupName: source.name,
    condition: conditionFor(entityId, attributes),
    nonEssential: nonEssential.has(entityId),
    battery: Number.isFinite(Number(battery[entityId])) ? Number(battery[entityId]) : null,
    signal: Number.isFinite(Number(signal[entityId]))
      ? { value: Number(signal[entityId]), unit: String(signalUnits[entityId] || "") }
      : null,
    offlineSince: typeof offlineSince[entityId] === "string" ? offlineSince[entityId] : null,
    lastSeen: typeof lastSeen[entityId] === "string" ? lastSeen[entityId] : null,
  }));
  const problemCount = asNumber(attributes.offline)
    + asNumber(attributes.stale)
    + asNumber(attributes.low_battery)
    + asNumber(attributes.poor_signal);
  return {
    slug: source.slug,
    name: source.name,
    sourceEntityId: source.entityId,
    condition: problemCount > 0 ? "problem" : "healthy",
    total: asNumber(attributes.total_entities ?? source.state),
    essential: asNumber(attributes.essential ?? (
      asNumber(attributes.total_entities ?? source.state) - asNumber(attributes.non_essential)
    )),
    nonEssential: asNumber(attributes.non_essential),
    nonEssentialOnline: asNumber(attributes.non_essential_online),
    nonEssentialOffline: asNumber(attributes.non_essential_offline),
    nonEssentialSuppressed: asNumber(attributes.non_essential_suppressed),
    online: asNumber(attributes.online),
    offline: asNumber(attributes.offline),
    stale: asNumber(attributes.stale),
    lowBattery: asNumber(attributes.low_battery),
    poorSignal: asNumber(attributes.poor_signal),
    suppressed: asNumber(attributes.suppressed),
    items,
  };
}

export function buildAvailabilitySnapshot(states = {}) {
  const sources = discoverAvailabilityGroups(states);
  const emptyTotals = {
    total: 0,
    online: 0,
    offline: 0,
    stale: 0,
    low_battery: 0,
    poor_signal: 0,
  };
  const emptyComposition = {
    essential: 0,
    non_essential: 0,
    suppressed: 0,
    non_essential_online: 0,
    non_essential_offline: 0,
    non_essential_suppressed: 0,
  };
  if (!sources.length) {
    return {
      status: "no_integration",
      totals: emptyTotals,
      composition: emptyComposition,
      groups: [],
      items: [],
      diagnostics: { unavailableSources: [], missingOptionalData: [] },
      updateEntityIds: [],
    };
  }

  const groups = sources.map(buildGroup).sort((left, right) => {
    const leftWeight = left.condition === "no_data" ? 0 : left.condition === "problem" ? 1 : 2;
    const rightWeight = right.condition === "no_data" ? 0 : right.condition === "problem" ? 1 : 2;
    return leftWeight - rightWeight || left.name.localeCompare(right.name, "ru");
  });
  const totals = groups.reduce((result, group) => ({
    total: result.total + group.total,
    online: result.online + group.online,
    offline: result.offline + group.offline,
    stale: result.stale + group.stale,
    low_battery: result.low_battery + group.lowBattery,
    poor_signal: result.poor_signal + group.poorSignal,
  }), { ...emptyTotals });
  const composition = groups.reduce((result, group) => ({
    essential: result.essential + group.essential,
    non_essential: result.non_essential + group.nonEssential,
    suppressed: result.suppressed + group.suppressed,
    non_essential_online: result.non_essential_online + group.nonEssentialOnline,
    non_essential_offline: result.non_essential_offline + group.nonEssentialOffline,
    non_essential_suppressed: result.non_essential_suppressed + group.nonEssentialSuppressed,
  }), { ...emptyComposition });
  const items = groups.flatMap((group) => group.items).sort((left, right) => (
    (CONDITION_WEIGHT[left.condition] ?? 99) - (CONDITION_WEIGHT[right.condition] ?? 99)
    || left.name.localeCompare(right.name, "ru")
  ));
  const unavailableSources = groups
    .filter((group) => group.condition === "no_data")
    .map((group) => group.sourceEntityId);
  const problem = totals.offline + totals.stale + totals.low_battery + totals.poor_signal > 0;
  return {
    status: unavailableSources.length ? "no_data" : problem ? "problem" : "healthy",
    totals,
    composition,
    groups,
    items,
    diagnostics: { unavailableSources, missingOptionalData: [] },
    updateEntityIds: sources.map((source) => source.entityId).sort(),
  };
}

export function filterAvailabilityItems(
  snapshot,
  query = "",
  group = "all",
  condition = "all",
) {
  const needle = String(query).trim().toLocaleLowerCase("ru");
  return (snapshot?.items || []).filter((item) => {
    if (group !== "all" && item.group !== group) return false;
    if (condition !== "all" && item.condition !== condition) return false;
    if (!needle) return true;
    return `${item.name} ${item.entityId} ${item.groupName}`
      .toLocaleLowerCase("ru")
      .includes(needle);
  });
}
