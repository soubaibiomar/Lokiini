import type { components, paths } from "./openapi";

export type LokiiniApiPaths = keyof paths;
export type LokiiniApiSchemas = keyof components["schemas"];

const healthPath: LokiiniApiPaths = "/api/v1/health";

export { healthPath };
