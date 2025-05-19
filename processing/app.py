"""
REST API server for analyzer.

From: https://github.com/microsoft/presidio/blob/main/presidio-analyzer/app.py
"""
import json
import logging
import os
from logging.config import fileConfig
from pathlib import Path

from flask import Flask, Response, jsonify, request
from presidio_analyzer import AnalyzerEngine, AnalyzerRequest
from utils.engine_factory import create_analyzer_engine
from werkzeug.exceptions import HTTPException

from core.flair_recognizer import FlairRecognizer
from dotenv import load_dotenv

DEFAULT_PORT = "3000"

LOGGING_CONF_FILE = "logging.ini"

WELCOME_MESSAGE = r"""
    
 ________  ___  ___  ________  ________  ________     
|\   ____\|\  \|\  \|\   __  \|\   __  \|\   ___ \    
\ \  \___|\ \  \\\  \ \  \|\  \ \  \|\  \ \  \_|\ \   
 \ \  \  __\ \  \\\  \ \   __  \ \   _  _\ \  \ \\ \  
  \ \  \|\  \ \  \\\  \ \  \ \  \ \  \\  \\ \  \_\\ \ 
   \ \_______\ \_______\ \__\ \__\ \__\\ _\\ \_______\
    \|_______|\|_______|\|__|\|__|\|__|\|__|\|_______|
       
                                                      
"""

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

class Server:
    """HTTP Server for calling Custom Presidio Analyzer."""

    def __init__(self):
        # Init logging
        fileConfig(Path(Path(__file__).parent / "config", LOGGING_CONF_FILE))
        self.logger = logging.getLogger("guard-analyzer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = Flask(__name__)

        # Init the analyzer engine
        self.logger.info("Initializing analyzer engine...")
        self.engine:AnalyzerEngine = create_analyzer_engine()
    
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Analyzer service is up"

        @self.app.route("/analyze", methods=["POST"])
        def analyze():
            """Execute the analyzer function."""
            # Parse the request params
            request_json = request.get_json()

            if not request_json:
                return jsonify(error="Invalid JSON"), 400
            
            if 'text' not in request_json:
                return jsonify(error="No text provided"), 400
            
            if 'language' not in request_json:
                return jsonify(error="No language provided"), 400
            
            try:
                req_data = AnalyzerRequest(request_json)
                
                recognizer_result_list = self.engine.analyze(
                    text=req_data.text,
                    language=req_data.language,
                )

                return Response(
                    json.dumps(
                        recognizer_result_list,
                        # security measure as the o doesn't always have a proper result object, due to unexpected behaviour of the custom analyzer engine. 
                        default=lambda o: o.to_dict() if hasattr(o, "to_dict") else str(o),
                        sort_keys=True,
                    ),
                    content_type="application/json",
                )
            except TypeError as te:
                error_msg = (
                    f"Failed to parse /analyze request "
                    f"for AnalyzerEngine.analyze(). {te.args[0]}"
                )
                self.logger.error(error_msg)
                return jsonify(error=error_msg), 400

            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.analyze(). {e}"
                )
                return jsonify(error=str(e)), 500

        @self.app.route("/recognizers", methods=["GET"])
        def recognizers() -> tuple[Response, int]:
            """Return a list of supported recognizers."""
            language = request.args.get("language")
            if not language:
                return jsonify(error="No language provided"), 400

            try:
                recognizers_list = self.engine.get_recognizers(language)
                # Use str() instead of direct name access to handle MagicMock objects
                names = [str(o.name) for o in recognizers_list]
                return jsonify(names), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.get_recognizers(). {e}"
                )
                return jsonify(error=str(e)), 500

        @self.app.route("/supportedentities", methods=["GET"])
        def supported_entities() -> tuple[Response, int]:
            """Return a list of supported entities."""
            language = request.args.get("language")
            try:
                entities_list = self.engine.get_supported_entities(language)
                return jsonify(entities_list), 200
            except Exception as e:
                self.logger.error(
                    f"A fatal error occurred during execution of "
                    f"AnalyzerEngine.supported_entities(). {e}"
                )
                return jsonify(error=e.args[0]), 500

        @self.app.errorhandler(HTTPException)
        def http_exception(e):
            return jsonify(error=e.description), e.code

def create_app(): # noqa
    server = Server()
    return server.app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    app.run(host="0.0.0.0", port=port)