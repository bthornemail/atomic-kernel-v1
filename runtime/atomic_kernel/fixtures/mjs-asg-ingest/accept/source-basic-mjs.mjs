import { parse } from './control_surface.mjs';

export class BridgeLayer extends AdapterBase {
  map(input) {
    return parse(input);
  }
}

export function emitEnvelope(payload) {
  return BridgeLayer(payload);
}
