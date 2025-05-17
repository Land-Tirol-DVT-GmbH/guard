from pathlib import Path
from dotenv import load_dotenv
import pytest
from utils.engine_factory import create_analyzer_engine


load_dotenv(Path(__file__).parent.parent.parent / '.env')

@pytest.fixture(scope='package')
def setup_engine():
    """
    Helper method to setup the Analyzer Engine once for all test files in the *unit* package.
    
    Setup function is called once, before the yield, prepare the data and then yield it.
    After yield the teardown is prepared which is called after all tests, from all files [package].
    """
    print("Setting up the engine...")
    engine = create_analyzer_engine()
    yield engine
    print("Tearing down resources...")
    # Nothing (yet)