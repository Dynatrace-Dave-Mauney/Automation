import { recordInsight } from './lib/dynatrace.js';
import http from "http";
import fs from "fs";
import yaml from "js-yaml";

const server = http.createServer(function onRequest(req, res) {
    let count_list = []
    let time_taken_list = []
    let timestamp_list = []

    try {
      const config = yaml.load(fs.readFileSync('configurations.yaml', 'utf8'));
      count_list = config.count_list;
      time_taken_list = config.time_taken_list;
      timestamp_list = config.timestamp_list;
    } catch (e) {
      console.error(e);
    }

    process.nextTick(() => {
        http.get("http://dynatrace.com")
        for (let i = 0; i < count_list.length; i++) {
            recordInsight(count_list[i], "count", undefined, 100)
        }
        for (let i = 0; i < time_taken_list.length; i++) {
            recordInsight(time_taken_list[i], "timeTaken", 1000)
        }
        for (let i = 0; i < timestamp_list.length; i++) {
            recordInsight(timestamp_list[i], "timestamp")
        }
    //	recordInsight("TimestampOnlyExample", "timestamp")
    //	recordInsight("TimeTakenExample", "timeTaken", 1000)
    });
}).listen(9001).on("listening", () => setInterval(() => http.get("http://localhost:" + server.address().port), 500));

