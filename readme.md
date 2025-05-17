# 🗃️ GUARD
Austrian data anonymization at ease. GUARD builds on top of [Microsoft Presidio](https://github.com/microsoft/presidio) and makes use of multiple open source `NER` / `transformer` models to detect sensitive data.

## Documentation
Detailed documentation can be found under `guard/guard-documentation`. The documentation is built on top of [Docusaurus](https://docusaurus.io).

To start the webserver serving the documentation:
```bash
    npx docusaurus start
```
## Curerntly supported languages
- DE
- EN
- IT (experimental)

## Currently supported entities
- `AUT_LICENSE_PLATE`: Austrian license plate.
- `PERSON`: Names of people, either given name, surname or fullname.
- `LOCATION`: Address, City, Country, State.
- `ORG`: Organizations e.g. Google.
- `PHONE`: Phone numbers.
- `EMAIL`: Email addresses.

## Evaluation
Since the target language is `German` multiple analyzer engines were benchmarked on German synthetic data. The synthetic data was generated via OpenAI's [Chat GPT](https://chatgpt.com/) entailing realistic Austrian data. The data itself was used to populate templates in the form of:

> My name is {{name}} I am 32 years old and live in {{address}}

These templates were populated with the synthetic data and 1500 rows were generated. We then evaluated the data on different models: `distillbert` (transfomer), `piiranha` (transfomer), `spacy` (NER model), `stanza` (NER model), and `flair` (in combination with the transfomers) to select the best model. The respective Notebooks can be found under [experiments](/processing_experiments/experiment).