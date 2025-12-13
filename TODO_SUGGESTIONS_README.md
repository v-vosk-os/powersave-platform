# PowerSave To-Do Suggestions Feature

## Overview

The To-Do Suggestions feature provides personalized, actionable energy-saving tasks to PowerSave users. It combines intelligent recommendations with gamification elements to drive user engagement and energy savings.

## Features

### 🎯 Personalized Recommendations
- **Time-aware suggestions**: Different tasks recommended based on time of day
- **User context**: Adapts to user profile (kids, garden, challenges)
- **Priority-based**: Tasks ranked by impact (High/Medium/Low)

### 📊 Six Suggestion Categories
1. **Energy Saving** - Direct energy reduction tasks
2. **Saving Sessions** - Scheduled energy-saving windows
3. **Gamification** - Green Garden, badges, challenges
4. **Kids Program** - Age-appropriate missions (4-7, 8-12)
5. **Social Solidarity** - Community engagement
6. **Waste Wallet** - Financial tracking

### 💡 Smart Features
- **Estimated savings**: Shows potential kWh reduction
- **Green Points rewards**: Gamification incentives
- **Quick Wins**: High-impact, easy tasks
- **Action links**: Deep links to relevant features

## API Endpoints

### GET `/api/todo-suggestions`
Get personalized daily suggestions

**Query Parameters:**
- `limit` (int): Maximum suggestions (default: 5)
- `has_kids` (bool): User has children
- `garden_needs_watering` (bool): Virtual garden status
- `active_challenges` (array): Active challenge IDs

**Response:**
```json
{
  "date": "2025-12-13T...",
  "suggestions": [
    {
      "id": "es_01",
      "title": "Schedule Today's Saving Session",
      "description": "Plan a 2-hour energy-saving session...",
      "category": "saving_session",
      "priority": "high",
      "icon": "⚡",
      "estimated_savings_kwh": 1.5,
      "green_points_reward": 50,
      "action_url": "/saving-sessions/schedule"
    }
  ],
  "quick_wins": [...],
  "summary": {
    "total_suggestions": 5,
    "potential_energy_savings_kwh": 4.3,
    "potential_green_points": 130,
    "categories_covered": 4
  }
}
```

### GET `/api/todo-suggestions/quick-wins`
Get high-impact quick win suggestions

**Response:**
```json
{
  "quick_wins": [...],
  "total": 3
}
```

### GET `/api/todo-suggestions/category/<category>`
Get suggestions by category

**Categories:**
- `energy_saving`
- `saving_session`
- `gamification`
- `kids_program`
- `social_solidarity`
- `waste_wallet`

## Frontend Integration

### Standalone Page
Access the full to-do suggestions interface at:
```
http://localhost:5000/todo_suggestions.html
```

### Embedding in Mobile App
```javascript
// Fetch suggestions
const response = await fetch('/api/todo-suggestions?has_kids=true&limit=5');
const data = await response.json();

// Display suggestions
data.suggestions.forEach(suggestion => {
  renderSuggestionCard(suggestion);
});
```

### User Personalization
```javascript
// Update filters
const params = new URLSearchParams({
  has_kids: userProfile.hasChildren,
  garden_needs_watering: gardenStatus.needsWater,
  active_challenges: userChallenges.map(c => c.id),
  limit: 10
});
```

## Suggestion Logic

### Time-Based Recommendations
- **Morning (6am-12pm)**: Natural light, unplug devices, kids missions
- **Afternoon (12pm-6pm)**: Saving sessions, AC optimization, garden
- **Evening (6pm-12am)**: Review savings, challenges, donations

### Priority Calculation
1. **High Priority**: Direct energy savings, scheduled sessions
2. **Medium Priority**: Gamification, kids program, challenges
3. **Low Priority**: Social features, reviews, leaderboards

### Personalization Factors
- **User Profile**: Children, household size, energy patterns
- **Historical Data**: Past sessions, baseline consumption
- **Gamification State**: Garden status, active challenges
- **Seasonal Context**: Summer cooling vs winter heating

## Example Suggestions

### Energy Saving
```
⚡ Schedule Today's Saving Session
   → 1.5 kWh potential savings
   → 50 Green Points reward
```

### Kids Program
```
🔦 Light Patrol Mission (Ages 4-7)
   → Help Fotis find lights left on
   → 25 Green Points reward
```

### Quick Wins
```
❄️ Adjust AC Temperature
   → Set to 24-26°C
   → 2.0 kWh potential savings
   → 30 Green Points reward
```

## Integration with PowerSave Ecosystem

### Saving Sessions
- Prompts users to schedule sessions during optimal times
- Links directly to session creation interface

### Green Garden
- Reminds users when plants need watering
- Connects to virtual garden feature

### Kids Program
- Age-appropriate missions (4-7, 8-12, 13-17)
- Integration with "Fotis the Firefly" mascot

### Waste Wallet
- Highlights accumulated credits
- Encourages donations to Solidarity Fund

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic suggestion engine
- ✅ Time-based recommendations
- ✅ Six categories
- ✅ Priority system

### Phase 2 (Planned)
- [ ] Machine learning personalization
- [ ] Historical pattern analysis
- [ ] Weather-based suggestions
- [ ] Social comparison insights

### Phase 3 (Future)
- [ ] Push notifications
- [ ] Smart home integration
- [ ] Predictive scheduling
- [ ] AI-powered coaching

## Technical Details

### Dependencies
- Python 3.10+
- Flask for API endpoints
- No external ML libraries (uses rule-based logic)

### Performance
- Suggestion generation: <10ms
- API response time: <50ms
- Cache-friendly design

### Scalability
- Stateless suggestion engine
- Can be extended with user-specific database queries
- Ready for Redis caching integration

## Testing

Run the demo:
```bash
python todo_suggestions.py
```

Start the server:
```bash
python server.py
```

Access the UI:
```
http://localhost:5000/todo_suggestions.html
```

## Code Structure

```
todo_suggestions.py
├── SuggestionCategory (enum)
├── SuggestionPriority (enum)
├── TodoSuggestion (class)
└── TodoSuggestionEngine (class)
    ├── _initialize_base_suggestions()
    ├── get_personalized_suggestions()
    ├── get_suggestions_by_category()
    └── get_quick_wins()
```

## Best Practices

1. **Keep suggestions actionable**: Each task should have clear next steps
2. **Balance variety**: Mix high-effort and low-effort tasks
3. **Update regularly**: Refresh suggestions based on completed actions
4. **Track completion**: Measure which suggestions drive most engagement
5. **A/B test**: Experiment with messaging and timing

## Contributing

To add new suggestions:
1. Add to `_initialize_base_suggestions()` in `todo_suggestions.py`
2. Assign appropriate category, priority, and rewards
3. Update frontend icons and styling if needed
4. Test with various user profiles

## License

Part of the PowerSave Cyprus platform.
