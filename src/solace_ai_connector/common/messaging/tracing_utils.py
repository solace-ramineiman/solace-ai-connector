from opentelemetry import trace, propagate
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter


class TracingUtils:
    is_init = False
    tracer = None
    text_map = None

    @staticmethod
    def init_tracing(connection_string, batch_size, queue_size, schedule_delay):
        if TracingUtils.is_init:
            return

        resource = Resource(attributes={
            SERVICE_NAME: "solace_ai_connector"
        })
        provider = TracerProvider(resource=resource)

        if connection_string != "":
            exporter = OTLPSpanExporter(endpoint=connection_string)
        else:
            exporter = InMemorySpanExporter()

        processor = BatchSpanProcessor(exporter,
                                       max_export_batch_size=batch_size,
                                       max_queue_size=queue_size,
                                       schedule_delay_millis=schedule_delay)
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)

        TracingUtils.tracer = trace.get_tracer("solace_ai_connector")
        TracingUtils.text_map = propagate.get_global_textmap()
        TracingUtils.is_init = True

    @staticmethod
    def get_baggage(baggage_str):
        baggage_list = list()

        for baggage_item in baggage_str.split(","):
            baggage_sub_items = baggage_item.split("=")
            baggage_list.append((baggage_sub_items[0], baggage_sub_items[1]))

        return baggage_list