from jinja2 import Environment, FileSystemLoader
import pandas as pd
from datetime import date
import yaml
import json
import base64
import argparse

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--input_dir", "-i", type=str, required=True)
    argp.add_argument("--sample_name", "-s", type=str, required=True)
    argp.add_argument("--neg_control", "-n", type=str, required=True)

    args = argp.parse_args()

    input_dir = args.input_dir
    sample_name = args.sample_name
    neg_control = args.neg_control

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html.j2")

    #Load sample read assignment table
    assignment = pd.read_csv(f"{input_dir}/results/{sample_name}_downsampled.fastq_read-assignment-distributions.tsv", sep="\t")
    assignment_filtered = assignment.iloc[:, 1:]                                                                            # Select all columns except the first one
    assignment_summary = assignment_filtered.agg(['median', 'mean']).T.reset_index()                                        # Compute mean and median for each column    
    assignment_summary.columns = ['tax id', 'median*', 'mean*']                                                             # Rename columns


    # Load neg control abundance table
    neg_control_abundance = pd.read_csv(f"{input_dir}/results/{neg_control}_downsampled.fastq_rel-abundance.tsv", sep="\t")
    neg_control_filtered = neg_control_abundance.iloc[:, list(range(5)) + [13]]                                             # Filter for wanted columns
    neg_control_switched = neg_control_filtered[neg_control_filtered.columns[1:].append(neg_control_filtered.columns[:1])]  # Move the first column (taxid) to the end
    neg_control_ordered = neg_control_switched.sort_values(by="abundance", ascending=False)                                 # Sort based on descending abundance
    neg_control_ordered = neg_control_ordered.reset_index(drop=True)                                                        # Re-index the table

    # Load sample abundance table
    abundance = pd.read_csv(f"{input_dir}/results/{sample_name}_downsampled.fastq_rel-abundance.tsv", sep="\t")
    abundance_assignment = abundance_ordered.merge(assignment_summary, on="tax id", how="left")                             # Merge abundance and assignment
    
    # Spike species
    highlight = {"Truepera radiovictrix", "Imtechella halotolerans", "Allobacillus halotolerans"}
    #highlight = {"Aquabacterium parvum", "Bradyrhizobium embrapense"}
    
    def highlight_species(row):
        if row["species"] in highlight:
            return ["background-color: #ddd6fe"] * len(row)
        return [""] * len(row)
        
    def unique_species(row):
        if row["species"] not in neg_control_ordered["species"].values:
            return ["background-color: #dcfce7"] * len(row)
        return [""] * len(row)

    styled_1 = ordered_abundance.style.apply(unique_species, axis=1)
    styled = styled_1.apply(highlight_species, axis=1)
    neg_control_styled = neg_control_ordered.style.apply(highlight_species, axis=1)

    html_table = styled.to_html(index=False, border=0)
    neg_control_html_table = styled.to_html(index=False, border=0)

    legend_html = """
    <p class="text-gray-700 italic mt-2">
        <span class="inline-block w-4 h-4 bg-purple-200 mr-2 border"></span>
        Purple rows indicate spike species
        <span class="inline-block w-4 h-4 bg-green-100 ml-6 mr-2 border"></span>
        Green rows indicate species not found in negative control
    </p>
    """

    legend_neg_html = """
    <p class="text-gray-700 italic mt-2">
        <span class="inline-block w-4 h-4 bg-purple-200 mr-2 border"></span>
        Purple rows indicate spike species
    </p>
    """

    # Function to encode PNG to Base64
    def img_to_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    image_files = [f"{input_dir}/nanoplot_unprocessed/{sample_name}_nanoplot_unprocessed_LengthvsQualityScatterPlot_dot.png", f"{input_dir}/nanoplot_processed/{sample_name}_nanoplot_processed_LengthvsQualityScatterPlot_dot.png"]

    # Convert all images to Base64 strings
    images_base64 = [img_to_base64(path) for path in image_files]

    today = date.today().strftime("%Y-%m-%d")

    with open(f"{input_dir}/pipeline_info/software_versions.yml") as v:
        software_versions = yaml.safe_load(v)

    # Load MultiQC JSON
    with open(f"{input_dir}/multiqc/multiqc_data/multiqc_data.json") as f:
        multiqc_data = json.load(f)

    trana_version = software_versions["Workflow"]["genomic-medicine-sweden/TRANA"]

    html = template.render(
        table = styled.to_html(index=False),
        neg_control_table = neg_control_styled.to_html(index=False),
        legend = legend_html,
        legend_neg = legend_neg_html,
        today = today,
        pipeline_version = trana_version,
        multiqc_data  = multiqc_data,
        images = images_base64,
        input_dir = input_dir,
        sample_name = sample_name,
        neg_control = neg_control
    )

    with open("output/report.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    main()