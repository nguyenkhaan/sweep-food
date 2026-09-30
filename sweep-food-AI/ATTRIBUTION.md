# Attribution & Source Provenance

The SweepFood dataset is **derived** from publicly accessible Vietnamese recipe
web pages. The published dataset contains only factual, structured data
(normalized dish names, ingredient lists, quantities, estimated weights, and
nutrition values) together with the original `source_url` for each recipe so
that users can consult the original page. No verbatim instruction text,
editorial description, photograph, or original creative title from the sources
is redistributed.

## Sources

| Platform (`source_platform`) | Domain | Recipes (published) |
|---|---|---|
| `monngonmoingay` | monngonmoingay.com | 1,963 |
| `dienmayxanh` | dienmayxanh.com | 1,865 |
| `cookpad` | cookpad.com | 1,813 |
| **Total** | | **5,641** |

Each recipe row retains `source_platform` and `source_url` for full traceability
back to the originating page.

## Nutrition reference

Master-ingredient nutrition values are derived from the Vietnamese food
composition data published by the National Institute of Nutrition (Viện Dinh
Dưỡng), processed under `data/processed/viendinhduong/`.

## Usage terms

- The derived dataset is released under **CC BY 4.0** (see `DATA_LICENSE`).
- When using this dataset, please credit "SweepFood Vietnamese Recipe–Nutrition
  Dataset" and retain the `source_url` provenance.
- Users who wish to access the original recipe pages (instructions, photos,
  descriptions) must obtain them directly from the source websites under those
  sites' own terms of service. Those materials are the property of their
  respective owners and are **not** part of this release.

## Reproducibility note

The verbatim crawl snapshot (`data/raw/recipes_raw_scraped.json`), which holds
original text and media URLs, is kept only in the local working copy for
pipeline reproducibility and is excluded from version control and the published
dataset.
