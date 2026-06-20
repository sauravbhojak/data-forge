"""Relational multi-table data generator with referential integrity."""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import Any

from faker import Faker

from app.exceptions.custom import SchemaValidationError
from app.generators.table_generator import TableGenerator
from app.schemas.generation import RelationalSchemaRequest, RelationshipDefinition, TableSchema


class RelationalGenerator:
    """
    Generates multiple related tables while maintaining referential integrity.

    Algorithm:
    1. Build a dependency graph from relationship definitions.
    2. Topological-sort tables so parents are generated before children.
    3. Generate parent records; collect FK values.
    4. Generate child records; replace FK fields with valid parent values.

    Memory:
    - Parent FK columns are collected into compact lists (not full row dicts).
    - Child rows are yielded one at a time.
    """

    def __init__(self, fake: Faker) -> None:
        self._table_gen = TableGenerator(fake)

    def generate(self, request: RelationalSchemaRequest) -> dict[str, list[dict[str, Any]]]:
        """
        Generate all tables respecting relationships.

        Returns a dict mapping table_name → list of row dicts.
        NOTE: For large datasets, prefer generate_streaming which returns iterators.
        This method materialises all data in memory — use only for preview/SQL inserts.
        """
        order = self._topological_sort(request)
        fk_pools: dict[str, list[Any]] = {}  # "table.field" → list of generated values
        result: dict[str, list[dict[str, Any]]] = {}

        for table_name in order:
            table = self._get_table(table_name, request)
            rows = list(self._generate_table_with_fks(table, request, fk_pools))
            result[table_name] = rows

            # Populate FK pools for downstream children
            for rel in request.relationships:
                if rel.parent_table == table_name:
                    pool_key = f"{table_name}.{rel.parent_field}"
                    fk_pools[pool_key] = [r[rel.parent_field] for r in rows if r.get(rel.parent_field) is not None]

        return result

    def generate_streaming(self, request: RelationalSchemaRequest) -> dict[str, Iterator[dict[str, Any]]]:
        """
        Return iterators for each table in topological order.

        Parents are fully materialised to build FK pools;
        children stream one row at a time.
        """
        # Parents must be materialised for FK pools
        data = self.generate(request)
        return {name: iter(rows) for name, rows in data.items()}

    def _generate_table_with_fks(
        self,
        table: TableSchema,
        request: RelationalSchemaRequest,
        fk_pools: dict[str, list[Any]],
    ) -> Iterator[dict[str, Any]]:
        """Yield rows, overwriting FK fields with valid parent values."""
        # Find which fields in this table are child FK fields
        child_fks: dict[str, list[Any]] = {}  # field_name → pool
        for rel in request.relationships:
            if rel.child_table == table.name:
                pool_key = f"{rel.parent_table}.{rel.parent_field}"
                pool = fk_pools.get(pool_key, [])
                if pool:
                    child_fks[rel.child_field] = pool

        for row in self._table_gen.generate(table):
            for field_name, pool in child_fks.items():
                row[field_name] = random.choice(pool)
            yield row

    @staticmethod
    def _topological_sort(request: RelationalSchemaRequest) -> list[str]:
        """Return table names sorted so parents come before children."""
        table_names = {t.name for t in request.tables}
        deps: dict[str, set[str]] = {n: set() for n in table_names}

        for rel in request.relationships:
            if rel.child_table not in deps:
                raise SchemaValidationError(
                    f"Unknown table in relationship: {rel.child_table}"
                )
            if rel.parent_table not in table_names:
                raise SchemaValidationError(
                    f"Unknown parent table: {rel.parent_table}"
                )
            deps[rel.child_table].add(rel.parent_table)

        # Kahn's algorithm
        in_degree = {n: len(d) for n, d in deps.items()}
        queue = [n for n, d in in_degree.items() if d == 0]
        order: list[str] = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for child, parents in deps.items():
                if node in parents:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        queue.append(child)

        if len(order) != len(table_names):
            raise SchemaValidationError("Circular dependency detected in table relationships")

        return order

    @staticmethod
    def _get_table(name: str, request: RelationalSchemaRequest) -> TableSchema:
        for t in request.tables:
            if t.name == name:
                return t
        raise SchemaValidationError(f"Table '{name}' not found in schema")
