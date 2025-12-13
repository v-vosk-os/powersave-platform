from flask import Flask, send_from_directory, request, jsonify
import os
from datetime import datetime
from todo_suggestions import get_daily_suggestions, suggestion_engine, SuggestionCategory
from waste_fee_offset import waste_fee_engine, Municipality

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

# ============================================================================
# Waste Fee Offset API Endpoints
# ============================================================================

@app.route('/api/waste-fee/account/create', methods=['POST'])
def create_waste_fee_account():
    """Create or link municipal waste fee account"""
    data = request.json

    try:
        municipality = Municipality[data['municipality'].upper()]

        account = waste_fee_engine.create_waste_fee_account(
            user_id=data.get('user_id', 'demo_user'),
            property_number=data['property_number'],
            municipality=municipality,
            annual_fee=float(data['annual_fee']),
            owner_name=data['owner_name'],
            address=data['address']
        )

        return jsonify({
            "status": "success",
            "message": "Σύνδεση Υποστατικού επιτυχής!",
            "account": {
                "property_number": account.property_number,
                "municipality": account.municipality.value,
                "annual_fee": account.annual_fee,
                "owner_name": account.owner_name
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/waste-fee/wallet/<user_id>', methods=['GET'])
def get_waste_wallet(user_id):
    """Get waste wallet status"""
    wallet = waste_fee_engine.get_wallet_status(user_id)

    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    progress = waste_fee_engine.get_progress_percentage(user_id)

    return jsonify({
        "balance_eur": round(wallet.balance_eur, 2),
        "annual_goal_eur": wallet.annual_goal_eur,
        "progress_percentage": progress,
        "year_to_date_earnings": round(wallet.year_to_date_earnings, 2),
        "total_sessions_completed": wallet.total_sessions_completed,
        "total_kwh_saved": round(wallet.total_kwh_saved, 2),
        "last_payment_date": wallet.last_payment_date.isoformat() if wallet.last_payment_date else None,
        "last_payment_amount": wallet.last_payment_amount
    })

@app.route('/api/waste-fee/session/complete', methods=['POST'])
def complete_saving_session():
    """Complete a saving session and calculate rewards"""
    data = request.json

    user_id = data.get('user_id', 'demo_user')
    actual_kwh = float(data['actual_kwh'])
    historical_consumption = data.get('historical_consumption', [2.5, 2.3, 2.6, 2.4, 2.5])
    is_double_points = data.get('is_double_points', False)

    session = waste_fee_engine.complete_saving_session(
        user_id=user_id,
        start_time=datetime.now(),
        actual_kwh=actual_kwh,
        historical_consumption=historical_consumption,
        is_double_points=is_double_points
    )

    # Get updated wallet
    wallet = waste_fee_engine.get_wallet_status(user_id)
    progress = waste_fee_engine.get_progress_percentage(user_id)

    message = f"Μπράβο! Κατανάλωσες {session.savings_kwh} kWh λιγότερο από το συνηθισμένο σου. "
    message += f"Κέρδισες €{session.earnings_eur} στο Waste Wallet σου."

    if is_double_points:
        message += " ⭐ DOUBLE POINTS!"

    return jsonify({
        "status": "success",
        "message": message,
        "session": {
            "session_id": session.session_id,
            "baseline_kwh": session.baseline_kwh,
            "actual_kwh": session.actual_kwh,
            "savings_kwh": session.savings_kwh,
            "earnings_eur": session.earnings_eur,
            "is_double_points": session.is_double_points
        },
        "wallet": {
            "new_balance": round(wallet.balance_eur, 2),
            "progress_percentage": progress
        }
    })

@app.route('/api/waste-fee/payment/process', methods=['POST'])
def process_monthly_payment():
    """Process monthly payment to municipality"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')

    result = waste_fee_engine.process_monthly_payment(user_id)
    return jsonify(result)

@app.route('/api/waste-fee/tips', methods=['GET'])
def get_waste_fee_tips():
    """Get energy-saving tips for maximum earnings"""
    time_of_day = request.args.get('time_of_day', type=int)
    tips = waste_fee_engine.get_saving_tips(time_of_day)

    return jsonify({
        "tips": tips,
        "total": len(tips)
    })

@app.route('/api/waste-fee/simulate', methods=['GET'])
def simulate_waste_fee_scenario():
    """Simulate yearly savings scenario"""
    annual_fee = request.args.get('annual_fee', 185.0, type=float)
    sessions_per_week = request.args.get('sessions_per_week', 5, type=int)
    avg_savings_kwh = request.args.get('avg_savings_kwh', 2.0, type=float)

    scenario = waste_fee_engine.simulate_scenario(
        annual_fee=annual_fee,
        sessions_per_week=sessions_per_week,
        avg_savings_per_session_kwh=avg_savings_kwh
    )

    return jsonify(scenario)

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    app.run(port=5000, debug=True)