from flask import Flask, send_from_directory, request, jsonify
import os
from todo_suggestions import get_daily_suggestions, suggestion_engine, SuggestionCategory

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    # Placeholder for real LLM integration
    # In a real app, you would call OpenAI or a local model here
    return jsonify({"response": f"Echo from server: {user_message}"})

@app.route('/api/todo-suggestions', methods=['GET'])
def get_todo_suggestions():
    """Get personalized to-do suggestions for the current user"""
    # In a real app, you would get user_id from authentication token
    # and fetch user data from database
    user_data = {
        "has_kids": request.args.get('has_kids', 'false').lower() == 'true',
        "garden_needs_watering": request.args.get('garden_needs_watering', 'false').lower() == 'true',
        "active_challenges": request.args.getlist('active_challenges')
    }

    limit = int(request.args.get('limit', 5))

    result = get_daily_suggestions(user_data)
    result['suggestions'] = result['suggestions'][:limit]

    return jsonify(result)

@app.route('/api/todo-suggestions/category/<category>', methods=['GET'])
def get_suggestions_by_category(category):
    """Get suggestions filtered by category"""
    try:
        cat_enum = SuggestionCategory[category.upper()]
        suggestions = suggestion_engine.get_suggestions_by_category(cat_enum)
        return jsonify({
            "category": category,
            "suggestions": suggestions,
            "total": len(suggestions)
        })
    except KeyError:
        return jsonify({"error": "Invalid category"}), 400

@app.route('/api/todo-suggestions/quick-wins', methods=['GET'])
def get_quick_wins():
    """Get high-impact quick win suggestions"""
    quick_wins = suggestion_engine.get_quick_wins()
    return jsonify({
        "quick_wins": quick_wins,
        "total": len(quick_wins)
    })

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(port=5000, debug=True)