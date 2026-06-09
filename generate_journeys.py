import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ==========================================================
# CONFIGURATION
# ==========================================================

RANDOM_SEED = 101

np.random.seed(RANDOM_SEED)

CHANNELS = [
    "meta_awareness",
    "meta_conversion",
    "google_search",
    "google_display",
    "email_nurture",
    "whatsapp_trigger",
    "organic_search"
]

CUSTOMER_SEGMENTS = [
    "cold",
    "warm",
    "hot"
]

SEGMENT_WEIGHTS = [
    0.50,
    0.35,
    0.15
]

# ==========================================================
# TRANSITION RULES
# ==========================================================

TRANSITIONS = {

    "START": {
        "meta_awareness": 0.30,
        "google_search": 0.25,
        "google_display": 0.20,
        "organic_search": 0.25
    },

    "meta_awareness": {
        "meta_conversion": 0.40,
        "email_nurture": 0.20,
        "whatsapp_trigger": 0.15,
        "DROP_OFF": 0.25
    },

    "google_display": {
        "meta_conversion": 0.25,
        "google_search": 0.25,
        "email_nurture": 0.20,
        "DROP_OFF": 0.30
    },

    "google_search": {
        "meta_conversion": 0.35,
        "email_nurture": 0.20,
        "whatsapp_trigger": 0.20,
        "CONVERSION": 0.10,
        "DROP_OFF": 0.15
    },

    "email_nurture": {
        "meta_conversion": 0.25,
        "whatsapp_trigger": 0.35,
        "CONVERSION": 0.20,
        "DROP_OFF": 0.20
    },

    "meta_conversion": {
        "whatsapp_trigger": 0.35,
        "email_nurture": 0.15,
        "CONVERSION": 0.35,
        "DROP_OFF": 0.15
    },

    "whatsapp_trigger": {
        "CONVERSION": 0.60,
        "DROP_OFF": 0.20,
        "meta_conversion": 0.20
    },

    "organic_search": {
        "meta_awareness": 0.35,
        "google_search": 0.25,
        "email_nurture": 0.15,
        "DROP_OFF": 0.25
    }
}

# ==========================================================
# SEGMENT MODIFIERS
# ==========================================================

SEGMENT_CONVERSION_MULTIPLIER = {
    "cold": 0.8,
    "warm": 1.0,
    "hot": 1.4
}

SEGMENT_REVENUE_RANGE = {
    "cold": (50, 150),
    "warm": (100, 500),
    "hot": (500, 2500)
}

# ==========================================================
# HELPERS
# ==========================================================

def normalize_probabilities(options):

    total = sum(options.values())

    return {
        k: v / total
        for k, v in options.items()
    }


def choose_next_state(current_state, segment):

    options = TRANSITIONS[current_state].copy()

    if "CONVERSION" in options:

        options["CONVERSION"] *= (
            SEGMENT_CONVERSION_MULTIPLIER[segment]
        )

    options = normalize_probabilities(options)

    states = list(options.keys())
    probs = list(options.values())

    return np.random.choice(states, p=probs)


# ==========================================================
# MAIN GENERATOR
# ==========================================================

def generate_sequential_journeys(
        num_users=10000):

    print(
        f"\n[Markov Nexus] Generating "
        f"{num_users:,} journeys..."
    )

    records = []

    start_date = datetime(2025, 1, 1)

    for user_id in range(
            1,
            num_users + 1):

        segment = np.random.choice(
            CUSTOMER_SEGMENTS,
            p=SEGMENT_WEIGHTS
        )

        current_state = "START"

        path = []

        timestamps = []

        current_time = start_date + timedelta(
            days=np.random.randint(0, 365)
        )

        step_count = 0

        while current_state not in (
                "CONVERSION",
                "DROP_OFF"):

            next_state = choose_next_state(
                current_state,
                segment
            )

            current_time += timedelta(
                hours=np.random.randint(4, 72)
            )

            path.append(next_state)

            timestamps.append(
                current_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            current_state = next_state

            step_count += 1

            if step_count > 15:

                path.append("DROP_OFF")

                current_state = "DROP_OFF"

                break

        converted = (
            1
            if "CONVERSION" in path
            else 0
        )

        revenue = 0

        if converted:

            revenue = round(
                np.random.uniform(
                    *SEGMENT_REVENUE_RANGE[
                        segment
                    ]
                ),
                2
            )

        records.append({

            "user_id":
                f"USR_{user_id:06d}",

            "customer_segment":
                segment,

            "journey_path":
                " > ".join(path),

            "touchpoints":
                len(path),

            "converted":
                converted,

            "revenue":
                revenue,

            "final_state":
                current_state,

            "first_touch":
                path[0]
                if path else None,

            "last_touch":
                path[-2]
                if converted and len(path) > 1
                else (
                    path[-1]
                    if path
                    else None
                ),

            "journey_end":
                timestamps[-1]
                if timestamps
                else None
        })

    df = pd.DataFrame(records)

    os.makedirs(
        "core_logic",
        exist_ok=True
    )

    output_file = os.path.join(
        "core_logic",
        "user_journey_sequences.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\nDataset Generated Successfully")
    print(f"Rows: {len(df):,}")
    print(
        f"Conversions: "
        f"{df['converted'].sum():,}"
    )

    print(
        f"Revenue: "
        f"${df['revenue'].sum():,.2f}"
    )

    print(
        f"\nSaved to:\n{output_file}"
    )

    return df


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    generate_sequential_journeys(
        num_users=10000
    )
