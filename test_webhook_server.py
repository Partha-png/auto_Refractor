from flask import Flask, request, jsonify
from src.refactor.engine import Engine
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
engine = Engine(use_groq=True)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook from GitHub or manual testing."""
    try:
        data = request.json
        logger.info(f"Received webhook: {data.get('action', 'unknown')}")
        
        # Simulate PR event
        if data.get('action') == 'opened':
            logger.info("Processing pull request...")
            
            # For demo: analyze test file
            test_file = "test_complex.py"
            if Path(test_file).exists():
                code = Path(test_file).read_text()
            else:
                # Fallback to sample
                test_file = "src/refactor/sample.py"
                code = Path(test_file).read_text()
            
            result = engine.analyze_and_refactor(test_file, code)
            
            response = {
                "status": "success",
                "file": test_file,
                "issues_found": result.get('issues', '').count('Line'),
                "improvement": result.get('scores', {}).get('improvement', 0)
            }
            
            logger.info(f"Analysis complete: {response}")
            return jsonify(response)
        
        return jsonify({"status": "received", "action": data.get('action')})
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "auto-refractor"})

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with info."""
    return jsonify({
        "service": "Auto-Refractor Webhook",
        "endpoints": {
            "/webhook": "POST - Handle GitHub webhooks",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    logger.info("Starting Auto-Refractor webhook server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
