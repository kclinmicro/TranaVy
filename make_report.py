from jinja2 import Environment, FileSystemLoader
import pandas as pd
from datetime import date
import yaml
import json
import argparse
import tomllib

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--input_dir", "-i", type=str, required=True, help="Path to the input directory containing results")
    argp.add_argument("--sample_name", "-s", type=str, required=True, help="Name of the sample")
    argp.add_argument("--neg_control", "-n", type=str, required=True, help="Name of the negative control")
    argp.add_argument("--config", "-c", type=str, default="configs/config.toml", help="Path to config file")

    args = argp.parse_args()

    input_dir = args.input_dir
    sample_name = args.sample_name
    neg_control = args.neg_control
    config_path = args.config

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html.j2")

    # Load sample read assignment table
    assignment = pd.read_csv(f"{input_dir}/results/{sample_name}_downsampled.fastq_read-assignment-distributions.tsv", sep="\t")
    # Select all columns except the first one
    assignment_filtered = assignment.iloc[:, 1:]                                                                            
    # Compute mean and median for each column
    assignment_summary = assignment_filtered.agg(['median', 'mean']).T.reset_index()                                            
    # Rename columns
    assignment_summary.columns = ['tax id', 'median*', 'mean*']                                                             


    # Load neg control abundance table
    neg_control_abundance = pd.read_csv(f"{input_dir}/results/{neg_control}_downsampled.fastq_rel-abundance.tsv", sep="\t")
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

    # Load sample abundance table
    abundance = pd.read_csv(f"{input_dir}/results/{sample_name}_downsampled.fastq_rel-abundance.tsv", sep="\t")
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
    
    # Merge abundance and assignment
    abundance_assignment = abundance_ordered.merge(assignment_summary, on="tax id", how="left")                             
    
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

    # Apply functions for spike species and unique species
    styled_abundance = (abundance_assignment.style                                                                          
        .apply(unique_species, axis=1)
        .apply(highlight_species, axis=1)
        .format({"estimated read counts": "{:.0f}"})
    )
    # Convert to html table
    html_table = styled_abundance.to_html(index=False, border=0)                                                            

    # Apply function for spike species
    styled_neg_control = (neg_control_ordered.style
        .apply(highlight_species, axis=1)                                                                                   
        .format({"estimated read counts": "{:.0f}"})
    )
    # Convert to html table
    neg_control_html_table = styled_neg_control.to_html(index=False, border=0)                                              

    legend_html = """
    <p class="text-gray-700 italic mt-2">
        <span class="inline-block w-4 h-4 bg-purple-200 mr-2 border"></span>
        Purple rows indicate spike species
        <span class="inline-block w-4 h-4 bg-green-100 ml-14 mr-2 border"></span>
        Green rows indicate species not found in negative control<br>
        <span class="not-italic text-sm"><span class="font-bold text-black">median*/mean*</span>: Median/Mean probability of the assigned taxon across reads</span>
    </p>
    """

    legend_neg_html = """
    <p class="text-gray-700 italic mt-2">
        <span class="inline-block w-4 h-4 bg-purple-200 mr-2 border"></span>
        Purple rows indicate spike species
    </p>
    """

    # Save date
    today = date.today().strftime("%Y-%m-%d")
    
    # Load software version
    with open(f"{input_dir}/pipeline_info/software_versions.yml") as v:
        software_versions = yaml.safe_load(v)

    # Load MultiQC JSON
    with open(f"{input_dir}/multiqc/multiqc_data/multiqc_data.json") as f:
        multiqc_data = json.load(f)

    trana_version = software_versions["Workflow"]["genomic-medicine-sweden/TRANA"]

    html = template.render(
        table = html_table,
        neg_control_table = neg_control_html_table,
        legend = legend_html,
        legend_neg = legend_neg_html,
        today = today,
        pipeline_version = trana_version,
        multiqc_data  = multiqc_data,
        input_dir = input_dir,
        sample_name = sample_name,
        neg_control = neg_control
    )

    with open("output/report.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    main()