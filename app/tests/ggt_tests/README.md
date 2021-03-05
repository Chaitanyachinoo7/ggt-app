# GGT Unit testing

Unit tests are written using `unittest`.

Unit tests for the app `GGT` is placed under the directory `app/tests/ggt_tests`

(Name `ggt_tests` was given to avoid package name conflicts with existing `ggt` package)

When placing unit tests, place them in the same folder structure as the `ggt` package.

Example is given below.
```
app
├── ggt
│   ├── lib
│       ├── adapters 
│           ├── stripe_adapter.py # py file to be tested
│           ├── ...  
├── ...
├── tests
│   ├── ggt_tests
│       ├── lib
│           ├── adapters 
│               ├── test_stripe_adapter.py # test py with tests
│               ├── ...
```

Name of the unit tests files should start with `test_`, this will allow `unittest` module to pick them.

## Running unit tests 

### Command line

- First run the following command,

```shell
export PYTHONPATH="${PYTHONPATH}:<ggt_project_directory>/app"
```

- Then from the project root directory run the following

```shell
python -m unittest discover -v  app/tests/ggt_tests
```

### Pycharm

- Open the Run/Debug configuration window
- Click on Add New Configuration button `+`
- Under Python Tests select `Unittests`
- Give a name
- Set the `Script Path` to `<ggt_project_directory>/app/tests/ggt_tests`
- Set the `Working directory` to `<ggt_project_directory>/app`
- Save and Run 