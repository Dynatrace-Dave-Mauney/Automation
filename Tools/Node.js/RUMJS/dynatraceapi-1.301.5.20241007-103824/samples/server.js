import http from 'http';
import fs from 'node:fs';

const server = http.createServer(function (req, res) {
	let url = ""
    if (req.url == '/') {
		url = "index.html"
	} else {
		url = req.url.replace("/", "")
	}

	fs.readFile(url, 'utf8', (err, data) => {
		if (err) {
			console.error(err);
			return;
		}
		res.writeHead(200, { 'Content-Type': 'text/html' });
		res.write(data);
		res.end();
	})
}).listen(8080, () => console.log('Server running on port 8080'));
