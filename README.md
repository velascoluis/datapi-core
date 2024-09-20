# datapi

`datapi` is a Python package that allows you to deploy data resources, list them, and generate documentation, similar to how `dbt` operates.

## Installation
```bash
pip install -e .
```

## Usage

- **Deploy Resources**

  ```bash
  datapi run --all
  ```

- **List Resources**

  ```bash
  datapi show --all
  ```

- **Generate Documentation**

  ```bash
  datapi docs generate
  ```

## Getting Started

### Initialize a New Project

To create a new `datapi` project, run:

```bash
datapi init [PROJECT_NAME]
```

If you don't specify a project name, it will default to 'datapi_project'.

Example:

```
## Commands

- **Initialize Project**

  ```bash
  datapi init [PROJECT_NAME]
  ```

- **Deploy Resources**

  ```bash
  datapi run --all --project [PROJECT_NAME]
  ```

- **List Resources**

  ```bash
  datapi show --all --project [PROJECT_NAME]
  ```

- **Generate Documentation**

  ```bash
  datapi docs generate --project [PROJECT_NAME]
  ```

## Notes

- Run `datapi` commands from the directory containing your datapi project.
- If you don't specify a project name with the `--project` option, datapi will attempt to find a project in the current directory.