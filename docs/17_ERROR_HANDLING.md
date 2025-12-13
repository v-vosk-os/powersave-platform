# PowerSave Cyprus - Error Handling & Recovery

## Επισκόπηση

Το σύστημα PowerSave υλοποιεί ένα ολοκληρωμένο πλαίσιο διαχείρισης σφαλμάτων για να εξασφαλίσει την αξιοπιστία και την εμπιστοσύνη των χρηστών.

---

## Saving Session Error States

### Session Status Enum

```python
class SessionStatus(Enum):
    SCHEDULED = "scheduled"      # Προγραμματισμένη
    IN_PROGRESS = "in_progress"  # Σε εξέλιξη
    COMPLETED = "completed"      # Ολοκληρωμένη
    FAILED = "failed"            # Αποτυχημένη
    CANCELLED = "cancelled"      # Ακυρωμένη
```

### Failure Scenarios

| Σενάριο | Αιτία | Χειρισμός |
|---------|-------|-----------|
| **METER_DATA_UNAVAILABLE** | ΑΗΚ API timeout/error | Retry 3x, then FAILED |
| **BASELINE_CALCULATION_ERROR** | Ανεπαρκή ιστορικά δεδομένα | Fallback to default baseline |
| **NETWORK_ERROR** | Connectivity issues | Queue for retry |
| **VALIDATION_ERROR** | Invalid session parameters | Reject with user message |

---

## Retry Logic

### Celery Task Retry Configuration

```python
@celery.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    retry_backoff=True,
    retry_backoff_max=3600    # Max 1 hour
)
def process_session_end(self, session_id):
    try:
        # Fetch actual consumption
        # Calculate savings
        # Update database
    except MeterDataUnavailableError as e:
        raise self.retry(exc=e)
    except Exception as e:
        # Log error
        # Mark session as FAILED
        # Notify admin
```

### Retry Schedule

| Attempt | Delay | Total Wait |
|---------|-------|------------|
| 1st | 5 min | 5 min |
| 2nd | 10 min | 15 min |
| 3rd | 20 min | 35 min |
| **Final** | FAILED | Admin notification |

---

## API Error Responses

### HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| **400** | Bad Request | Invalid parameters |
| **401** | Unauthorized | Invalid/expired JWT |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Duplicate session |
| **422** | Unprocessable | Validation failed |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Error | Unexpected server error |
| **502** | Bad Gateway | External API failure |
| **503** | Unavailable | Maintenance mode |

### Error Response Format

```json
{
  "error": {
    "code": "SESSION_OVERLAP",
    "message": "Υπάρχει ήδη προγραμματισμένη συνεδρία για αυτό το διάστημα",
    "message_en": "A session is already scheduled for this time slot",
    "details": {
      "existing_session_id": "uuid-here",
      "conflicting_start": "2024-01-15T17:00:00Z",
      "conflicting_end": "2024-01-15T20:00:00Z"
    },
    "timestamp": "2024-01-15T14:30:00Z",
    "request_id": "req-12345"
  }
}
```

### Greek Error Messages

| Code | Μήνυμα |
|------|--------|
| `INVALID_CREDENTIALS` | Λάθος στοιχεία σύνδεσης |
| `SESSION_OVERLAP` | Υπάρχει ήδη προγραμματισμένη συνεδρία |
| `INSUFFICIENT_POINTS` | Δεν έχετε αρκετούς πόντους |
| `METER_UNAVAILABLE` | Τα δεδομένα μετρητή δεν είναι διαθέσιμα |
| `SESSION_TOO_SHORT` | Η συνεδρία πρέπει να είναι τουλάχιστον 1 ώρα |
| `SESSION_TOO_LONG` | Η συνεδρία δεν μπορεί να υπερβαίνει τις 4 ώρες |
| `RATE_LIMIT_EXCEEDED` | Πολλές αιτήσεις. Δοκιμάστε αργότερα |

---

## Fallback Mechanisms

### Baseline Calculation Fallbacks

```
Priority 1: 4-week rolling average (same day/hour)
    ↓ (if insufficient data)
Priority 2: 2-week rolling average
    ↓ (if still insufficient)
Priority 3: Category average (similar households)
    ↓ (if no category match)
Priority 4: National average for time slot
```

### External API Fallbacks

| Primary | Fallback | Timeout |
|---------|----------|---------|
| ΑΗΚ Real-time API | ΑΗΚ Batch API | 30s |
| Firebase Push | SMS Gateway | 10s |
| Municipal Gateway | Manual reconciliation | 60s |

---

## Admin Override Capabilities

### Manual Session Adjustments

| Action | Permission Level | Use Case |
|--------|-----------------|----------|
| **Retry Session** | Operator | Transient failures |
| **Adjust Baseline** | Supervisor | Anomaly correction |
| **Force Complete** | Admin | Manual verification |
| **Override Savings** | Admin | Disputed calculations |
| **Cancel + Refund** | Admin | System errors |

### Admin API Endpoints

```
POST /admin/sessions/{id}/retry
POST /admin/sessions/{id}/force-complete
PATCH /admin/sessions/{id}/override
DELETE /admin/sessions/{id}/cancel
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Session Failure Rate | >5% | Warning |
| Session Failure Rate | >10% | Critical |
| API Error Rate (5xx) | >1% | Warning |
| API Latency (p95) | >2s | Warning |
| Celery Queue Length | >1000 | Warning |
| Smart Meter API Errors | >3 consecutive | Critical |

### Alert Channels

| Severity | Channel |
|----------|---------|
| Info | Slack #powersave-ops |
| Warning | Slack + Email |
| Critical | Slack + Email + SMS + PagerDuty |

---

## User Communication

### Failed Session Notification

```
🔴 Η συνεδρία εξοικονόμησης δεν ολοκληρώθηκε

Λυπούμαστε, αλλά η συνεδρία σας στις [DATE] 
δεν μπόρεσε να υπολογιστεί λόγω τεχνικού προβλήματος.

Τι σημαίνει αυτό:
• Δεν χρεώθηκαν πόντοι
• Δεν επηρεάστηκε το Waste Wallet σας
• Μπορείτε να προγραμματίσετε νέα συνεδρία

[Προγραμματισμός Νέας Συνεδρίας]
```

### Maintenance Notification

```
🔧 Προγραμματισμένη Συντήρηση

Το PowerSave θα είναι εκτός λειτουργίας 
στις [DATE] από [TIME] έως [TIME].

Οι προγραμματισμένες συνεδρίες θα εκτελεστούν 
κανονικά μετά την ολοκλήρωση της συντήρησης.
```

---

## Data Recovery

### Backup Strategy

| Data Type | Frequency | Retention | Recovery Time |
|-----------|-----------|-----------|---------------|
| PostgreSQL Full | Daily | 30 days | 4 hours |
| PostgreSQL WAL | Continuous | 7 days | Minutes (PITR) |
| Redis RDB | Hourly | 24 hours | 30 minutes |
| User Files | Daily | 90 days | 2 hours |

### Recovery Procedures

1. **Point-in-Time Recovery**: WAL replay για database
2. **Session Reconstruction**: Re-fetch meter data + recalculate
3. **Wallet Reconciliation**: Cross-reference with On-Bill Clearing
4. **Gamification Restore**: Green Points + Badges from transaction log

---

## Testing Error Scenarios

### Chaos Engineering

| Test | Frequency | Method |
|------|-----------|--------|
| API Latency Injection | Weekly | Toxiproxy |
| Database Failover | Monthly | Kill primary |
| Celery Worker Death | Weekly | Random kill |
| External API Mock Failure | Daily | Feature flags |

### Error Scenario Testing

```bash
# Simulate meter data unavailability
curl -X POST /test/simulate-meter-failure

# Simulate high latency
curl -X POST /test/inject-latency?ms=5000

# Trigger circuit breaker
curl -X POST /test/trip-circuit-breaker?service=ahk
```

---

## Πηγές

- [Celery Error Handling](https://docs.celeryq.dev/en/stable/userguide/tasks.html#retrying)
- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [PostgreSQL PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
