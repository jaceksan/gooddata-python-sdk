# (C) 2022 GoodData Corporation
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from gooddata_metadata_client.model.declarative_table import DeclarativeTable
from gooddata_sdk.catalog.data_source.declarative_model.physical_model.column import CatalogDeclarativeColumn
from gooddata_sdk.catalog.entity import CatalogTypeEntity
from gooddata_sdk.utils import read_layout_from_file, write_layout_to_file


class CatalogDeclarativeTable(CatalogTypeEntity):
    def __init__(
        self,
        id: str,
        type: str,
        path: list[str],
        name_prefix: Optional[str],
        columns: list[CatalogDeclarativeColumn],
    ):
        super(CatalogDeclarativeTable, self).__init__(id, type)
        self.path = path
        self.name_prefix = name_prefix
        self.columns = columns

    @classmethod
    def from_api(cls, entity: dict[str, Any]) -> CatalogDeclarativeTable:
        columns = [CatalogDeclarativeColumn.from_api(v) for v in entity["columns"]]
        return cls(
            id=entity["id"],
            type=entity["type"],
            path=entity["path"],
            name_prefix=entity.get("name_prefix"),
            columns=columns,
        )

    def to_api(self) -> DeclarativeTable:
        columns = [v.to_api() for v in self.columns]
        kwargs = dict()
        if self.name_prefix is not None:
            kwargs["name_prefix"] = self.name_prefix
        return DeclarativeTable(id=self.id, type=self.type, path=self.path, columns=columns, **kwargs)

    def store_to_disk(self, pdm_folder: Path) -> None:
        table_dict = self.to_api().to_dict(camel_case=True)
        table_file_path = pdm_folder / f"{self.id}.yaml"
        write_layout_to_file(table_file_path, table_dict)

    @classmethod
    def load_from_disk(cls, table_file_path: Path) -> CatalogDeclarativeTable:
        table_data = read_layout_from_file(table_file_path)
        return CatalogDeclarativeTable.from_dict(table_data)

    @classmethod
    def from_dict(cls, data: dict[str, Any], camel_case: bool = True) -> CatalogDeclarativeTable:
        """
        :param data:    Data loaded for example from the file.
        :param camel_case:  True if the variable names in the input
                        data are serialized names as specified in the OpenAPI document.
                        False if the variables names in the input data are python
                        variable names in PEP-8 snake case.
        :return:    CatalogDeclarativeTable object.
        """
        declarative_table = DeclarativeTable.from_dict(data, camel_case)
        return cls.from_api(declarative_table)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CatalogDeclarativeTable):
            return False
        return (
            self.id == other.id
            and self.type == other.type
            and self.path == other.path
            and self.columns == other.columns
        )
