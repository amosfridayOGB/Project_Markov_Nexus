import pandas as pd

df = pd.read_csv("core_logic/user_journey_sequences.csv")

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\nHEAD:")
print(df.head())

print("\nSHAPE:")
print(df.shape)
