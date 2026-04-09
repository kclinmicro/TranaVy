# TranaVy

This repository contains a small reporting tool for generating a static HTML
report from results produced by the
[TRANA](https://github.com/genomic-medicine-sweden/TRANA) taxonomic profiling
pipeline for 16S rRNA reads.

The script parses pipeline outputs and renders a human-readable summary report
using a Jinja2 HTML template and CSS styling.

## Repository Contents

| File                         | Description                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------ |
| `make_report.py`             | Python script that parses pipeline output and generates the report                               |
| `configs/config.toml`        | Configuration file for customizing report generation                                             |
| `templates/template.html.j2` | Jinja2 template used to render the HTML report                                                   |
| `static/style.css`           | CSS styling for the report                                                                       |
| `output/`                    | Directory where the generated HTML report (`report.html`) will be saved after running the script |
| `README.md`                  | Project documentation                                                                            |

## Setup

This project uses dependencies defined in pyproject.toml and requires Python
≥3.11. You can set up the environment using either Conda or Pixi.

### Dependencies

- python >=3.11,<=3.13
- jinja2
- pandas
- pysam
- pyyaml

## Usage

Run the report generator using the Python script:

```bash
python make_report.py --input-dir <results_directory> \
                 --output-file <output_file> \
                 --sample-name <sample_name> \
                 --neg-control <negative_control_name> \
                 [--config config.toml] \
                 [--prob-score] \
                 [--alignment-metrics]
```

### Example
Generating a report without probability scores:
```bash
python make_report.py \
  --input-dir results/sample_01 \
  --output-file output/sample_01_report.html \
  --sample-name sample_01 \
  --neg-control neg_control \
  --config config.toml
```

Generating a report with probability scores:
```bash
python make_report.py \
  --input-dir results/sample_01 \
  --output-file output/sample_01_report.html \
  --sample-name sample_01 \
  --neg-control neg_control \
  --config config.toml \
  --prob-score
```

### Arguments

| Argument              | Short | Required | Description                                                                                                 |
| ---------------       | ----- | -------- | -------------------------------------------------------                                                     |
| `--input-dir`         | `-i`  | Yes      | Path to the directory containing TRANA pipeline results                                                     |
| `--output-file`       | `-o`  | Yes      | Name of the output html report generated                                                                    |
| `--sample-name`       | `-s`  | Yes      | Name of the sample to generate the report for                                                               |
| `--neg-control`       | `-n`  | Yes      | Name of the negative control sample                                                                         |
| `--config`            | `-c`  | No       | Path to configuration file (default: `config.toml`)                                                         |
| `--prob-score`        | `-p`  | No       | Handle to use for generating probability scores                                                             |
| `--alignment-metrics` | `-m`  | No       | Include metrics based on the raw alignment of reads to the database (percent identity and percent coverage) |

### Customization

The report can be customized to the users spike species by editing the already
existing, or creating a new, `config.toml` file and supplying it through
`--config` (`-c`).

### Output

The script generates a **static HTML report** (`report.html`) in the `output/`
directory summarizing results from the
[TRANA](https://github.com/genomic-medicine-sweden/TRANA) pipeline. The report
contains:

#### Summary Statistics

Key sequencing metrics, including number of reads (before downsampling),
mean/median read length and read quality (Phred score), read length N50,
standard deviation (STDEV) of read lengths, total bases and number of mapped
reads.

#### Sample Abundance Table

A table summarizing the abundance and taxonomic composition of the sample, with
the following columns:

| Column                | Description                                           |
| --------------------- | ----------------------------------------------------- |
| Abundance             | Relative abundance of the taxon                       |
| Species               | Assigned species                                      |
| Genus                 | Assigned genus                                        |
| Family                | Assigned family                                       |
| TaxID                 | NCBI Taxonomy ID                                      |
| Estimated read counts | Number of reads assigned                              |
| Median probability*   | Median probability of the assigned taxon across reads |
| Mean probability*     | Mean probability of the assigned taxon across reads   |

*: The two columns for median and mean probability is by default not included in the table. These can be added by supplying --prob_score (-p).

**Color coding:**

- **Purple rows** indicate spike species
- **Green rows** indicate species absent in negative control or with abundances 100x greater than the negative control

#### Negative Control Table

A table summarizing the negative control sample, with the same first 6 columns as the previous table.

**Color coding:**

- **Purple rows** indicate spike species
