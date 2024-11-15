import pandas as pd
import matplotlib.pyplot as plt
import os

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def plot_all_metrics(csv_directory, output_directory, show_plots=False):
    create_directory(output_directory)

    all_data = []

    for csv_file in os.listdir(csv_directory):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(csv_directory, csv_file)
            
            data = pd.read_csv(file_path)
            
            if "Method" not in data.columns:
                print(f"Skipping {csv_file}: 'Method' column is missing.")
                continue
            
            all_data.append(data)

    combined_data = pd.concat(all_data, ignore_index=True)

    metrics = [col for col in combined_data.columns if col not in ["Run", "Method"]]

    averages = combined_data.groupby("Method")[metrics].mean()

    for metric in metrics:
        plt.figure(figsize=(12, 6))
        
        # Bar chart
        averages[metric].plot(kind="bar", color="skyblue", edgecolor="black")
        plt.title(f"Comparison of {metric} Across Methods (Bar)", fontsize=16)
        plt.xlabel("Method", fontsize=12)
        plt.ylabel(metric, fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        bar_output_file = os.path.join(output_directory, f"{metric}_comparison_bar.png")
        plt.savefig(bar_output_file)
        print(f"Saved bar plot for {metric}: {bar_output_file}")
        if show_plots:
            plt.show()
        else:
            plt.close()

        # Line chart
        plt.figure(figsize=(12, 6))
        plt.plot(averages.index, averages[metric], marker="o", color="red", label=metric)
        plt.title(f"Comparison of {metric} Across Methods (Line)", fontsize=16)
        plt.xlabel("Method", fontsize=12)
        plt.ylabel(metric, fontsize=12)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        line_output_file = os.path.join(output_directory, f"{metric}_comparison_line.png")
        plt.savefig(line_output_file)
        print(f"Saved line plot for {metric}: {line_output_file}")
        if show_plots:
            plt.show()
        else:
            plt.close()

def main():
    csv_directory = "metrics"
    output_directory = "plots"
    show_plots = False

    plot_all_metrics(csv_directory, output_directory, show_plots)

if __name__ == "__main__":
    main()
