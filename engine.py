import pandas as pd
import numpy as np
from collections import defaultdict
import os


class MarkovAttributionKernel:
    def __init__(self, data_path: str):
        """Initializes the Markov Kernel and loads the sequential journey data."""
        self.data_path = data_path
        self.df = self._load_data()
        self.channels = []
        self.transition_probabilities = {}
        self.removal_effects = {}

    def _load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset missing at {self.data_path}. Run generate_journeys.py first.")
        return pd.read_csv(self.data_path)

    def build_transition_matrix(self):
        """
        Calculates the state transition matrix.
        Determines the probability P(j|i) of moving to state j given current state i.
        """
        print("[Engine] Building Transition Probability Matrix...")

        transitions = defaultdict(lambda: defaultdict(int))
        state_totals = defaultdict(int)
        unique_channels = set()

        # Parse the journey paths
        for path in self.df['journey_path']:
            nodes = ["START"] + path.split(" > ")

            for i in range(len(nodes) - 1):
                current_state = nodes[i]
                next_state = nodes[i + 1]

                transitions[current_state][next_state] += 1
                state_totals[current_state] += 1

                if current_state not in ["START", "CONVERSION", "DROP_OFF"]:
                    unique_channels.add(current_state)

        self.channels = list(unique_channels)

        # Convert raw transition counts to probabilities
        for state, destinations in transitions.items():
            self.transition_probabilities[state] = {}
            for dest, count in destinations.items():
                self.transition_probabilities[state][dest] = count / state_totals[state]

        print("[Engine] Transition Matrix Compiled Successfully.\n")

    def simulate_conversion_probability(self, removal_state: str = None) -> float:
        """
        Simulates the total probability of conversion using the transition matrix.
        If removal_state is provided, it reroutes that channel's traffic to DROP_OFF.
        """
        # Start with 100% of traffic at START
        current_distribution = {"START": 1.0}
        conversion_prob = 0.0

        # Simulate 15 steps (to cover max journey length)
        for _ in range(15):
            next_distribution = defaultdict(float)

            for state, weight in current_distribution.items():
                if state == "CONVERSION":
                    conversion_prob += weight
                    continue
                if state == "DROP_OFF":
                    continue

                # If we are testing the removal effect, this channel drops to 0
                if removal_state and state == removal_state:
                    next_distribution["DROP_OFF"] += weight
                    continue

                # Distribute traffic based on Markov probabilities
                if state in self.transition_probabilities:
                    for dest, prob in self.transition_probabilities[state].items():
                        next_distribution[dest] += weight * prob

            current_distribution = next_distribution

        return conversion_prob

    def calculate_removal_effects(self):
        """
        Calculates the statistical impact of removing each marketing channel.
        """
        print("[Engine] Calculating Channel Removal Effects...")

        base_conversion = self.simulate_conversion_probability()
        print(f"Base System Conversion Rate: {base_conversion:.2%}")

        for channel in self.channels:
            removal_conversion = self.simulate_conversion_probability(removal_state=channel)
            loss_effect = (base_conversion - removal_conversion) / base_conversion
            self.removal_effects[channel] = loss_effect

            print(f"Removal Effect [{channel}]: {loss_effect:.2%} loss in conversions.")

    def execute_pipeline(self):
        self.build_transition_matrix()
        self.calculate_removal_effects()
        return self.removal_effects


if __name__ == "__main__":
    # Point the engine to the generated core logic dataset
    target_data = os.path.join("core_logic", "user_journey_sequences.csv")

    kernel = MarkovAttributionKernel(target_data)
    results = kernel.execute_pipeline()
