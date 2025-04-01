import os
import sys

import pandas as pd

cache_types = {"1": "PostgreSQL", "2": "Redis",
               "3": "Memcached", "4": "PythonDict"}

tests_folder_path = sys.argv[1]


df_stats = pd.DataFrame()
for file in os.listdir(tests_folder_path):
    filename = os.fsdecode(file)
    if filename.endswith(".log"):
        test_csv_log_path = os.path.join(tests_folder_path, filename)
        print(filename)
        df = pd.read_csv(test_csv_log_path)
        # print(df.sample())

        mean_response = df['delta_time'].mean()
        print(mean_response)

        delta_time_sum = df['delta_time'].sum()
        print(delta_time_sum)

        mean_hit_response = df.loc[df['cache_action'] == True, 'delta_time'].mean()
        mean_miss_response = df.loc[df['cache_action'] == False, 'delta_time'].mean()

        row_count = len(df)

        hit_rate = df.loc[df['cache_action'] ==
                          True, 'cache_action'].count() / row_count
        miss_rate = df.loc[df['cache_action'] ==
                           False, 'cache_action'].count() / row_count

        secs = delta_time_sum / 1000
        mins = secs / 60
        hrs = mins / 60
        splitDash = filename.split('_')
        trace_file = splitDash[0]
        cache_type = splitDash[-1][0]

        throughput = row_count / secs
        stats_row = {'cache_type': cache_types[cache_type],
                     'trace_file': filename.split('_')[0],
                     #  'secs': "{:.4f}".format(secs),
                     'mins': "{:.4f}".format(mins),
                     'hrs': "{:.4f}".format(hrs),
                     'mean_response (m/s)': "{:.4f}".format(mean_response),
                     'mean_hit_response (m/s)': "{:.4f}".format(mean_hit_response),
                     'mean_miss_response (m/s)': "{:.4f}".format(mean_miss_response),
                     'throughput (per sec)': "{:.4f}".format(throughput),
                     'hit_rate %': "{:.4f}".format(hit_rate),
                     'miss_rate %': "{:.4f}".format(miss_rate)}

        df_stats = pd.concat(
            [df_stats, pd.DataFrame([stats_row])], ignore_index=True)
    # break


# df_stats = pd.read_csv(os.path.join(tests_folder_path, 'stats.csv'))

df_stats = df_stats.sort_values(by=['trace_file', 'mean_response (m/s)'])
df_stats.to_csv(os.path.join(tests_folder_path, 'stats.csv'), index=False)
