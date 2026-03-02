import logging
import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
)  # noqa: E402
import pytest  # noqa: E402
import yaml  # noqa: E402
from csvimport import get_format, load_config, setup_logging  # noqa: E402

# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


def test_load_config_no_path():
    assert load_config(None) == {}


def test_load_config_empty_string():
    assert load_config("") == {}


def test_load_config_valid(tmp_path):
    conf = tmp_path / "test.conf"
    conf.write_text("organizations:\n  org1:\n    key_fields: [col1]\n")
    result = load_config(str(conf))
    assert result["organizations"]["org1"]["key_fields"] == ["col1"]


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.conf")


def test_load_config_malformed_yaml(tmp_path):
    conf = tmp_path / "bad.conf"
    conf.write_text("organizations:\n  org1: [\n")  # unclosed bracket
    with pytest.raises(yaml.YAMLError):
        load_config(str(conf))


# ---------------------------------------------------------------------------
# get_format
# ---------------------------------------------------------------------------

SAMPLE_CONFIG = {
    "organizations": {
        "myorg": {
            "input_format": ["col1", "col2"],
            "output_format": ["col1", "col2"],
        }
    }
}


def test_get_format_cli_override_takes_priority():
    cli = ["A", "B"]
    result = get_format(SAMPLE_CONFIG, "myorg", "input_format", cli)
    assert result == ["A", "B"]


def test_get_format_falls_back_to_config():
    result = get_format(SAMPLE_CONFIG, "myorg", "input_format", None)
    assert result == ["col1", "col2"]


def test_get_format_returns_none_no_cli_no_config():
    result = get_format({}, "myorg", "input_format", None)
    assert result is None


def test_get_format_returns_none_unknown_org():
    result = get_format(SAMPLE_CONFIG, "unknown_org", "input_format", None)
    assert result is None


def test_get_format_returns_none_no_org():
    result = get_format(SAMPLE_CONFIG, None, "input_format", None)
    assert result is None


def test_get_format_returns_none_missing_key():
    result = get_format(SAMPLE_CONFIG, "myorg", "key_fields", None)
    assert result is None


# ---------------------------------------------------------------------------
# setup_logging
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_csvimport_logger():
    """Remove all handlers from the csvimport logger before and after each test."""
    logger = logging.getLogger("csvimport")
    yield
    for h in list(logger.handlers):
        h.close()
        logger.removeHandler(h)


def test_setup_logging_non_debug_creates_file_handler(tmp_path):
    log_file = str(tmp_path / "test.log")
    logger = setup_logging(False, log_file)
    assert logger.name == "csvimport"
    assert logger.level == logging.INFO
    assert logger.debug_mode is False
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    stream_handlers = [
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    assert len(stream_handlers) == 0


def test_setup_logging_debug_adds_stdout_handler(tmp_path):
    log_file = str(tmp_path / "debug.log")
    logger = setup_logging(True, log_file)
    assert logger.level == logging.DEBUG
    assert logger.debug_mode is True
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    stream_handlers = [
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    assert len(stream_handlers) == 1


def test_setup_logging_creates_log_directory(tmp_path):
    log_dir = tmp_path / "nested" / "logs"
    log_file = str(log_dir / "csvimport.log")
    assert not log_dir.exists()
    setup_logging(False, log_file)
    assert log_dir.exists()


def test_setup_logging_no_duplicate_handlers(tmp_path):
    log_file = str(tmp_path / "test.log")
    setup_logging(False, log_file)
    setup_logging(False, log_file)
    logger = logging.getLogger("csvimport")
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1
