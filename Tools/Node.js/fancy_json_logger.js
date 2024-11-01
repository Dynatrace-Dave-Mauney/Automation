import { recordInsight } from './lib/dynatrace.js';

import http from "http";

const server = http.createServer(function onRequest(req, res) {
  process.nextTick(() => {
	http.get("http://dynatrace.com")
	recordInsight("TimestampOnlyExample", "timestamp")
	recordInsight("CountExample", "count", undefined, 100)
	recordInsight("TimeTakenExample", "timeTaken", 1000)
  });
}).listen(9001).on("listening", () => setInterval(() => http.get("http://localhost:" + server.address().port), 500));

