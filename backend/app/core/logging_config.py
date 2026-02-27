import atexit
import datetime as dt
import json
import logging
import logging.config
import pathlib
from typing import override

from app.core.config import APP_ENV, LOG_LEVEL, PROJECT_NAME, VERSION

logger = logging.getLogger('anonify')
logger.setLevel(LOG_LEVEL)


def setup_logging():
    loggers = (
        'uvicorn',
        'uvicorn.access',
        'uvicorn.error',
        'fastapi',
        'asyncio',
        'starlette',
    )

    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.setLevel(LOG_LEVEL)
        logging_logger.handlers = []
        logging_logger.propagate = True

    config_file = pathlib.Path(__file__).parent / 'logging_config.json'
    with open(config_file) as f:
        config = json.load(f)

    # Ensure log directories exist
    handlers = config.get('handlers', {})
    for handler_config in handlers.values():
        if 'filename' in handler_config:
            log_file_path = pathlib.Path(handler_config['filename'])
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(config)

    queue_handler = logging.getHandlerByName('queue')
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore


LOG_RECORD_BUILTIN_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
    'taskName',
}


class ColoredFormatter(logging.Formatter):
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'  # Reset color
    BOLD = '\033[1m'

    def __init__(self, *args, use_colors: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors

    @override
    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors:
            original_levelname = record.levelname
            color = self.COLORS.get(original_levelname, '')
            record.levelname = (
                f'{color}{self.BOLD}{original_levelname}{self.RESET}'
            )
            formatted = super().format(record)
            # Restore original levelname to avoid affecting other handlers
            record.levelname = original_levelname
            return formatted
        return super().format(record)


class MyJSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            'message': record.getMessage(),
            'timestamp': dt.datetime.fromtimestamp(
                record.created, tz=dt.UTC
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields['exc_info'] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields['stack_info'] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class MySerilogFormatter(logging.Formatter):
    """
    Serilog-compatible JSON formatter with optional Elastic Common Schema (ECS) version.

    Output shape (common Serilog JSON conventions):
      - Timestamp (ISO-8601, UTC, milliseconds, with 'Z')
      - Level (Verbose/Debug/Information/Warning/Error/Fatal)
      - MessageTemplate
      - RenderedMessage
      - Exception (optional)
      - SourceContext (logger name)
      - Properties (custom/extra fields + useful context + default app metadata)
    """

    _LEVEL_MAP = {
        'NOTSET': 'Verbose',
        'DEBUG': 'Debug',
        'INFO': 'Information',
        'WARNING': 'Warning',
        'ERROR': 'Error',
        'CRITICAL': 'Fatal',
    }

    def __init__(
        self,
        *,
        include_rendered_message: bool = True,
        include_message_template: bool = True,
        include_ecs_version: str | None = '8.10.0',
    ):
        super().__init__()
        self.include_rendered_message = include_rendered_message
        self.include_message_template = include_message_template
        self.include_ecs_version = include_ecs_version

    @override
    def format(self, record: logging.LogRecord) -> str:
        payload = self._prepare_serilog_dict(record)
        return json.dumps(payload, default=str, ensure_ascii=False)

    def _prepare_serilog_dict(self, record: logging.LogRecord) -> dict:
        ts = (
            dt.datetime.fromtimestamp(record.created, tz=dt.UTC)
            .isoformat(timespec='milliseconds')
            .replace('+00:00', 'Z')
        )

        level = self._LEVEL_MAP.get(record.levelname, record.levelname.title())
        if isinstance(level, str):
            level = level.replace('\u001b[31m', '').replace('\u001b[39m', '')

        event: dict = {
            'Timestamp': ts,
            'Level': level,
            'SourceContext': record.name,
        }

        if self.include_ecs_version:
            event['ecs.version'] = self.include_ecs_version

        if self.include_message_template:
            try:
                event['MessageTemplate'] = (
                    record.msg
                    if isinstance(record.msg, str)
                    else str(record.msg)
                )
            except Exception:
                event['MessageTemplate'] = '<unavailable>'

        if self.include_rendered_message:
            event['RenderedMessage'] = record.getMessage()

        if record.exc_info is not None:
            event['Exception'] = self.formatException(record.exc_info)

        props: dict = {
            # Useful context
            'Module': record.module,
            'Function': record.funcName,
            'Line': record.lineno,
            'ProcessId': record.process,
            'ThreadId': record.thread,
            'ThreadName': record.threadName,
        }

        if record.stack_info is not None:
            props['StackTrace'] = self.formatStack(record.stack_info)

        # Attach any extras passed via logger(..., extra={...})
        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                props[key] = val

        event['Properties'] = props
        event['service'] = {
            'name': PROJECT_NAME,
            'version': VERSION,
        }
        event['environment'] = APP_ENV
        return event


class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO


class ErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno > logging.INFO


class DuplicateFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.seen = set()

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record_tuple = (record.name, record.levelno, message)
        if record_tuple in self.seen:
            return False
        self.seen.add(record_tuple)
        return True


class LoggerNameFilter(logging.Filter):
    def __init__(
        self,
        exclude_names: list[str] | None = None,
        include_names: list[str] | None = None,
        exclude_prefixes: list[str] | None = None,
    ):
        super().__init__()
        self.exclude_names = set(exclude_names) if exclude_names else set()
        self.include_names = set(include_names) if include_names else None
        self.exclude_prefixes = exclude_prefixes or []

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        logger_name = record.name

        # If include_names is set, only allow those loggers
        if self.include_names is not None:
            return logger_name in self.include_names

        # Exclude specific logger names
        if logger_name in self.exclude_names:
            return False

        # Exclude loggers with matching prefixes
        for prefix in self.exclude_prefixes:
            if logger_name.startswith(prefix):
                return False

        return True
