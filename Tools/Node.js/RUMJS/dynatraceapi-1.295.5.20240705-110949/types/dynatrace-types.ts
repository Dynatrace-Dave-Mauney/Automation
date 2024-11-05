export type JSONObject = { [k: string]: JSONValue };
export type Primitive = string | number | boolean | null;
export type JSONArray = JSONValue[];
export type JSONValue = JSONArray | JSONObject | Primitive;

export interface DynatraceApi {
    /**
     * Sends an event with the given type in form of JSON.
     *
     * @example
     * ```typescript
     * dynatrace.sendEvent("click", {
     *     prop: "value",
     *     timestamp: 123,
     *     url: "www.dynatrace.com",
     *     "page_id": "123456789",
     *     "window.orientation": "diagonal"
     * });
     *```
     * @ignore
     * @param type       Mandatory event type
     * @param attributes Must be a valid JSON object and cannot contain functions, undefined, Infinity and NaN as values, otherwise they will be replaced with null.
     *                   `Attributes` need to be serializable using JSON.stringify.
     *                   The resulting event will be populated with `attributes` parameter, and enriched with additional properties, thus also empty objects are valid.
     */
    sendEvent(type: string, attributes: JSONObject): void;

    /**
     * Send a Business Event
     *
     * With sendBizEvent, you can report a business event. These standalone events are being sent detached from user actions or sessions.
     * Note: Business events are only supported on Dynatrace SaaS deployments currently.
     *
     * @example
     * ```typescript
     * dynatrace.sendBizEvent("type", {
     *     prop: "value",
     *     name: "biz event name",
     *     timestamp: 123,
     *     url: "www.dynatrace.com",
     *     "page_id": "123456789",
     *     "window.orientation": "diagonal"
     * });
     *```
     *
     * @param type       Mandatory event type
     * @param attributes Must be a valid JSON object and cannot contain functions, undefined, Infinity and NaN as values, otherwise they will be replaced with null.
     *                   `Attributes` need to be serializable using JSON.stringify.
     *                   The resulting event will be populated with `attributes` parameter, and enriched with additional properties, thus also empty objects are valid.
     */
    sendBizEvent(type: string, attributes: JSONObject): void;
}
