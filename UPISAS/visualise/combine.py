import pandas as pd

# Load the uploaded files
run_file_path = 'run.csv'
var_rate_file_path = 'var_rate_300.csv'

run_data = pd.read_csv(run_file_path)
var_rate_data = pd.read_csv(var_rate_file_path, header=None, names=['var_rate'])

# Ensure the `var_rate` data has indices corresponding to `image` numbers (1 to 300)
var_rate_data['image'] = var_rate_data.index + 1

# Merge `run_data` with `var_rate_data` based on the `image` column
combined_data = pd.merge(run_data, var_rate_data, on='image', how='left')


# Save the combined dataframe to a new CSV file
output_path = 'combined_run_var_rate.csv'
combined_data.to_csv(output_path, index=False)

