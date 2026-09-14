import fs from "node:fs";
import {
  buildAvailabilitySnapshot,
  discoverAvailabilityGroups,
  filterAvailabilityItems,
} from "../custom_components/contract_generated_ui/frontend/device-availability-model.js";

const request = JSON.parse(fs.readFileSync(0, "utf8"));
let result;
if (request.operation === "discover") {
  result = discoverAvailabilityGroups(request.states);
} else if (request.operation === "filter") {
  const snapshot = buildAvailabilitySnapshot(request.states);
  result = filterAvailabilityItems(
    snapshot,
    request.query || "",
    request.group || "all",
    request.condition || "all",
  );
} else {
  result = buildAvailabilitySnapshot(request.states);
}
process.stdout.write(JSON.stringify(result));
