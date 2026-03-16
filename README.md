# 16s-report

This repository contains a small reporting tool for generating a static HTML report from results produced by the [TRANA](https://github.com/genomic-medicine-sweden/TRANA) taxonomic profiling pipeline for 16S rRNA reads.

The script parses pipeline outputs and renders a human-readable summary report using a Jinja2 HTML template and CSS styling.

## Repository Contents

| File                         | Description                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| `make_report.py`             | Python script that parses pipeline output and generates the report                               |
| `configs/config.toml`        | Configuration file for customizing report generation                                             |
| `templates/template.html.j2` | Jinja2 template used to render the HTML report                                                   |
| `static/style.css`           | CSS styling for the report                                                                       |
| `output/`                    | Directory where the generated HTML report (`report.html`) will be saved after running the script |
| `README.md`                  | Project documentation                                                                            |

## Usage

Run the report generator using the Python script:

```bash
python make_report.py --input_dir <results_directory> \
                 --sample_name <sample_name> \
                 --neg_control <negative_control_name> \
                 [--config config.toml]
```

### Example

```bash
python make_report.py \
  --input_dir results/sample_01 \
  --sample_name sample_01 \
  --neg_control neg_control \
  --config config.toml
```

### Arguments

| Argument        | Short | Required | Description                                             |
| --------------- | ----- | -------- | ------------------------------------------------------- |
| `--input_dir`   | `-i`  | Yes      | Path to the directory containing TRANA pipeline results |
| `--sample_name` | `-s`  | Yes      | Name of the sample to generate the report for           |
| `--neg_control` | `-n`  | Yes      | Name of the negative control sample                     |
| `--config`      | `-c`  | No       | Path to configuration file (default: `config.toml`)     |

### Customization

The report can be customized to the users spike species by editing the already existing, or creating a new, `config.toml` file and supplying it through `--config` (`-c`).

### Output

The script generates a **static HTML report** (`report.html`) in the `output/` directory summarizing results from the [TRANA](https://github.com/genomic-medicine-sweden/TRANA) pipeline. The report contains:

#### Summary Statistics

Key sequencing metrics, including number of reads, mean/median read length and read quality (Phred score), read length N50, standard deviation (STDEV) of read lengths, and total bases.

#### Sample Abundance Table

A table summarizing the abundance and taxonomic composition of the sample, with the following columns:

| Column                | Description                                           |
| --------------------- | ----------------------------------------------------- |
| Abundance             | Relative abundance of the taxon                       |
| Species               | Assigned species                                      |
| Genus                 | Assigned genus                                        |
| Family                | Assigned family                                       |
| TaxID                 | NCBI Taxonomy ID                                      |
| Estimated read counts | Number of reads assigned                              |
| Median                | Median probability of the assigned taxon across reads |
| Mean                  | Mean probability of the assigned taxon across reads   |

**Color coding:**

- **Purple rows** indicate spike species
- **Green rows** indicate species absent in negative control

#### Negative Control Table

A table summarizing the negative control sample, with the same first 6 columns as the previous table.

**Color coding:**

- **Purple rows** indicate spike species
