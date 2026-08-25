# Paper Corpus Collection Protocol

## Corpus Origin

The 279-document analysis corpus was derived from the literature inventories
accompanying two reviews of medical and healthcare AI agents:

- Al Radi et al., *Agentic large-language-model systems in medicine: A
  systematic review and taxonomy* (2025); and
- Xu et al., *A comprehensive survey of AI Agents in Healthcare* (2026).

The inventories were obtained from the public project repositories associated
with those reviews (`AIM-Research-Lab/Awesome-AI-Agents-Medicine` and
`AgenticHealthAI/Awesome-AI-Agents-for-Healthcare`).

The AgentArena/SciAgentArena Markdown document was added as a prespecified
benchmark-alignment case. The final analysis manifest therefore contains 278
extracted paper documents plus AgentArena, for 279 records.

This is a curated-source corpus, not a systematic PubMed, Scopus, or Web of
Science search. Manuscript claims should describe it accordingly and should not
imply exhaustive coverage of healthcare agent literature.

## Collection Procedure

The source script `paper_extraction_parsing/paper_extract_from_readme.py`:

1. downloaded the README files from the two source repositories;
2. identified Markdown links whose labels, paths, or domains indicated a paper;
3. excluded common code and social-media domains;
4. accepted established publication, preprint, and proceedings domains;
5. normalized and deduplicated records by URL within the collection pass;
6. resolved direct PDF links or located PDFs from landing-page metadata; and
7. recorded the source repository, paper URL, resolved PDF URL, download status,
   HTTP status, and local filename in `paper_download_results.csv/json`.

Downloaded PDFs were converted to Markdown. The analysis script discovered one
Markdown file per extracted-paper directory, assigned a stable slug-based paper
identifier, resolved duplicate identifiers with a path-derived hash, and wrote
`data/reporting_completeness/paper_manifest.csv`.

## Analysis Eligibility

A record was eligible for the reporting-completeness analysis when a readable
Markdown extraction was available in the extraction tree. No publication was
excluded because it lacked a particular AGENT-O reporting field; missing fields
are the outcome being assessed. Paper type was assigned separately so that
benchmark, survey/review, governance/policy, method/model, and conceptual papers
could use `not_applicable` rather than being automatically penalized for absent
concrete-system details.

## Corpus Provenance Limitations

The collection index used during corpus assembly preserved source URLs and
download outcomes, but the current public manifest does not contain immutable
source-list revisions, complete DOI/arXiv metadata, source-document checksums,
or a fully reconstructed record-by-record deduplication and exclusion log.
These fields were not inferred retrospectively. The public manifest therefore
supports identification of the analyzed 279 records and verification of the
released scores, but not independent reconstruction of every collection step.

Paper types in the public manifest are the final v2.2.3 automated analytical
labels. They contain no `unclear` records, but they have not been fully
human-verified. Records selected for manual calibration are listed separately
in the public human-review queue.

If the study intends to make claims about the broader literature rather than
this curated corpus, a reproducible database search with explicit queries,
dates, screening criteria, and a PRISMA-style flow should replace or supplement
the current collection strategy.
