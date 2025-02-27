from flask import Flask, request
import logging
import os
import socket

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import set_logger_provider

app = Flask(__name__)


# fallback if no var set we get from docker instead
instance_id = os.getenv("INSTANCE_ID", socket.gethostname())

logger_provider = LoggerProvider(
    resource=Resource.create(
        {
            "service.name": "flask-dummy",
            "service.instance.id": instance_id,
        }
    ),
)
set_logger_provider(logger_provider)

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "grafana-alloy:4317")

otlp_exporter = OTLPLogExporter(endpoint=OTLP_ENDPOINT, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))


otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
#logging.getLogger().addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)


logger = logging.getLogger("flask-dummy")
logger.setLevel(logging.DEBUG)
logger.addHandler(otel_handler)

@app.route('/get')
def get():
    logger.warning("Received GET request")
    return {'success': True}

@app.route('/post')
def post():
    logger.info("Received POST request")
    return {'success': True}

@app.route('/health')
def health():
    logger.info("Receved Health request")
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
