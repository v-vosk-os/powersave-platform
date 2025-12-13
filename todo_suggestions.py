"""
PowerSave To-Do Suggestions Module

Generates personalized energy-saving task suggestions based on:
- User activity patterns
- Time of day/season
- Gamification progress
- Kids Program participation
- Saving session history
"""

from datetime import datetime, time
from typing import List, Dict, Optional
from enum import Enum


class SuggestionCategory(Enum):
    """Categories for to-do suggestions"""
    ENERGY_SAVING = "energy_saving"
    SAVING_SESSION = "saving_session"
    GAMIFICATION = "gamification"
    KIDS_PROGRAM = "kids_program"
    SOCIAL_SOLIDARITY = "social_solidarity"
    WASTE_WALLET = "waste_wallet"


class SuggestionPriority(Enum):
    """Priority levels for suggestions"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TodoSuggestion:
    """Represents a single to-do suggestion"""

    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        category: SuggestionCategory,
        priority: SuggestionPriority,
        icon: str,
        estimated_savings_kwh: Optional[float] = None,
        green_points_reward: Optional[int] = None,
        action_url: Optional[str] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.category = category.value
        self.priority = priority.value
        self.icon = icon
        self.estimated_savings_kwh = estimated_savings_kwh
        self.green_points_reward = green_points_reward
        self.action_url = action_url

    def to_dict(self) -> Dict:
        """Convert suggestion to dictionary format"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "icon": self.icon,
            "estimated_savings_kwh": self.estimated_savings_kwh,
            "green_points_reward": self.green_points_reward,
            "action_url": self.action_url
        }


class TodoSuggestionEngine:
    """Engine for generating personalized to-do suggestions"""

    def __init__(self):
        self.base_suggestions = self._initialize_base_suggestions()

    def _initialize_base_suggestions(self) -> List[TodoSuggestion]:
        """Initialize base suggestion templates"""
        return [
            # Energy Saving Suggestions
            TodoSuggestion(
                id="es_01",
                title="Schedule Today's Saving Session",
                description="Plan a 2-hour energy-saving session during off-peak hours (2pm-4pm recommended)",
                category=SuggestionCategory.SAVING_SESSION,
                priority=SuggestionPriority.HIGH,
                icon="⚡",
                estimated_savings_kwh=1.5,
                green_points_reward=50,
                action_url="/saving-sessions/schedule"
            ),
            TodoSuggestion(
                id="es_02",
                title="Unplug Vampire Devices",
                description="Check for devices on standby mode and unplug chargers not in use",
                category=SuggestionCategory.ENERGY_SAVING,
                priority=SuggestionPriority.MEDIUM,
                icon="🔌",
                estimated_savings_kwh=0.5,
                green_points_reward=20
            ),
            TodoSuggestion(
                id="es_03",
                title="Adjust AC Temperature",
                description="Set your AC to 24-26°C to optimize energy use while staying comfortable",
                category=SuggestionCategory.ENERGY_SAVING,
                priority=SuggestionPriority.HIGH,
                icon="❄️",
                estimated_savings_kwh=2.0,
                green_points_reward=30
            ),
            TodoSuggestion(
                id="es_04",
                title="Use Natural Light",
                description="Open curtains and turn off unnecessary lights during daylight hours",
                category=SuggestionCategory.ENERGY_SAVING,
                priority=SuggestionPriority.LOW,
                icon="☀️",
                estimated_savings_kwh=0.3,
                green_points_reward=15
            ),

            # Gamification Suggestions
            TodoSuggestion(
                id="gm_01",
                title="Water Your Green Garden",
                description="Check on your virtual plants and help them grow with your energy savings",
                category=SuggestionCategory.GAMIFICATION,
                priority=SuggestionPriority.MEDIUM,
                icon="🌱",
                green_points_reward=10,
                action_url="/garden"
            ),
            TodoSuggestion(
                id="gm_02",
                title="Complete Active Challenge",
                description="Join this week's community challenge to earn bonus Green Points",
                category=SuggestionCategory.GAMIFICATION,
                priority=SuggestionPriority.MEDIUM,
                icon="🏆",
                green_points_reward=100,
                action_url="/challenges"
            ),
            TodoSuggestion(
                id="gm_03",
                title="Check Your Leaderboard Position",
                description="See how you rank among other PowerSavers in your municipality",
                category=SuggestionCategory.GAMIFICATION,
                priority=SuggestionPriority.LOW,
                icon="📊",
                action_url="/leaderboard"
            ),

            # Kids Program Suggestions
            TodoSuggestion(
                id="kp_01",
                title="Light Patrol Mission (Ages 4-7)",
                description="Help Fotis the Firefly find lights left on in empty rooms",
                category=SuggestionCategory.KIDS_PROGRAM,
                priority=SuggestionPriority.HIGH,
                icon="🔦",
                green_points_reward=25,
                action_url="/kids/missions"
            ),
            TodoSuggestion(
                id="kp_02",
                title="Vampire Hunt Mission (Ages 8-12)",
                description="Find all the energy vampires (devices on standby) in your home",
                category=SuggestionCategory.KIDS_PROGRAM,
                priority=SuggestionPriority.MEDIUM,
                icon="🦇",
                estimated_savings_kwh=0.8,
                green_points_reward=40,
                action_url="/kids/missions"
            ),
            TodoSuggestion(
                id="kp_03",
                title="Temperature Check Mission",
                description="Learn about optimal AC and heating settings with interactive games",
                category=SuggestionCategory.KIDS_PROGRAM,
                priority=SuggestionPriority.MEDIUM,
                icon="🌡️",
                green_points_reward=30,
                action_url="/kids/missions"
            ),

            # Social Solidarity Suggestions
            TodoSuggestion(
                id="ss_01",
                title="Donate to Solidarity Fund",
                description="Help vulnerable households by donating some of your waste fee credits",
                category=SuggestionCategory.SOCIAL_SOLIDARITY,
                priority=SuggestionPriority.LOW,
                icon="❤️",
                action_url="/waste-wallet/donate"
            ),
            TodoSuggestion(
                id="ss_02",
                title="Share Your Energy Story",
                description="Inspire others by sharing your energy-saving success story",
                category=SuggestionCategory.SOCIAL_SOLIDARITY,
                priority=SuggestionPriority.LOW,
                icon="📢",
                green_points_reward=50
            ),

            # Waste Wallet Suggestions
            TodoSuggestion(
                id="ww_01",
                title="Check Your Waste Wallet Balance",
                description="View your accumulated waste fee credits from energy savings",
                category=SuggestionCategory.WASTE_WALLET,
                priority=SuggestionPriority.MEDIUM,
                icon="💰",
                action_url="/waste-wallet"
            ),
            TodoSuggestion(
                id="ww_02",
                title="Review Monthly Savings Report",
                description="See how much you've saved in energy and waste fees this month",
                category=SuggestionCategory.WASTE_WALLET,
                priority=SuggestionPriority.LOW,
                icon="📈",
                action_url="/dashboard"
            ),
        ]

    def get_personalized_suggestions(
        self,
        user_data: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Generate personalized to-do suggestions for a user

        Args:
            user_data: Optional user context data including:
                - has_kids: bool
                - last_session_date: datetime
                - active_challenges: List[str]
                - garden_needs_watering: bool
                - time_of_day: str
                - season: str
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries
        """
        current_hour = datetime.now().hour
        suggestions = []

        # Time-based filtering
        if current_hour >= 6 and current_hour < 12:
            # Morning suggestions
            suggestions.extend([
                s for s in self.base_suggestions
                if s.id in ["es_04", "es_02", "ww_02", "kp_01"]
            ])
        elif current_hour >= 12 and current_hour < 18:
            # Afternoon suggestions
            suggestions.extend([
                s for s in self.base_suggestions
                if s.id in ["es_01", "es_03", "gm_01", "kp_02"]
            ])
        else:
            # Evening suggestions
            suggestions.extend([
                s for s in self.base_suggestions
                if s.id in ["es_02", "gm_02", "ww_01", "ss_01"]
            ])

        # User-specific filtering
        if user_data:
            # Add kids program suggestions if user has children
            if user_data.get("has_kids", False):
                kid_suggestions = [
                    s for s in self.base_suggestions
                    if s.category == SuggestionCategory.KIDS_PROGRAM.value
                ]
                suggestions.extend(kid_suggestions[:2])

            # Remind about saving session if none scheduled today
            if user_data.get("last_session_date") != datetime.now().date():
                session_suggestion = next(
                    (s for s in self.base_suggestions if s.id == "es_01"),
                    None
                )
                if session_suggestion and session_suggestion not in suggestions:
                    suggestions.insert(0, session_suggestion)

            # Add garden reminder if plants need watering
            if user_data.get("garden_needs_watering", False):
                garden_suggestion = next(
                    (s for s in self.base_suggestions if s.id == "gm_01"),
                    None
                )
                if garden_suggestion and garden_suggestion not in suggestions:
                    suggestions.insert(0, garden_suggestion)

            # Highlight active challenges
            if user_data.get("active_challenges", []):
                challenge_suggestion = next(
                    (s for s in self.base_suggestions if s.id == "gm_02"),
                    None
                )
                if challenge_suggestion and challenge_suggestion not in suggestions:
                    suggestions.insert(1, challenge_suggestion)

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s.id not in seen:
                seen.add(s.id)
                unique_suggestions.append(s)

        # Sort by priority (HIGH > MEDIUM > LOW)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unique_suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))

        # Limit results
        return [s.to_dict() for s in unique_suggestions[:limit]]

    def get_suggestions_by_category(
        self,
        category: SuggestionCategory
    ) -> List[Dict]:
        """Get all suggestions for a specific category"""
        return [
            s.to_dict()
            for s in self.base_suggestions
            if s.category == category.value
        ]

    def get_quick_wins(self) -> List[Dict]:
        """Get high-impact, easy-to-complete suggestions"""
        quick_wins = [
            s for s in self.base_suggestions
            if s.estimated_savings_kwh and s.estimated_savings_kwh >= 0.5
            and s.priority == SuggestionPriority.HIGH.value
        ]
        return [s.to_dict() for s in quick_wins[:3]]


# Singleton instance
suggestion_engine = TodoSuggestionEngine()


def get_daily_suggestions(user_data: Optional[Dict] = None) -> Dict:
    """
    Main function to get daily to-do suggestions

    Returns structured response with suggestions and metadata
    """
    suggestions = suggestion_engine.get_personalized_suggestions(user_data)
    quick_wins = suggestion_engine.get_quick_wins()

    total_potential_savings = sum(
        s.get("estimated_savings_kwh", 0)
        for s in suggestions
        if s.get("estimated_savings_kwh")
    )

    total_potential_points = sum(
        s.get("green_points_reward", 0)
        for s in suggestions
        if s.get("green_points_reward")
    )

    return {
        "date": datetime.now().isoformat(),
        "suggestions": suggestions,
        "quick_wins": quick_wins,
        "summary": {
            "total_suggestions": len(suggestions),
            "potential_energy_savings_kwh": round(total_potential_savings, 2),
            "potential_green_points": total_potential_points,
            "categories_covered": len(set(s["category"] for s in suggestions))
        }
    }


if __name__ == "__main__":
    # Example usage
    print("=== PowerSave To-Do Suggestions Demo ===\n")

    # Example 1: Default suggestions
    print("1. Default Daily Suggestions:")
    result = get_daily_suggestions()
    print(f"   Total: {result['summary']['total_suggestions']} suggestions")
    print(f"   Potential savings: {result['summary']['potential_energy_savings_kwh']} kWh")
    print(f"   Potential points: {result['summary']['potential_green_points']} GP\n")

    # Example 2: User with kids
    print("2. Suggestions for User with Kids:")
    user_with_kids = {
        "has_kids": True,
        "garden_needs_watering": True,
        "active_challenges": ["summer-cooling-challenge"]
    }
    result = get_daily_suggestions(user_with_kids)
    for i, s in enumerate(result['suggestions'], 1):
        print(f"   {i}. [{s['priority'].upper()}] {s['title']}")
        print(f"      {s['description']}")
        if s.get('estimated_savings_kwh'):
            print(f"      💡 Savings: {s['estimated_savings_kwh']} kWh")
        if s.get('green_points_reward'):
            print(f"      🌟 Points: {s['green_points_reward']} GP")
        print()
