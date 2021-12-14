# Abbot Python Skill Runner

This is the Python skill runner for Abbot hosted as an Azure Function (`abbot-skills-python`).

## Local Development

Start with `script/bootstrap`.

To run the Abbot Python runner locally:

`script/server`.

## Testing

Add tests by adding files in `src/tests` that match the pattern `test_*.py`.
We use the [`unittest` testing framework](https://docs.python.org/2/library/unittest.html).
Tests can viewed, run, and debugged in VS Code.

Run all tests from the command line with:

`script/test`

## Related Repositories

* [https://github.com/aseriousbiz/abbot](Abbot)

## Known Issues
Packages with C dependencies won't get compiled in Azure. We have to deploy binary versions (i.e. `psycopg2-binary`). 

GitHub Actions doesn't seem to be deploying binaries, so publish the app directly from the src directory when adding those dependencies: 

`func azure functionapp publish abbot-skills-python --python` 


