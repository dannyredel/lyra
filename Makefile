# Vega — reproducible by command. A run is fully defined by (config.yaml + meta.seed).
.PHONY: help install run metrics infer validate all test lint clean

CONFIG ?= config.yaml

help:
	@echo "Vega targets:"
	@echo "  install   install package + dev/dbt extras"
	@echo "  run       simulate -> emit events/ (engine)"
	@echo "  metrics   build dbt staging/intermediate/marts over the event log"
	@echo "  infer     run inference estimators"
	@echo "  validate  Criteo real-data leg"
	@echo "  all       run -> metrics -> infer"
	@echo "  test      pytest (recovery + naive-bias + A/A)"
	@echo "  lint      ruff"

install:
	python -m pip install -e ".[dev,dbt]"

run:
	python -m cli --config $(CONFIG) run

metrics:
	cd metrics && dbt build --profiles-dir .

infer:
	python -m cli --config $(CONFIG) infer

validate:
	python -m cli --config $(CONFIG) validate

all:
	python -m cli --config $(CONFIG) all

test:
	pytest

lint:
	ruff check .

clean:
	rm -rf events/day=* vega.duckdb metrics/target metrics/dbt_packages .pytest_cache
