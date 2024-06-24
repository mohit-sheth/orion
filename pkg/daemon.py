"""
Module to run orion in daemon mode
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from jinja2 import Template
import pkg_resources
import yaml
from pkg.logrus import SingletonLogger
from pkg.types import OptionMap

from . import runTest

app = FastAPI()
logger_instance = SingletonLogger(debug=logging.INFO).logger


@app.get("/daemon/changepoint")
async def daemon_changepoint(
    version: str = "4.17",
    uuid: str = "",
    baseline: str = "",
    filter_changepoints="",
    test_name="small-scale-cluster-density",
):
    """starts listening on port 8000 on url /daemon

    Args:
        file (UploadFile, optional): config file for the test. Defaults to File(...).

    Returns:
        json: json object of the changepoints and metrics
    """
    parameters = {"version": version}
    config_file_name=test_name+".yml"
    option_arguments = {
        "config": config_file_name,
        "output_path": "output.csv",
        "hunter_analyze": True,
        "anomaly_detection": False,
        "output_format": "json",
        "uuid": uuid,
        "baseline": baseline,
        "configMap": render_template(config_file_name, parameters),
    }
    filter_changepoints = (
        True if filter_changepoints == "true" else False  # pylint: disable = R1719
    )
    OptionMap.set_map(option_arguments)
    result = runTest.run()
    if result is None:
        return {"Error":"No UUID with given metadata"}
    if filter_changepoints:
        for key, value in result.items():
            result[key] = list(filter(lambda x: x.get("is_changepoint", False), value))
    return result


@app.get("/daemon/options")
async def get_options():
    """Lists all the tests available in daemon mode

    Raises:
        HTTPException: Config not found
        HTTPException: cannot find files for config

    Returns:
        config: list of files
    """
    config_dir = pkg_resources.resource_filename("configs", "")
    if not os.path.isdir(config_dir):
        raise HTTPException(status_code=404, detail="Config directory not found")
    try:
        files = [
            os.path.splitext(file)[0]
            for file in os.listdir(config_dir)
            if file != "__init__.py"
            and not file.endswith(".pyc")
            and file != "__pycache__"
        ]
        return {"options": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@app.get("/daemon/anomaly")
async def daemon_anomaly( # pylint: disable = R0913
    version: str = "4.17",
    uuid: str = "",
    baseline: str = "",
    filter_points="",
    test_name="small-scale-cluster-density",
    anomaly_window=5,
    min_anomaly_percent=10
):
    """starts listening on port 8000 on url /daemon

    Args:
        file (UploadFile, optional): config file for the test. Defaults to File(...).

    Returns:
        json: json object of the changepoints and metrics
    """
    parameters = {"version": version}
    config_file_name=test_name+".yml"
    option_arguments = {
        "config": config_file_name,
        "output_path": "output.csv",
        "hunter_analyze": False,
        "anomaly_detection": True,
        "output_format": "json",
        "uuid": uuid,
        "baseline": baseline,
        "configMap": render_template(config_file_name, parameters),
        "anomaly_window": int(anomaly_window),
        "min_anomaly_percent":int(min_anomaly_percent)
    }
    filter_points = (
        True if filter_points == "true" else False  # pylint: disable = R1719
    )
    OptionMap.set_map(option_arguments)
    result = runTest.run()
    if result is None:
        return {"Error":"No UUID with given metadata"}
    if filter_points:
        for key, value in result.items():
            result[key] = list(filter(lambda x: x.get("is_changepoint", False), value))
    return result


def render_template(test_name, parameters):
    """replace parameters in the config file

    Args:
        file_name (str): the config file
        parameters (dict): parameters to be replaces

    Returns:
        dict: configMap in dict
    """
    config_path = pkg_resources.resource_filename("configs", test_name)
    with open(config_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()
    template = Template(template_content)
    rendered_config_yaml = template.render(parameters)
    rendered_config = yaml.safe_load(rendered_config_yaml)
    return rendered_config
