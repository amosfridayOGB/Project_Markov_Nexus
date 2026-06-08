import pandas as pd
import numpy as np
import os


def generate_sequential_journeys(num_users: int = 5000):
    """
    Simulates multi-touch customer journeys across marketing channels
    to feed a Markov Chain Transition Matrix model for Project Markov Nexus.
    """
    print(f"[Markov_Nexus Simulation] Generating {num_users:,} unique customer paths...")

    # Isolated seed for academic replicability
    np.random.seed(101)

    channels = ["meta_awareness", "meta_conversion", "whatsapp_trigger"]

    # Define baseline transition probabilities from any current state
    # Mapped as: [To Meta_Awareness, To Meta_Conversion, To WhatsApp, To Conversion, To Drop_Off]
    transition_rules = {
        "START": [0.6, 0.3, 0.1, 0.0, 0.0],
        "meta_awareness": [0.1, 0.5, 0.2, 0.0, 0.2],
        "meta_conversion": [0.0, 0.1, 0.3, 0.4, 0.2],
        "whatsapp_trigger": [0.1, 0.0, 0.1, 0.6, 0.2]
    }

    states_modifier = channels + ["CONVERSION", "DROP_OFF"]
    journey_records = []

    for user_id in range(1, num_users + 1):
        current_state = "START"
        path = []

        while current_state not in ["CONVERSION", "DROP_OFF"]:
            probs = transition_rules[current_state]
            next_state = np.random.choice(states_modifier, p=probs)

            # Record the state transition
            if next_state not in ["CONVERSION", "DROP_OFF"]:
                path.append(next_state)
            else:
                path.append(next_state)

            current_state = next_state

            # Circuit breaker to prevent infinite loops in simulation
            if len(path) > 10:
                path.append("DROP_OFF")
                break

        # Join the path nodes with a standard token separator
        path_string = " > ".join(path)
        journey_records.append({
            "user_id": f"USR_{user_id:06d}",
            "journey_path": path_string,
            "converted": 1 if "CONVERSION" in path else 0
        })

    df = pd.DataFrame(journey_records)

    # Save systematically into the core logic module
    os.makedirs("core_logic", exist_ok=True)
    output_path = os.path.join("core_logic", "user_journey_sequences.csv")
    df.to_csv(output_path, index=False)

    print("\n[Success] Sequential journey dataset saved successfully.")
    print(df.head(10))


if __name__ == "__main__":
    generate_sequential_journeys(num_users=5000)
