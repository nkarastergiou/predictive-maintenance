from dataclasses import dataclass


@dataclass
class MaintenanceAssessment:
    health_score: int
    maintenance_priority: str
    risk_driver: str
    recommended_action: str


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def calculate_sensor_severity(
    temperature: float,
    vibration: float,
    current: float
):
    severities = {
        "TEMPERATURE": 0,
        "VIBRATION": 0,
        "CURRENT": 0,
    }

    # Temperature severity
    if temperature >= 48:
        severities["TEMPERATURE"] = 30
    elif temperature >= 45:
        severities["TEMPERATURE"] = 18
    elif temperature >= 43:
        severities["TEMPERATURE"] = 8

    # Vibration severity
    if vibration >= 0.28:
        severities["VIBRATION"] = 30
    elif vibration >= 0.22:
        severities["VIBRATION"] = 18
    elif vibration >= 0.18:
        severities["VIBRATION"] = 8

    # Current severity
    if current >= 5.7:
        severities["CURRENT"] = 30
    elif current >= 5.2:
        severities["CURRENT"] = 18
    elif current >= 4.9:
        severities["CURRENT"] = 8

    return severities


def determine_risk_driver(severities: dict) -> str:
    max_severity = max(severities.values())

    if max_severity == 0:
        return "NONE"

    highest = [
        sensor
        for sensor, severity in severities.items()
        if severity == max_severity
    ]

    if len(highest) > 1:
        return "MULTIPLE FACTORS"

    return highest[0]


def calculate_health_score(
    temperature: float,
    vibration: float,
    current: float,
    current_status: str,
    predictive_state: str,
    failure_probability: float
) -> tuple[int, dict]:

    score = 100

    severities = calculate_sensor_severity(
        temperature,
        vibration,
        current
    )

    # Apply the highest sensor penalty rather than summing all three
    # to avoid over-penalizing correlated sensor degradation.
    score -= max(severities.values())

    # Failure probability penalty: up to 30 points
    probability = clamp(failure_probability * 100)
    score -= probability * 0.30

    # Current operational status penalty
    status_penalties = {
        "NORMAL": 0,
        "WARNING": 12,
        "FAILURE RISK": 28,
    }

    score -= status_penalties.get(current_status, 0)

    # Predictive state penalty
    predictive_penalties = {
        "NO IMMINENT FAILURE": 0,
        "PREDICTED FAILURE": 18,
        "ALREADY FAILED": 30,
    }

    score -= predictive_penalties.get(predictive_state, 0)

    return round(clamp(score)), severities


def determine_priority(
    health_score: int,
    current_status: str,
    predictive_state: str
) -> str:

    # Hard safety overrides
    if current_status == "FAILURE RISK":
        return "CRITICAL"

    if predictive_state == "ALREADY FAILED":
        return "CRITICAL"

    if predictive_state == "PREDICTED FAILURE":
        if health_score <= 20:
            return "CRITICAL"
        return "HIGH"

    if health_score <= 25:
        return "CRITICAL"

    if health_score <= 50:
        return "HIGH"

    if health_score <= 75:
        return "MEDIUM"

    return "LOW"


def recommend_action(
    priority: str,
    risk_driver: str
) -> str:

    if priority == "LOW":
        return "Continue normal operation"

    if priority == "MEDIUM":
        return "Monitor closely and schedule inspection"

    if priority == "CRITICAL":
        return "Immediate maintenance intervention required"

    # HIGH priority
    actions = {
        "TEMPERATURE":
            "Inspect cooling and thermal conditions",

        "VIBRATION":
            "Inspect vibration-related components and bearings",

        "CURRENT":
            "Inspect electrical load and motor condition",

        "MULTIPLE FACTORS":
            "Perform comprehensive machine inspection",

        "NONE":
            "Schedule maintenance inspection",
    }

    return actions.get(
        risk_driver,
        "Schedule maintenance inspection"
    )


def assess_machine(
    temperature: float,
    vibration: float,
    current: float,
    current_status: str,
    predictive_state: str,
    failure_probability: float
) -> MaintenanceAssessment:

    health_score, severities = calculate_health_score(
        temperature,
        vibration,
        current,
        current_status,
        predictive_state,
        failure_probability
    )

    risk_driver = determine_risk_driver(severities)

    priority = determine_priority(
        health_score,
        current_status,
        predictive_state
    )

    action = recommend_action(
        priority,
        risk_driver
    )

    return MaintenanceAssessment(
        health_score=health_score,
        maintenance_priority=priority,
        risk_driver=risk_driver,
        recommended_action=action
    )


if __name__ == "__main__":
    examples = [
        {
            "name": "Healthy machine",
            "temperature": 42.0,
            "vibration": 0.15,
            "current": 4.5,
            "current_status": "NORMAL",
            "predictive_state": "NO IMMINENT FAILURE",
            "failure_probability": 0.10,
        },
        {
            "name": "Early predicted failure",
            "temperature": 44.5,
            "vibration": 0.23,
            "current": 5.1,
            "current_status": "WARNING",
            "predictive_state": "PREDICTED FAILURE",
            "failure_probability": 0.75,
        },
        {
            "name": "Failed machine",
            "temperature": 49.0,
            "vibration": 0.31,
            "current": 5.9,
            "current_status": "FAILURE RISK",
            "predictive_state": "ALREADY FAILED",
            "failure_probability": 0.90,
        },
    ]

    for example in examples:
        assessment = assess_machine(
            temperature=example["temperature"],
            vibration=example["vibration"],
            current=example["current"],
            current_status=example["current_status"],
            predictive_state=example["predictive_state"],
            failure_probability=example["failure_probability"],
        )

        print(f"\n{example['name']}")
        print(assessment)