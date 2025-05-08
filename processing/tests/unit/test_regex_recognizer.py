import pytest
from dotenv import load_dotenv
from pathlib import Path
from utils.engine_factory import create_analyzer_engine, AnalyzerEngine


@pytest.fixture(scope='module')
def setup_engine():
    """
    Setup function is called once, before the yield prepare the data and then yield it.
    After yield the teardown is prepared which is called after all tests, when the scope is set to module.
    """
    print("Setting up the engine...")
    engine = create_analyzer_engine()
    yield engine
    print("Tearing down resources...")
    # Nothing (yet)