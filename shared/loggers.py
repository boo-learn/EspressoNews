import logging
import structlog
import inspect
import pathlib


logging.basicConfig(level=logging.NOTSET)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('celery').setLevel(logging.WARNING)
logging.getLogger('aiormq').setLevel(logging.WARNING)
logging.getLogger('aio_pika').setLevel(logging.WARNING)
logging.getLogger('admin_service').setLevel(logging.WARNING)


class ConsoleStringRenderer(structlog.dev.ConsoleRenderer):
    def _repr(self, val) -> str:
        return str(val)


json_formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.processors.JSONRenderer()
)
struct_formatter = structlog.stdlib.ProcessorFormatter(
    processor=ConsoleStringRenderer(colors=False)
)
logfmt_formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.processors.LogfmtRenderer(
        key_order=['timestamp', 'level', 'event']
    )
)


def get_logger(
    name: str = None,
    level: int = logging.INFO,
    use_console: bool = True,
    filename: str = None,
    file_level: int = None,
    is_async: bool = False,
    **kwargs
):
    if not name:
        frame = inspect.stack()[1]
        name = pathlib.Path(frame.filename).name
    logger = logging.getLogger(name)
    logger.propagate = False
    if use_console:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(struct_formatter)
        logger.addHandler(handler)
    if filename:
        handler = logging.FileHandler(filename=filename)
        handler.setLevel(file_level or level)
        handler.setFormatter(logfmt_formatter)
        logger.addHandler(handler)

    if is_async:
        wrapper_class = structlog.stdlib.AsyncBoundLogger
    else:
        wrapper_class = structlog.stdlib.BoundLogger

    configuration = {
        'processors': [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        'context_class': dict,
        'wrapper_class': wrapper_class,
        'cache_logger_on_first_use': True,
    }

    return structlog.wrap_logger(logger, **configuration, **kwargs)
