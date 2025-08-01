# CBD Logistics Survey Analysis - Medellín 2025

## Overview

This repository contains the data analysis pipeline for a logistics survey conducted in the Central Business District (CBD) of Medellín, Colombia. The research focuses on understanding specific logistics needs within CBDs and how alignment of supply and demand can inform Urban Consolidation Center (UCC) implementation in Low Emission Zones (LEZs).

## Research Question

**What are the specific logistics needs within CBDs, and how can alignment of supply and demand inform UCC implementation in LEZs?**

## Project Structure

```
CBD_MDE_2025/
├── code/
│   ├── python/
│   │   ├── datacleaning.py              # Data cleaning utilities
│   │   ├── final_mario_plots_and_analysis.ipynb
│   │   ├── plots_and_analysis.ipynb     # Visualization and analysis
│   │   ├── plots_and_analysis.py
│   │   ├── survey_cleaning.py           # Survey data preprocessing
│   │   ├── unified.py                   # Unified analysis pipeline
│   │   ├── v2_plots_and_analysis.ipynb
│   │   └── v3_data_cleaning.ipynb       # Latest data cleaning pipeline
│   └── R/
│       ├── Analysis_survey_29072025.Rmd
│       ├── FTG_models_CBD.Rmd
│       └── multivariate_analysis_survey_29072025.Rmd
├── data/
│   ├── intermediate/
│   │   ├── df_clean.csv                 # Cleaned dataset
│   │   ├── mario_clean.csv
│   │   ├── survey_for_famd.csv          # Data prepared for FAMD analysis
│   │   └── translated_survey.csv        # Translated survey responses
│   └── raw/
│       ├── 03. Resultados_encuesta_logistica_ZUAP_20220927_v1.xlsx
│       ├── 03. Resultados_encuesta_logistica_ZUAP_20220927_v1.csv
│       └── clean_survey.xlsx
├── requirements.txt                     # Python dependencies
├── CBD_MDE_2025.Rproj                  # R project file
└── README.md
```

## Dataset Description

The survey data includes responses from businesses and establishments in Medellín's CBD, covering:

- **Company Information**: Name, contact details, employee demographics
- **Logistics Operations**: Supply frequency, delivery schedules, vehicle types
- **Infrastructure**: Warehouse facilities, loading/unloading methods
- **Safety Perceptions**: Risk assessment for different transport modes
- **Gender Inclusion**: Female participation in logistics operations
- **Economic Activity**: Business types and main products/services

## Key Features

### Data Processing Pipeline
- **Text Normalization**: Accent removal, case standardization
- **Translation**: Spanish to English for international collaboration
- **Multi-label Encoding**: One-hot encoding for categorical variables
- **Data Validation**: Comprehensive cleaning and type conversion

### Analysis Components
- **Factor Analysis of Mixed Data (FAMD)**: For mixed-type variables
- **Clustering Analysis**: To identify business segments
- **Correspondence Analysis**: For categorical relationships
- **Visualization**: Interactive plots and statistical graphics

## Installation & Setup

### Python Environment
```bash
# Create virtual environment
python -m venv venv_cbd
source venv_cbd/bin/activate  # On Windows: venv_cbd\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### R Environment
```r
# Install required packages
install.packages(c("FactoMineR", "factoextra", "dplyr", "ggplot2", "readr"))
```

## Usage

### Data Cleaning

#### Option 1: Using the Unified Pipeline
The main data cleaning pipeline is in `unified.py`:
```python
from code.python.unified import clean_survey

# Load and process survey data
df_clean = clean_survey()  # Uses default paths
# Or specify custom path
df_clean = clean_survey("path/to/raw/data.xlsx")
```

#### Option 2: Using Jupyter Notebooks
Alternative pipeline in `v3_data_cleaning.ipynb`:
```python
# Load and process survey data
df_clean = dataframe_cleaning("path/to/raw/data.xlsx")
# Apply translations and create dummy variables
df_translated = translate_survey_data(df_clean)
df_with_dummies = create_dummy_variables(df_translated)
```

### Data Types & Processing
The unified pipeline applies:
- **Numeric conversion**: Counts, areas, heights, delivery numbers
- **Categorical typing**: Single-label variables with proper categories
- **Ordered factors**: Likert scales (1-5), supply frequency, warehouse floors
- **Multi-label preservation**: Comma-separated text fields for later expansion
- **Text normalization**: Accent removal, case standardization for Spanish text

### Analysis
Run the analysis notebooks in sequence:
1. `v3_data_cleaning.ipynb` - Data preprocessing
2. `plots_and_analysis.ipynb` - Exploratory data analysis
3. `final_mario_plots_and_analysis.ipynb` - Final visualizations

## Key Findings

*This section will be updated as analysis progresses*

## Data Dictionary

### Numeric Variables (Counts & Measures)
- `number_warehouse`: Number of warehouse spaces available
- `warehouse_area`: Warehouse area in square meters
- `warehouse_height`: Warehouse height in meters
- `num_deliveries`: Daily number of home deliveries
- `num_online_deliveries`: Daily number of online order deliveries
- `employees`: Total number of employees
- `female_employees`: Number of female employees
- `female_emplo_distri`: Number of women in distribution chain
- `female_distri_vincu`: Number of women with formal employment contracts in distribution

### Percentage Variables
- `women_distri_percentage`: Percentage of women in distribution
- `hired_women_percentage`: Percentage of hired women with contracts

### Likert Scale Variables (1-5, Ordered)
- `supply_safety_percep`: Safety perception for motorized vehicle loading/unloading (1=very unsafe, 5=very safe)
- `supply_bic_safety_perception`: Safety perception for bicycle loading/unloading (1=very unsafe, 5=very safe)

### Ordered Categorical Variables
- `warehouse_floor`: Floor level where warehouse is located (ordered by numeric value)
- `supply_frequency_num`: Supply frequency per week (1, 2, 5, 6+ times)

### Single-Label Categorical Variables
- `main_products`: Main products/services offered (normalized text)
- `warehouse`: Whether establishment has warehouse space (yes/no)
- `zuap_warehouse`: Whether warehouse is located within ZUAP zone (yes/no/not applicable)
- `warehouse_municipality`: Municipality where warehouse is located
- `warehouse_type`: Type of warehouse facility
- `economic_activity`: Primary economic activity category
- `female_support`: Support provided for women in logistics training

### Multi-Label Text Variables (Comma-separated)
- `specific_activity`: Top 3 commercial activities (in order of importance)
- `supply_day`: Days of the week when supplies are received
- `supply_schedule`: Time schedules for loading/unloading activities
- `supply_unloading`: Methods used for unloading merchandise
- `warehouse_equipement`: Equipment available for loading/unloading
- `delivery_transp_mode`: Transportation modes used for home deliveries
- `online_trans_mode`: Transportation modes used for online order deliveries
- `female_popg`: Female population groups represented in workforce

### Derived Variables
- `econ_main`: Main economic activity category (split from economic_activity)
- `econ_sub1`: First subcategory of economic activity
- `econ_sub2`: Second subcategory of economic activity

## Contributing

This research is part of an academic project. For questions or collaboration opportunities, please contact the research team.

## License

This project is for academic research purposes. Please cite appropriately if using any part of this analysis.

## Citation

```
CBD Logistics Survey Analysis - Medellín 2025
Universidad Nacional de Colombia
Research on Urban Consolidation Centers and Low Emission Zones
```

## Contact

- **Researcher**: Carlos Grnada
- **Institution**: University of Antwerp
- **Email**: carlos.grandamunoz@uantwerpen.be

---

*Last updated: August 2025*
