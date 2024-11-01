#
# Manual OTEL Instrumentation:
# https://docs.dynatrace.com/docs/extend-dynatrace/opentelemetry/walkthroughs/python/python-manual
#


import json
import logging

import random

from opentelemetry.sdk.resources import Resource

# Import exporters
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Trace imports
from opentelemetry.trace import set_tracer_provider, get_tracer_provider
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Metric imports
from opentelemetry import metrics as metrics
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram, ObservableCounter, \
    ObservableUpDownCounter
from opentelemetry.metrics import set_meter_provider, get_meter_provider

# Logs import
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

from Reuse import environment

from flask import Flask

app = Flask(__name__)
tracer = get_tracer_provider().get_tracer("hello_world_tracer")


@app.route('/')
def help():
    return 'Use one of these endpoints to exercise OTEL capabilities: "/spans", "/metrics" or "/logs"'


@app.route('/spans')
def spans():
    with tracer.start_as_current_span("Call to /1") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("net.protocol.version", "1.1")
    return 'OTEL span "Call to /spans" for "hello_world_with_otel" service created'


@app.route('/metrics')
def metrics():
    meter = get_meter_provider().get_meter("random_number_meter", "1.0")
    random_number = meter.create_counter(
        name="random_number",
        description="A random number"
    )
    attributes = {"range": "0 to 100"}

    for i in range(100):
        random_integer = random.randint(0, 100)
        print(f'Metric "random_number" added: {random_integer}')
        random_number.add(random_integer, attributes)

    return 'OTEL metric "random_number" created'


@app.route('/logs')
def log():

    for i in range(100):
        logging.critical(f"CRITICAL: OTEL Random Log {random.randint(0, 100)}")
        logging.debug(f"DEBUG: OTEL Random Log {random.randint(0, 100)}")
        logging.error(f"ERROR: OTEL Random Log {random.randint(0, 100)}")
        logging.info(f"INFO: OTEL Random Log {random.randint(0, 100)}")
        logging.fatal(f"FATAL: OTEL Random Log {random.randint(0, 100)}")
    return('OTEL log lines written')


def otel_setup():
    # ===== GENERAL SETUP =====

    configuration_file = 'configurations.yaml'

    DT_API_URL = environment.get_configuration('DT_API_URL', configuration_file=configuration_file)
    DT_API_TOKEN = environment.get_configuration('DT_API_TOKEN', configuration_file=configuration_file)

    print(DT_API_URL, DT_API_TOKEN)

    merged = dict()
    for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json",
                 "/var/lib/dynatrace/enrichment/dt_host_metadata.json"]:
        try:
            data = ''
            with open(name) as f:
                data = json.load(f if name.startswith("/var") else open(f.read()))
                merged.update(data)
        except:
            pass

    merged.update({
        "service.name": "hello_world_with_otel",
        "service.version": "1.0",
    })
    resource = Resource.create(merged)

    # ===== TRACING SETUP =====

    tracer_provider = TracerProvider(sampler=sampling.ALWAYS_ON, resource=resource)
    set_tracer_provider(tracer_provider)

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=DT_API_URL + "/v1/traces",
                headers={
                    "Authorization": "Api-Token " + DT_API_TOKEN
                }
            )
        )
    )

    # ===== METRIC SETUP =====

    exporter = OTLPMetricExporter(
        endpoint=DT_API_URL + "/v1/metrics",
        headers={"Authorization": "Api-Token " + DT_API_TOKEN},
        preferred_temporality={
            Counter: AggregationTemporality.DELTA,
            UpDownCounter: AggregationTemporality.CUMULATIVE,
            Histogram: AggregationTemporality.DELTA,
            ObservableCounter: AggregationTemporality.DELTA,
            ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
        }
    )

    reader = PeriodicExportingMetricReader(exporter)
    provider = MeterProvider(metric_readers=[reader], resource=resource)
    set_meter_provider(provider)

    # ===== LOG SETUP =====

    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(
            endpoint=DT_API_URL + "/v1/logs",
            headers={"Authorization": "Api-Token " + DT_API_TOKEN}
        ))
    )
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

    # Attach OTLP handler to root logger
    logging.getLogger().addHandler(handler)


if __name__ == '__main__':
    # print('before otel_setup')
    otel_setup()
    # print('after otel_setup')
    print('OTEL Setup Seems to Disable Logging to Console so:')
    print('Should be running on http://127.0.0.1:5000/')
    print('Should be running on http://192.168.1.247:5000')
    print('Endpoints: ', 'spans', 'metrics', 'logs')
    app.run('0.0.0.0', 5000)


'''
Alternative Invocation (from command line):
. .venv/bin/activate
sudo pigpiod
# Run the test app
flask --app hello run --host=0.0.0.0
'''
