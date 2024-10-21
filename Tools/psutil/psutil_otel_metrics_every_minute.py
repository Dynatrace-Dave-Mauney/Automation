import json
import psutil
import time

from opentelemetry.sdk.resources import Resource

# Import exporters
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

# Metric imports
from opentelemetry import metrics as metrics
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram, ObservableCounter, \
    ObservableUpDownCounter
from opentelemetry.metrics import set_meter_provider, get_meter_provider

from Reuse import environment


def send_otel_metrics():
    meter = get_meter_provider().get_meter("cpu_meter", "1.0")

    cpu_percent_metric = meter.create_gauge(
    # cpu_percent_metric = meter.create_counter(
        name="raspberry_cpu_percent_gauge",
        description="Raspberry CPU Percent Gauge"
    )
    memory_used_percent_metric = meter.create_gauge(
    # cpu_percent_metric = meter.create_counter(
        name="raspberry_memory_used_percent_gauge",
        description="Raspberry Memory Used Percent Gauge"
    )
    attributes = {}

    while True:
        cpu_percent = psutil.cpu_percent(4)
        memory_used_percent = psutil.virtual_memory()[2]
        memory_used = psutil.virtual_memory()[3] / 1000000000
        # cpu_percent_metric.add(cpu_percent, attributes)
        cpu_percent_metric.set(cpu_percent, attributes)
        print(cpu_percent, cpu_percent_metric)
        memory_used_percent_metric.set(memory_used_percent, attributes)
        print(cpu_percent, cpu_percent_metric)
        print(memory_used_percent, memory_used_percent_metric)
        time.sleep(5)

def otel_setup():
    # ===== GENERAL SETUP =====

    configuration_file = 'configurations.yaml'

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
        "service.name": "psutil_otel_metrics",
        "service.version": "1.0",
    })
    resource = Resource.create(merged)

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


if __name__ == '__main__':
    otel_setup()
    send_otel_metrics()
