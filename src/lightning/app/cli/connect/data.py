# Copyright The Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

import click
import rich
from lightning_cloud.openapi import Create, V1AwsDataConnection
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

from lightning.app.utilities.app_helpers import Logger
from lightning.app.utilities.cli_helpers import _error_and_exit
from lightning.app.utilities.cloud import _get_project
from lightning.app.utilities.network import LightningClient

logger = Logger(__name__)


@click.argument("name", required=True)
@click.argument("region", required=True)
@click.argument("source", required=True)
@click.argument("secret_arn_name", required=False)
@click.argument("destination", required=False)
@click.argument("project_name", required=False)
def connect_data(
    name: str,
    region: str,
    source: str,
    secret_arn_name: str = "",
    destination: str = "",
    project_name: str = "",
) -> None:
    """Create a new data connection."""

    if sys.platform == "win32":
        _error_and_exit("Data connection isn't supported on windows. Open an issue on Github.")

    with Live(Spinner("point", text=Text("pending...", style="white")), transient=True) as live:

        live.stop()

        client = LightningClient()
        projects = client.projects_service_list_memberships()

        project_id = None

        for project in projects.memberships:

            if project.name == project_name:
                project_id = project.project_id
                break

        if project_id is None:
            project_id = _get_project(client).project_id

        if not source.startswith("s3://"):
            return _error_and_exit(
                "Only public S3 folders are supported for now. Please, open a Github issue with your use case."
            )

        try:
            client.data_connection_service_create_data_connection(
                body=Create(
                    name=name,
                    aws=V1AwsDataConnection(
                        region=region,
                        source=source,
                        destination=destination,
                        secret_arn_name=secret_arn_name,
                    ),
                ),
                project_id=project_id,
            )

            # Note: Expose through lightning show data {DATA_NAME}
            # response = client.data_connection_service_list_data_connection_artifacts(
            #     project_id=project_id,
            #     id=response.id,
            # )
        except Exception:
            _error_and_exit("The data connection creation failed.")

    rich.print(f"[green]Succeeded[/green]: You have created a new data connection {name}.")
