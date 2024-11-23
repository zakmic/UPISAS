import pandas as pd

# Load the uploaded files
run_path = 'run.csv'
var_rate_300_path = 'var_rate_300.csv'

run_df = pd.read_csv(run_path)
var_rate_300_df = pd.read_csv(var_rate_300_path)

# Display the first few rows of each dataframe to understand their structure
run_df.head(), var_rate_300_df.head()

# Renaming the column in var_rate_300 for clarity
var_rate_300_df.columns = ['var_rate']

# Ensure lengths align or trim the longer file
min_length = min(len(run_df), len(var_rate_300_df))
run_df_trimmed = run_df.iloc[:min_length].reset_index(drop=True)
var_rate_300_trimmed = var_rate_300_df.iloc[:min_length].reset_index(drop=True)

# Combine the two dataframes
combined_df = pd.concat([run_df_trimmed, var_rate_300_trimmed], axis=1)
# Save the combined dataframe to a new CSV file
output_path = 'combined_run_var_rate.csv'
combined_df.to_csv(output_path, index=False)
