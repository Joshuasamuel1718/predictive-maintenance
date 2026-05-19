import logging
from waitress import serve
from api import app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("waitress")

PORT = 5000
HOST = "0.0.0.0"  # Expose to all network interfaces

if __name__ == "__main__":
    logger.info(f"🚀 Starting Predictive Maintenance production server on http://localhost:{PORT}")
    logger.info("Serving React frontend from 'maintenance-dashboard/build'")
    logger.info("Serving Backend API endpoints under /login, /signup, /predict")
    logger.info("Press Ctrl+C to stop the server.")
    
    serve(app, host=HOST, port=PORT, threads=8)
