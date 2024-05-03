import os

from opentelemetry import trace

# Check which protocol we should be using for our logs
protocol = os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "GRPC")
if protocol == "HTTP":
    # Import the HTTP OTLP Protocol
    from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter,
    )
else:
    # Fall back to GRPC by default
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
    )
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class DirectWriteLoggingHandler(LoggingHandler):
    def __init__(self, *args, **kwargs):
        configs = self._load_settings()

        trace.set_tracer_provider(TracerProvider())
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )

        log_provider = LoggerProvider(
            resource=Resource.create(
                {
                    "tag" : configs["tag"],
                },
            ),
        )
        set_logger_provider(log_provider)

        if os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "GRPC") == "HTTP":
            exporter = OTLPLogExporter(
                endpoint=configs["endpoint"],
            )
        else:
            exporter = OTLPLogExporter(
                endpoint=configs["endpoint"],
                insecure=not configs["is_secure"],
            )
        log_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

        super(__class__, self).__init__(logger_provider=log_provider)
    
    def _load_settings(self):
        """load configuration from settings.py and return a dict"""
        config = {
            "endpoint": self._load_settings_option("OTLP_LOGGING_ENDPOINT", "http://localhost:4317"),
            "is_secure": self._load_settings_option("OTLP_IS_SECURE", True),
            "tag": self._load_settings_option("OTLP_TAG", "localhost debug"),
        }

        return config

    def _load_settings_option(self, var, default=None):
        """loads a variable from djangos settings. If the variable is not defined, and a default value is passed
        over with the call, default value is returned. If no default value is specified, the variable is required
        and a ImproperlyConfigured Exception is raised"""

        try:
            #load and return
            return getattr(settings, var)
        except AttributeError:
            #setting is not defined
            if default is not None:
                #but we have a default value that is not None. return it
                return default
            #setting is required but could not be loaded, print to stderr
            raise ImproperlyConfigured("Missing %s in settings. otlp exporter could not be loaded." % var)
