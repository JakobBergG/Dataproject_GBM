## How to use settings.json

In order to specify where data etc. is located, you must create a settings.json file in the location where you run the scripts.
Specify "path_" followed by the keyword folder you want to specify. You can use "../" to go to the folder above your current location.

Example of settings.json:

```json
{
    "path_data": "../Glioblastoma_proj/data",
    "path_info": "info",
    "path_output": "metrics_output"
}
```


## Conda environment student pc

The conda environment on the student pc is called `data_sciene_project`.