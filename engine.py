import os
from collections import defaultdict

import numpy as np
import pandas as pd


class MarkovAttributionKernel:

    def __init__(self, data_path: str):

        self.data_path = data_path

        self.df = self._load_data()

        self.channels = []

        self.transition_probabilities = {}

        self.removal_effects = {}

        self.base_conversion_rate = None

    # ======================================================
    # DATA LOADING
    # ======================================================

    def _load_data(self):

        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"Dataset not found: {self.data_path}"
            )

        df = pd.read_csv(self.data_path)

        required_columns = ["journey_path"]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        return df

    # ======================================================
    # TRANSITION MATRIX
    # ======================================================

    def build_transition_matrix(self):

        transitions = defaultdict(
            lambda: defaultdict(int)
        )

        state_totals = defaultdict(int)

        unique_channels = set()

        for path in self.df["journey_path"]:

            nodes = ["START"] + path.split(" > ")

            for i in range(len(nodes) - 1):

                current_state = nodes[i]
                next_state = nodes[i + 1]

                transitions[current_state][next_state] += 1
                state_totals[current_state] += 1

                if current_state not in (
                    "START",
                    "CONVERSION",
                    "DROP_OFF"
                ):
                    unique_channels.add(current_state)

        self.channels = sorted(
            list(unique_channels)
        )

        self.transition_probabilities = {}

        for state, destinations in transitions.items():

            self.transition_probabilities[state] = {}

            total = state_totals[state]

            for dest, count in destinations.items():

                self.transition_probabilities[state][dest] = (
                    count / total
                )

        return self.transition_probabilities

    # ======================================================
    # DEPTH
    # ======================================================

    def _get_max_depth(self):

        max_depth = max(
            len(path.split(" > "))
            for path in self.df["journey_path"]
        )

        return max_depth + 5

    # ======================================================
    # CONVERSION SIMULATION
    # ======================================================

    def simulate_conversion_probability(
            self,
            removal_state=None):

        if not self.transition_probabilities:
            self.build_transition_matrix()

        current_distribution = {
            "START": 1.0
        }

        conversion_probability = 0.0

        max_depth = self._get_max_depth()

        for _ in range(max_depth):

            next_distribution = defaultdict(float)

            for state, weight in current_distribution.items():

                if state == "CONVERSION":
                    conversion_probability += weight
                    continue

                if state == "DROP_OFF":
                    continue

                if (
                    removal_state is not None and
                    state == removal_state
                ):
                    next_distribution["DROP_OFF"] += weight
                    continue

                if state in self.transition_probabilities:

                    for dest, prob in self.transition_probabilities[
                        state
                    ].items():

                        next_distribution[dest] += (
                            weight * prob
                        )

            current_distribution = next_distribution

        return conversion_probability

    # ======================================================
    # MULTI CHANNEL REMOVAL
    # ======================================================

    def simulate_multi_channel_removal(
            self,
            channels_to_remove):

        if not self.transition_probabilities:
            self.build_transition_matrix()

        channels_to_remove = set(
            channels_to_remove
        )

        current_distribution = {
            "START": 1.0
        }

        conversion_probability = 0.0

        max_depth = self._get_max_depth()

        for _ in range(max_depth):

            next_distribution = defaultdict(float)

            for state, weight in current_distribution.items():

                if state == "CONVERSION":
                    conversion_probability += weight
                    continue

                if state == "DROP_OFF":
                    continue

                if state in channels_to_remove:

                    next_distribution["DROP_OFF"] += weight
                    continue

                if state in self.transition_probabilities:

                    for dest, prob in self.transition_probabilities[
                        state
                    ].items():

                        next_distribution[dest] += (
                            weight * prob
                        )

            current_distribution = next_distribution

        return conversion_probability

    # ======================================================
    # REMOVAL EFFECTS
    # ======================================================

    def calculate_removal_effects(self):

        if not self.transition_probabilities:
            self.build_transition_matrix()

        self.removal_effects = {}

        base_conversion = (
            self.simulate_conversion_probability()
        )

        self.base_conversion_rate = (
            base_conversion
        )

        for channel in self.channels:

            removal_conversion = (
                self.simulate_conversion_probability(
                    removal_state=channel
                )
            )

            if base_conversion == 0:

                loss_effect = 0

            else:

                loss_effect = (
                    (
                        base_conversion
                        - removal_conversion
                    )
                    / base_conversion
                )

            self.removal_effects[channel] = (
                loss_effect
            )

        return self.removal_effects

    # ======================================================
    # ATTRIBUTION WEIGHTS
    # ======================================================

    def get_attribution_weights(self):

        if not self.removal_effects:
            self.calculate_removal_effects()

        total_effect = sum(
            self.removal_effects.values()
        )

        if total_effect == 0:
            return {}

        return {
            channel: effect / total_effect
            for channel, effect
            in self.removal_effects.items()
        }

    # ======================================================
    # REVENUE
    # ======================================================

    def get_total_revenue(self):

        if "revenue" not in self.df.columns:
            return 0.0

        return float(
            self.df["revenue"].sum()
        )

    def get_average_order_value(self):

        if "revenue" not in self.df.columns:
            return 0.0

        converted = self.df[
            self.df["revenue"] > 0
        ]

        if len(converted) == 0:
            return 0.0

        return float(
            converted["revenue"].mean()
        )

    def get_revenue_attribution(self):

        if not self.removal_effects:
            self.calculate_removal_effects()

        total_revenue = (
            self.get_total_revenue()
        )

        total_effect = sum(
            self.removal_effects.values()
        )

        if total_effect == 0:
            return {}

        revenue_attribution = {}

        for channel, effect in (
                self.removal_effects.items()):

            share = effect / total_effect

            revenue_attribution[channel] = (
                share * total_revenue
            )

        return revenue_attribution

    def get_revenue_loss_estimates(self):

        if not self.removal_effects:
            self.calculate_removal_effects()

        total_revenue = (
            self.get_total_revenue()
        )

        revenue_loss = {}

        for channel, effect in (
                self.removal_effects.items()):

            revenue_loss[channel] = (
                total_revenue * effect
            )

        return revenue_loss

    # ======================================================
    # CUSTOMER SEGMENTS
    # ======================================================

    def get_segment_summary(self):

        if "customer_segment" not in self.df.columns:
            return pd.DataFrame()

        grouped = (
            self.df.groupby(
                "customer_segment"
            )
            .agg(
                users=("user_id", "count"),
                conversions=("converted", "sum"),
                revenue=("revenue", "sum"),
                avg_touchpoints=("touchpoints", "mean")
            )
            .reset_index()
        )

        grouped["conversion_rate"] = (
            grouped["conversions"]
            / grouped["users"]
        )

        return grouped

    # ======================================================
    # MATRIX EXPORT
    # ======================================================

    def get_transition_matrix_df(self):

        if not self.transition_probabilities:
            self.build_transition_matrix()

        return pd.DataFrame(
            self.transition_probabilities
        ).fillna(0)

    # ======================================================
    # MONTE CARLO
    # ======================================================

    def monte_carlo_forecast(
            self,
            simulations=5000):

        if not self.channels:
            self.build_transition_matrix()

        results = []

        for _ in range(simulations):

            sample_size = max(
                1,
                int(
                    len(self.channels) * 0.30
                )
            )

            removed_channels = np.random.choice(
                self.channels,
                size=sample_size,
                replace=False
            )

            conversion = (
                self.simulate_multi_channel_removal(
                    removed_channels
                )
            )

            results.append(conversion)

        return results

    # ======================================================
    # SUMMARY
    # ======================================================

    def get_summary(self):

        if not self.removal_effects:
            self.calculate_removal_effects()

        top_channel = max(
            self.removal_effects,
            key=self.removal_effects.get
        )

        lowest_channel = min(
            self.removal_effects,
            key=self.removal_effects.get
        )

        return {
            "journeys":
                len(self.df),

            "channels":
                len(self.channels),

            "baseline_conversion":
                self.base_conversion_rate,

            "total_revenue":
                self.get_total_revenue(),

            "avg_order_value":
                self.get_average_order_value(),

            "most_critical_channel":
                top_channel,

            "least_critical_channel":
                lowest_channel
        }

    # ======================================================
    # PIPELINE
    # ======================================================

    def execute_pipeline(self):

        if not self.transition_probabilities:
            self.build_transition_matrix()

        self.calculate_removal_effects()

        return self.removal_effects


# ======================================================
# LOCAL TEST
# ======================================================

if __name__ == "__main__":

    DATA_PATH = os.path.join(
        "core_logic",
        "user_journey_sequences.csv"
    )

    kernel = MarkovAttributionKernel(
        DATA_PATH
    )

    kernel.execute_pipeline()

    print("\nSUMMARY")
    print(kernel.get_summary())

    print("\nREVENUE ATTRIBUTION")
    print(kernel.get_revenue_attribution())

    print("\nREVENUE LOSS")
    print(kernel.get_revenue_loss_estimates())
    