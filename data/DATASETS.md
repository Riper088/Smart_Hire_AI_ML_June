# Datasets — what to download and how

All datasets come from **Kaggle** (free account needed). Download them **once** and
place the CSVs directly under `data/raw/`. Never edit the files in `raw/`.

## What to download

Use these exact Kaggle slugs (verified live July 2026). A slug is the `owner/name`
part of the dataset URL — it is what the `kaggle datasets download -d` command needs.

| Dataset | Used for | Kaggle slug (`owner/name`) | What you get |
|---------|----------|----------------------------|--------------|
| **Updated Resume Dataset** (962 resumes, 25 categories) | Resume classifier (supervised) | `jillanisofttech/updated-resume-dataset` | `UpdatedResumeDataSet.csv` |
| **Jobs on Naukri.com** (~22k Indian jobs) | Job corpus / recommender | `PromptCloudHQ/jobs-on-naukricom` | `naukri_com-job_sample.csv` |
| **LinkedIn Job Postings 2023–2024** (~124k jobs) | Job corpus / recommender | `arshkon/linkedin-job-postings` | a `linkedin/` folder (see below) |

> **Resume + Naukri are the minimum** — those two alone build the whole core project.
> **LinkedIn is added on top** for more job variety and richer descriptions. The
> pipeline uses it automatically if present, and runs fine without it.
>
> If a slug ever 404s (owners get removed), search the dataset title on Kaggle and copy
> the new slug from the URL bar. The columns below stay the same across re-uploads.

## Exact columns you get

**`UpdatedResumeDataSet.csv`** — two columns:

| Column | What it holds |
|--------|---------------|
| `Category` | the label — the job category, one of 25 (Data Science, HR, Java Developer, Web Designing, Testing, …). This is your **y** for the classifier. |
| `Resume` | the full resume text. This is your **X** — clean it, TF-IDF it. |

**`naukri_com-job_sample.csv`** — many columns; you only need these six:

| Column in file | Rename to | 
|----------------|-----------|
| `jobtitle` | `title` |
| `company` | `company` |
| `joblocation_address` | `location` |
| `skills` | `skills` |
| `jobdescription` | `description` |
| `experience` | `experience` |

(The file also has `payrate`, `industry`, `education`, `postdate`, `jobid`, etc. — ignore them for the core project.)

**LinkedIn** unzips into a `linkedin/` folder. Only three files are used; the rest can be deleted:

```
data/raw/linkedin/
├── postings.csv            main job table
├── jobs/job_skills.csv     skills per job, as codes (job_id, skill_abr)
└── mappings/skills.csv     code → skill name (skill_abr, skill_name)
```

Skills are split across two files. `preprocess.py` joins `job_skills.csv` to
`mappings/skills.csv` on `skill_abr`, then groups to one skills string per `job_id`.
The mapped columns are:

| Column in LinkedIn | Rename to |
|--------------------|-----------|
| `title` | `title` |
| `company_name` | `company` |
| `location` | `location` |
| *(joined skills string)* | `skills` |
| `description` | `description` |
| `formatted_experience_level` | `experience` |

> LinkedIn's skills are broad categories (Marketing, Design, …), not granular tech
> skills. Naukri's `skills` are more specific, so the skill-gap report leans on Naukri.

## How to get them — Option A: one script (easiest)

Run the helper script from the project root. It downloads both core datasets and
places the CSVs in `data/raw/` with the right names:

```
pip install kagglehub
python download_data.py
```

The first run asks for your Kaggle credentials (username + API key from
Kaggle → Settings → **API** → **Create New Token**). After it finishes, check
`data/raw/` for `UpdatedResumeDataSet.csv` and `naukri_com-job_sample.csv`.

For LinkedIn, download `arshkon/linkedin-job-postings` and unzip it into
`data/raw/linkedin/` (Option B or C below). You only need the three files listed
above; delete the rest.

## How to get them — Option B: Kaggle website (no code)

1. Create a free account at <https://www.kaggle.com>.
2. Search the term from the table above (e.g. "resume dataset").
3. Open the dataset page → click **Download** (downloads a `.zip`).
4. Unzip it and move the `.csv` file into this project's `data/raw/` folder.
5. Repeat for each dataset you need.

## How to get them — Option C: Kaggle API (command line)

Do this once so you can download by command instead of clicking.

1. Install the client:
   ```
   pip install kaggle
   ```
2. Get your API token: Kaggle → your profile → **Settings** → **API** →
   **Create New Token**. This downloads `kaggle.json`.
3. Put `kaggle.json` where Kaggle expects it:
   - Windows: `C:\Users\<you>\.kaggle\kaggle.json`
   - macOS/Linux: `~/.kaggle/kaggle.json`
4. Download the two core datasets straight into `data/raw/`:
   ```
   kaggle datasets download -d jillanisofttech/updated-resume-dataset -p data/raw --unzip
   kaggle datasets download -d PromptCloudHQ/jobs-on-naukricom -p data/raw --unzip
   ```
   For LinkedIn, download into `data/raw/linkedin/`:
   ```
   kaggle datasets download -d arshkon/linkedin-job-postings -p data/raw/linkedin --unzip
   ```

## After downloading

1. Confirm the files are in `data/raw/`:
   ```
   data/raw/UpdatedResumeDataSet.csv
   data/raw/naukri_com-job_sample.csv
   data/raw/linkedin/postings.csv          (optional)
   ```
2. Filenames are already set in `src/config.py` (`RESUME_CSV`, `NAUKRI_CSV`,
   `LINKEDIN_*`). Only edit those if your filenames differ.
3. Load and inspect them in `notebooks/01_eda.ipynb` (`df.head()`, `df.shape`,
   `df['Category'].value_counts()`).

## Building the job corpus

The recommender searches against **one** combined job table, not the separate files.
This is already implemented in `src/data/preprocess.py` — run it from the project root:

```
python -m src.data.preprocess
```

It renames each source to the common schema (**title, company, location, skills,
description, experience**), stacks them, drops duplicates and empty rows, builds a
cleaned `text` column for TF-IDF, and writes:

```
data/interim/job_corpus.csv       merged job table
data/processed/jobs_clean.csv     + cleaned text column (recommender input)
data/processed/resumes_clean.csv  cleaned resume text + Category (classifier input)
```

LinkedIn is merged in automatically if `data/raw/linkedin/postings.csv` exists;
otherwise the corpus is built from Naukri alone.
