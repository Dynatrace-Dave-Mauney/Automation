const http = require("http");

const server = http.createServer(function onRequest(req, res) {
  process.nextTick(() => {
	console.debug("simple_console_logger: Debug Message");
	console.error("simple_console_logger: Error Message");
	console.log("simple_console_logger: Log Message");
	console.warn("simple_console_logger: Warn Message");
	console.info("simple_console_logger: Info Message");
	console.trace("simple_console_logger: Trace Message");
	http.get("http://dynatrace.com")
    res.end();
  });
}).listen(9001).on("listening", () => setInterval(() => http.get("http://localhost:" + server.address().port), 500));
