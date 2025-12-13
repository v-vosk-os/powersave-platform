"""
PowerSave Waste Fee Offset Module

Implements the revolutionary Waste Fee Offset system that allows users to pay
their annual municipal waste fees using energy savings.

Πώς να μηδενίσετε τα Τέλη Σκυβάλων σας, κλείνοντας απλά τον διακόπτη.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Municipality(Enum):
    """Cyprus Municipalities"""
    NICOSIA = "nicosia"
    LIMASSOL = "limassol"
    LARNACA = "larnaca"
    PAPHOS = "paphos"
    FAMAGUSTA = "famagusta"


@dataclass
class WasteFeeAccount:
    """Municipal waste fee account information"""
    property_number: str
    municipality: Municipality
    annual_fee: float  # in Euros
    owner_name: str
    address: str


@dataclass
class SavingSession:
    """Represents a single energy-saving session"""
    session_id: str
    start_time: datetime
    end_time: datetime
    baseline_kwh: float  # Expected consumption based on 10-day average
    actual_kwh: float    # Actual consumption during session
    savings_kwh: float   # Difference (baseline - actual)
    earnings_eur: float  # kWh converted to Euros
    is_double_points: bool = False  # Special high-demand days


@dataclass
class WasteWallet:
    """User's waste fee credit wallet"""
    user_id: str
    balance_eur: float
    annual_goal_eur: float
    year_to_date_earnings: float
    total_sessions_completed: int
    total_kwh_saved: float
    last_payment_date: Optional[datetime]
    last_payment_amount: float


class WasteFeeOffsetEngine:
    """
    Core engine for the Waste Fee Offset system

    Converts energy savings (kWh) to waste fee credits (€)
    """

    # Conversion rates (can be adjusted based on policy)
    KWH_TO_EUR_RATE = 0.34  # Cyprus average electricity cost per kWh
    DOUBLE_POINTS_MULTIPLIER = 2.0

    # Session defaults
    TYPICAL_SESSION_DURATION_HOURS = 2
    PEAK_HOURS_START = 17  # 5:00 PM
    PEAK_HOURS_END = 20    # 8:00 PM

    # Baseline calculation
    BASELINE_LOOKBACK_DAYS = 10

    def __init__(self):
        self.sessions_db: List[SavingSession] = []
        self.wallets_db: Dict[str, WasteWallet] = {}
        self.accounts_db: Dict[str, WasteFeeAccount] = {}

    def create_waste_fee_account(
        self,
        user_id: str,
        property_number: str,
        municipality: Municipality,
        annual_fee: float,
        owner_name: str,
        address: str
    ) -> WasteFeeAccount:
        """
        Step 1: Connect municipal waste fee account

        Σύνδεση Υποστατικού - Link property account
        """
        account = WasteFeeAccount(
            property_number=property_number,
            municipality=municipality,
            annual_fee=annual_fee,
            owner_name=owner_name,
            address=address
        )

        self.accounts_db[user_id] = account

        # Initialize wallet with this annual goal
        self.wallets_db[user_id] = WasteWallet(
            user_id=user_id,
            balance_eur=0.0,
            annual_goal_eur=annual_fee,
            year_to_date_earnings=0.0,
            total_sessions_completed=0,
            total_kwh_saved=0.0,
            last_payment_date=None,
            last_payment_amount=0.0
        )

        return account

    def calculate_baseline_consumption(
        self,
        historical_data: List[float],
        time_of_day: int
    ) -> float:
        """
        Calculate expected consumption based on historical patterns

        Uses 10-day average as mentioned in the user guide
        """
        if not historical_data or len(historical_data) < 3:
            # Default baseline if insufficient data
            return 2.0  # 2 kWh for 2-hour session

        # Use last 10 data points or all available
        recent_data = historical_data[-min(10, len(historical_data)):]
        baseline = sum(recent_data) / len(recent_data)

        # Adjust for time of day (peak hours use more energy)
        if self.PEAK_HOURS_START <= time_of_day <= self.PEAK_HOURS_END:
            baseline *= 1.3  # 30% higher during peak hours

        return round(baseline, 2)

    def calculate_session_savings(
        self,
        baseline_kwh: float,
        actual_kwh: float,
        is_double_points: bool = False
    ) -> tuple[float, float]:
        """
        Calculate savings and earnings from a session

        Returns: (savings_kwh, earnings_eur)
        """
        # Energy saved
        savings_kwh = max(0, baseline_kwh - actual_kwh)

        # Convert to Euros
        earnings_eur = savings_kwh * self.KWH_TO_EUR_RATE

        # Apply double points multiplier if applicable
        if is_double_points:
            earnings_eur *= self.DOUBLE_POINTS_MULTIPLIER

        return round(savings_kwh, 2), round(earnings_eur, 2)

    def complete_saving_session(
        self,
        user_id: str,
        start_time: datetime,
        actual_kwh: float,
        historical_consumption: List[float],
        is_double_points: bool = False
    ) -> SavingSession:
        """
        Complete a saving session and credit the wallet

        This simulates the full flow:
        1. Calculate baseline
        2. Compare to actual consumption
        3. Calculate savings and earnings
        4. Credit wallet
        """
        # Calculate baseline
        baseline_kwh = self.calculate_baseline_consumption(
            historical_consumption,
            start_time.hour
        )

        # Calculate savings
        savings_kwh, earnings_eur = self.calculate_session_savings(
            baseline_kwh,
            actual_kwh,
            is_double_points
        )

        # Create session record
        session = SavingSession(
            session_id=f"SES_{user_id}_{start_time.strftime('%Y%m%d%H%M')}",
            start_time=start_time,
            end_time=start_time + timedelta(hours=self.TYPICAL_SESSION_DURATION_HOURS),
            baseline_kwh=baseline_kwh,
            actual_kwh=actual_kwh,
            savings_kwh=savings_kwh,
            earnings_eur=earnings_eur,
            is_double_points=is_double_points
        )

        self.sessions_db.append(session)

        # Credit wallet
        if user_id in self.wallets_db:
            wallet = self.wallets_db[user_id]
            wallet.balance_eur += earnings_eur
            wallet.year_to_date_earnings += earnings_eur
            wallet.total_sessions_completed += 1
            wallet.total_kwh_saved += savings_kwh

        return session

    def get_wallet_status(self, user_id: str) -> Optional[WasteWallet]:
        """Get current wallet status"""
        return self.wallets_db.get(user_id)

    def get_progress_percentage(self, user_id: str) -> float:
        """Calculate progress toward annual waste fee goal"""
        wallet = self.wallets_db.get(user_id)
        if not wallet or wallet.annual_goal_eur == 0:
            return 0.0

        progress = (wallet.balance_eur / wallet.annual_goal_eur) * 100
        return min(100.0, round(progress, 1))

    def process_monthly_payment(self, user_id: str) -> Dict:
        """
        Process automatic monthly payment to municipality

        "Δεν χρειάζεται να κάνετε τίποτα!"
        """
        wallet = self.wallets_db.get(user_id)
        account = self.accounts_db.get(user_id)

        if not wallet or not account:
            return {"error": "User not found"}

        payment_amount = wallet.balance_eur

        if payment_amount <= 0:
            return {
                "status": "no_payment",
                "message": "Δεν υπάρχει διαθέσιμο υπόλοιπο για πληρωμή"
            }

        # Process payment
        wallet.balance_eur = 0.0
        wallet.last_payment_date = datetime.now()
        wallet.last_payment_amount = payment_amount

        remaining_fee = max(0, wallet.annual_goal_eur - wallet.year_to_date_earnings)

        return {
            "status": "success",
            "payment_amount": round(payment_amount, 2),
            "municipality": account.municipality.value,
            "property_number": account.property_number,
            "remaining_annual_fee": round(remaining_fee, 2),
            "progress_percentage": self.get_progress_percentage(user_id),
            "receipt": f"Πληρώθηκε έναντι Τελών Σκυβάλων: €{payment_amount:.2f}"
        }

    def get_saving_tips(self, time_of_day: Optional[int] = None) -> List[Dict]:
        """
        Get personalized energy-saving tips

        Based on "Tips για Μέγιστο Κέρδος" from the guide
        """
        if time_of_day is None:
            time_of_day = datetime.now().hour

        tips = []

        # Peak hours tips (17:00-20:00)
        if self.PEAK_HOURS_START <= time_of_day <= self.PEAK_HOURS_END:
            tips.extend([
                {
                    "icon": "🔥",
                    "title": "Κλείστε τον Θερμοσίφωνα",
                    "description": "Είναι ο μεγαλύτερος καταναλωτής. Κλείστε τον κατά τη διάρκεια των Sessions.",
                    "potential_savings_kwh": 1.5,
                    "priority": "high"
                },
                {
                    "icon": "🍳",
                    "title": "Αποφύγετε τον Φούρνο",
                    "description": "Αποφύγετε τον φούρνο τις ώρες αιχμής (18:00-21:00).",
                    "potential_savings_kwh": 1.0,
                    "priority": "high"
                },
                {
                    "icon": "👕",
                    "title": "Αναβάλετε το Πλυντήριο",
                    "description": "Αναβάλετε τη χρήση του πλυντηρίου/στεγνωτηρίου για αργότερα.",
                    "potential_savings_kwh": 1.2,
                    "priority": "medium"
                },
                {
                    "icon": "❄️",
                    "title": "Ρυθμίστε το Κλιματιστικό",
                    "description": "Ρυθμίστε το κλιματιστικό στους 26°C αντί για 22°C.",
                    "potential_savings_kwh": 0.8,
                    "priority": "medium"
                }
            ])
        else:
            # Non-peak hours
            tips.extend([
                {
                    "icon": "🌙",
                    "title": "Ιδανική Ώρα για Πλύσιμο",
                    "description": "Τώρα είναι εκτός αιχμής - ιδανικό για πλυντήριο και στεγνωτήριο.",
                    "priority": "low"
                },
                {
                    "icon": "💡",
                    "title": "Προετοιμαστείτε για Αύριο",
                    "description": "Σκεφτείτε πώς θα εξοικονομήσετε ενέργεια στην επόμενη ώρα αιχμής.",
                    "priority": "low"
                }
            ])

        # Always relevant tips
        tips.append({
            "icon": "⭐",
            "title": "Μην Χάσετε Double Points Days",
            "description": "Μην χάνετε τα Double Points Days (ημέρες καύσωνα ή κρύου), όπου η αξία διπλασιάζεται!",
            "priority": "high"
        })

        return tips

    def simulate_scenario(
        self,
        annual_fee: float = 185.0,
        sessions_per_week: int = 5,
        avg_savings_per_session_kwh: float = 2.0,
        weeks: int = 52
    ) -> Dict:
        """
        Simulate a full year scenario

        Shows users what they could achieve
        """
        total_sessions = sessions_per_week * weeks
        total_savings_kwh = total_sessions * avg_savings_per_session_kwh
        total_earnings_eur = total_savings_kwh * self.KWH_TO_EUR_RATE

        weeks_to_goal = 0
        accumulated_eur = 0

        weekly_earnings = (sessions_per_week * avg_savings_per_session_kwh *
                          self.KWH_TO_EUR_RATE)

        while accumulated_eur < annual_fee and weeks_to_goal < 52:
            accumulated_eur += weekly_earnings
            weeks_to_goal += 1

        surplus = max(0, total_earnings_eur - annual_fee)

        return {
            "annual_fee_goal": annual_fee,
            "total_sessions": total_sessions,
            "total_kwh_saved": round(total_savings_kwh, 2),
            "total_earnings": round(total_earnings_eur, 2),
            "weeks_to_reach_goal": weeks_to_goal,
            "surplus_available": round(surplus, 2),
            "fee_coverage_percentage": min(100, round((total_earnings_eur / annual_fee) * 100, 1)),
            "avg_weekly_earnings": round(weekly_earnings, 2),
            "sessions_needed_to_reach_goal": round(annual_fee / (avg_savings_per_session_kwh * self.KWH_TO_EUR_RATE))
        }


# Singleton instance
waste_fee_engine = WasteFeeOffsetEngine()


def demo_waste_fee_offset():
    """Demo the Waste Fee Offset system"""
    print("=" * 70)
    print("ΟΔΗΓΟΣ ΧΡΗΣΗΣ: ΕΡΓΑΛΕΙΟ 'WASTE FEE OFFSET'")
    print("Πώς να μηδενίσετε τα Τέλη Σκυβάλων σας, κλείνοντας απλά τον διακόπτη.")
    print("=" * 70)
    print()

    # Step 1: Create account
    print("ΒΗΜΑ 1: Σύνδεση Υποστατικού")
    print("-" * 70)
    account = waste_fee_engine.create_waste_fee_account(
        user_id="user_123",
        property_number="12345678",
        municipality=Municipality.NICOSIA,
        annual_fee=185.00,
        owner_name="Γιώργος Παπαδόπουλος",
        address="Λεωφ. Μακαρίου 123, Λευκωσία"
    )
    print(f"✓ Σύνδεση επιτυχής!")
    print(f"  Δήμος: {account.municipality.value.title()}")
    print(f"  Αριθμός Υποστατικού: {account.property_number}")
    print(f"  Ετήσιο Τέλος: €{account.annual_fee:.2f}")
    print()

    # Step 2: Simulate sessions
    print("ΒΗΜΑ 2: Saving Sessions")
    print("-" * 70)

    # Simulate 10 sessions over 2 weeks
    historical_consumption = [2.5, 2.3, 2.6, 2.4, 2.5, 2.7, 2.4, 2.5, 2.6, 2.3]

    sessions_data = [
        (1.8, False),  # Good savings
        (2.0, False),
        (1.5, False),  # Great savings
        (2.2, False),
        (1.7, True),   # Double points day!
        (1.9, False),
        (1.6, False),
        (2.1, False),
        (1.4, True),   # Double points day!
        (1.8, False),
    ]

    for i, (actual_kwh, is_double) in enumerate(sessions_data, 1):
        session_date = datetime.now() - timedelta(days=20-i*2)
        session = waste_fee_engine.complete_saving_session(
            user_id="user_123",
            start_time=session_date.replace(hour=18, minute=0),
            actual_kwh=actual_kwh,
            historical_consumption=historical_consumption,
            is_double_points=is_double
        )

        multiplier = " (DOUBLE POINTS! ⭐)" if is_double else ""
        print(f"Session {i:2d}: Baseline {session.baseline_kwh} kWh → Actual {session.actual_kwh} kWh")
        print(f"            Έσωσες {session.savings_kwh} kWh = €{session.earnings_eur:.2f}{multiplier}")

    print()

    # Step 3: Check wallet
    print("ΒΗΜΑ 3: Το Waste Wallet σας")
    print("-" * 70)
    wallet = waste_fee_engine.get_wallet_status("user_123")
    progress = waste_fee_engine.get_progress_percentage("user_123")

    print(f"Υπόλοιπο Πορτοφολιού: €{wallet.balance_eur:.2f}")
    print(f"Στόχος Έτους: €{wallet.annual_goal_eur:.2f}")
    print(f"Πρόοδος: {progress}% Καλυμμένο")
    print(f"Συνολικά Sessions: {wallet.total_sessions_completed}")
    print(f"Συνολική Εξοικονόμηση: {wallet.total_kwh_saved} kWh")
    print()

    # Step 4: Process payment
    print("ΒΗΜΑ 4: Μηνιαία Πληρωμή στον Δήμο")
    print("-" * 70)
    payment = waste_fee_engine.process_monthly_payment("user_123")
    print(payment['receipt'])
    print(f"Πληρώθηκε στον Δήμο {payment['municipality'].title()}")
    print(f"Υπόλοιπο Ετήσιου Τέλους: €{payment['remaining_annual_fee']:.2f}")
    print()

    # Step 5: Tips
    print("ΒΗΜΑ 5: Tips για Μέγιστο Κέρδος 💡")
    print("-" * 70)
    tips = waste_fee_engine.get_saving_tips(time_of_day=18)
    for tip in tips[:3]:
        print(f"{tip['icon']} {tip['title']}")
        print(f"   {tip['description']}")
        if 'potential_savings_kwh' in tip:
            print(f"   Δυνητική εξοικονόμηση: ~{tip['potential_savings_kwh']} kWh")
        print()

    # Step 6: Yearly simulation
    print("ΒΗΜΑ 6: Προσομοίωση Ετήσιου Σεναρίου")
    print("-" * 70)
    scenario = waste_fee_engine.simulate_scenario(
        annual_fee=185.0,
        sessions_per_week=5,
        avg_savings_per_session_kwh=2.0
    )
    print(f"Αν κάνετε {scenario['sessions_needed_to_reach_goal']:.0f} sessions με μέσο όρο 2 kWh εξοικονόμηση:")
    print(f"  → Θα φτάσετε τον στόχο σε {scenario['weeks_to_reach_goal']} εβδομάδες")
    print(f"  → Συνολική ετήσια εξοικονόμηση: {scenario['total_kwh_saved']} kWh")
    print(f"  → Συνολικά κέρδη: €{scenario['total_earnings']:.2f}")
    print(f"  → Πλεόνασμα διαθέσιμο για δωρεά: €{scenario['surplus_available']:.2f}")
    print()


if __name__ == "__main__":
    demo_waste_fee_offset()
