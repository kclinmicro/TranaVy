import argparse
from datetime import date
from jinja2 import Environment, FileSystemLoader
import json
import yaml
import pandas as pd
import pysam
import re
import statistics
import tomllib

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("-i", "--input-dir", type=str, required=True, help="Path to the input directory containing results")
    argp.add_argument("-o", "--output-file", type=str, required=True, help="Path to the output report file")
    argp.add_argument("-s", "--sample-name", type=str, required=True, help="Name of the sample")
    argp.add_argument("-n", "--neg-control", type=str, required=True, help="Name of the negative control")
    argp.add_argument("-c", "--config", type=str, default="configs/config.toml", help="Path to config file")
    argp.add_argument("-p", "--prob-score", action="store_true", help="Include probability score in the report")
    argp.add_argument("-m", "--alignment-metrics", action="store_true", help="Include metrics based on the raw alignment of reads to the database (perc identity and perc coverage)")

    args = argp.parse_args()

    # Read CSS file content
    with open("static/style.css", "r") as f:
        css_content = f.read()

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html.j2")

    # Load sample read assignment table
    assignment = pd.read_csv(f"{args.input_dir}/results/{args.sample_name}_downsampled.fastq_read-assignment-distributions.tsv", sep="\t")
    # Select all columns except the first one
    assignment_filtered = assignment.iloc[:, 1:]
    # Compute mean and median for each column
    assignment_summary = assignment_filtered.agg(['median', 'mean']).T.reset_index()
    # Rename columns
    assignment_summary.columns = ['tax id', 'median probability*', 'mean probability*']


    # Load neg control abundance table
    neg_control_abundance = pd.read_csv(f"{args.input_dir}/results/{args.neg_control}_downsampled.fastq_rel-abundance.tsv", sep="\t")
    # Filter for wanted columns
    neg_control_filtered = neg_control_abundance.iloc[:, list(range(5)) + [13]]
    # Move the first column (taxid)
    neg_control_switched = neg_control_filtered[neg_control_filtered.columns[1:5]
        .append(neg_control_filtered.columns[:1])
        .append(neg_control_filtered.columns[5:])]
    # Rename col names
    neg_control_switched = neg_control_switched.rename(
        columns={
            "estimated counts": "estimated read counts",
            "tax_id": "tax id"
        }
    )
    # Sort based on descending abundance
    neg_control_ordered = neg_control_switched.sort_values(by="abundance", ascending=False)
    # Re-index the table
    neg_control_ordered = neg_control_ordered.reset_index(drop=True)
    # Filter rows where abundance < 0.005
    neg_control_ordered = neg_control_ordered[
        neg_control_ordered["abundance"] > 0.005
    ]

    # Load sample abundance table
    abundance = pd.read_csv(f"{args.input_dir}/results/{args.sample_name}_downsampled.fastq_rel-abundance.tsv", sep="\t")
    # Filter for wanted columns
    abundance_filtered = abundance.iloc[:, list(range(5)) + [13]]
    # Move the first column (taxid)
    abundance_switched = abundance_filtered[abundance_filtered.columns[1:5]
        .append(abundance_filtered.columns[:1])
        .append(abundance_filtered.columns[5:])]
    # Rename col names
    abundance_switched = abundance_switched.rename(
        columns={
            "estimated counts": "estimated read counts",
            "tax_id": "tax id"
        }
    )
    # Sort based on descending abundance
    abundance_ordered = abundance_switched.sort_values(by="abundance", ascending=False)
    # Re-index the table
    abundance_ordered = abundance_ordered.reset_index(drop=True)                                                            
    # Filter rows where abundance < 0.005
    abundance_ordered = abundance_ordered[
        abundance_ordered["abundance"] > 0.005
    ]

    # Merge abundance and assignment if prob_score is given
    if args.prob_score:
        abundance_assignment = abundance_ordered.merge(assignment_summary, on="tax id", how="left")
    else:
        abundance_assignment = abundance_ordered                
    
    # Spike species
    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    highlight = set(config.get("spike_species", []))

    # Define function for spike species
    def highlight_species(row):
        if row["species"] in highlight:
            return ["background-color: #ddd6fe"] * len(row)
        return [""] * len(row)

    # Define function for unique species not found in negative control
    def unique_species(row):
        if row["species"] not in neg_control_ordered["species"].values:
            return ["background-color: #dcfce7"] * len(row)
        return [""] * len(row)

        # Define function for unique species not found in negative control
    def hundred_times_abundance(row):
        match = neg_control_ordered.loc[
        neg_control_ordered["species"] == row["species"], "abundance"
        ]
        if not match.empty and row["abundance"] > 100 * match.iloc[0]:
            return ["background-color: #bfdbfe"] * len(row)
        return [""] * len(row)

    # Apply functions for spike species and unique species
    styled_abundance = (abundance_assignment.style
        .apply(hundred_times_abundance, axis=1)
        .apply(unique_species, axis=1)
        .apply(highlight_species, axis=1)
        .format({
            "estimated read counts": "{:.0f}",
            "abundance": "{:.2%}"
            })
    )
    # Convert to html table
    html_table = styled_abundance.to_html(index=False, border=0)

    # Apply function for spike species
    styled_neg_control = (neg_control_ordered.style
        .apply(highlight_species, axis=1)
        .format({
            "estimated read counts": "{:.0f}",
            "abundance": "{:.2%}"
            })
    )
    # Convert to html table
    neg_control_html_table = styled_neg_control.to_html(index=False, border=0)

    legend_lines = [
        '<span class="inline-block w-4 h-4 bg-purple-200 mr-2 border"></span> Purple rows indicate spike species<br>',
        '<span class="inline-block w-4 h-4 bg-green-100 mr-2 border"></span> Green rows indicate species not found in negative control<br>',
        '<span class="inline-block w-4 h-4 bg-blue-200 mr-2 border"></span> Blue rows indicate species with abundances 100x greater than the negative control.<br>'
    ]
    # Optional line for probability score
    if args.prob_score:
        legend_lines.append(
            '<span class="not-italic text-sm"><span class="font-bold text-black">median/mean probability*</span>: Median/Mean probability of the assigned taxon across reads</span>'
        )

    legend_html = '<p class="text-gray-700 italic mt-2">'+ "".join(legend_lines) + '</p>'

    legend_neg_html = """
    <p class="text-gray-700 italic mt-2">
        <span class="inline-block w-4 h-4 bg-purple-200 mr-2 border"></span>
        Purple rows indicate spike species
    </p>
    """

    # Save date
    today = date.today().strftime("%Y-%m-%d")

    # Load software version
    with open(f"{args.input_dir}/pipeline_info/software_versions.yml") as v:
        software_versions = yaml.safe_load(v)

    # Load MultiQC JSON
    with open(f"{args.input_dir}/multiqc/multiqc_data/multiqc_data.json") as f:
        multiqc_data = json.load(f)

    # Load emu log and extract mapped value
    with open(f"{args.input_dir}/results/emu_logs/{args.sample_name}_emu_log.log") as f:
        emu_log = f.read()
    # Use regex to find the value between "mapped" and "sequences"
    match_mapped = re.search(r"mapped (.*?) sequences", emu_log)

    # If a match is found, extract the value; otherwise, set it to "N/A" (avoid errors if the pattern is not found)
    if match_mapped:
        mapped_value = match_mapped.group(1)
    else:
        mapped_value = "N/A"

    trana_version = software_versions["Workflow"]["genomic-medicine-sweden/TRANA"]

    html = template.render(
        css = css_content,
        table = html_table,
        neg_control_table = neg_control_html_table,
        legend = legend_html,
        legend_neg = legend_neg_html,
        today = today,
        pipeline_version = trana_version,
        multiqc_data  = multiqc_data,
        mapped_value = mapped_value,
        input_dir = args.input_dir,
        sample_name = args.sample_name,
        neg_control = args.neg_control
    )

    with open(args.output_file, "w") as f:
        f.write(html)

if __name__ == "__main__":
    main()
