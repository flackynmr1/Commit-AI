from flask import jsonify
from agents.autonomous_manager import load_tasks

def register_agent_routes(app):
    @app.route("/agent-tasks")
    def agent_tasks():
        return jsonify(load_tasks())