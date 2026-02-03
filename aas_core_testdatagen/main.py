"""Generate test data for AAS elements based on the meta-model."""

import argparse
import itertools
import pathlib
import sys
from typing import TextIO

import aas_core_codegen.infer_for_schema
import aas_core_codegen.run

import aas_core_testdatagen
from aas_core_testdatagen import generation, verification, jsoning, xmling
from aas_core_testdatagen.common import bullet_points
from aas_core_testdatagen.v3_1 import generation as v3_1_generation

assert aas_core_testdatagen.__doc__ == __doc__


def execute(
    model_path: pathlib.Path, output_dir: pathlib.Path, stdout: TextIO, stderr: TextIO
) -> int:
    """
    Execute the test case generation.

    Return the exit code.
    """
    if not model_path.exists():
        print(f"The --model_path does not exist: {model_path}", file=stderr)
        return 1

    if not model_path.is_file():
        print(f"The --model_path is not a file: {model_path}", file=stderr)
        return 1

    symbol_table_atok, error = aas_core_codegen.run.load_model(model_path)
    if error is not None:
        print("The --model_path could not be parsed: {error}", file=stderr)
        return 1

    assert symbol_table_atok is not None
    symbol_table, _ = symbol_table_atok

    constraints_by_class, inference_errors = (
        aas_core_codegen.infer_for_schema.infer_constraints_by_class(
            symbol_table=symbol_table
        )
    )
    if inference_errors is not None:
        errors_str = bullet_points(map(repr, inference_errors))
        print(
            f"Failed to infer the schema constraints from --model_path:\n{errors_str}",
            file=stderr,
        )
        return 1

    assert constraints_by_class is not None
    reorganized_constraints_by_class = (
        verification.reorganize_schema_constraints_by_properties(
            constraints_by_class=constraints_by_class
        )
    )

    verificator = verification.Verificator(
        symbol_table=symbol_table, constraints_by_class=reorganized_constraints_by_class
    )

    case_generator: generation.CaseGenerator

    if symbol_table.meta_model.version == "V3.1":
        case_generator = v3_1_generation.CaseGenerator(
            instance_generator=v3_1_generation.InstanceGenerator(
                verificator=verificator
            )
        )
    else:
        print(
            f"Unhandled meta-model version in --model_path: "
            f"{symbol_table.meta_model.version}",
            file=stderr,
        )
        return 1

    for output in itertools.chain(
        jsoning.generate_test_data(case_generator),
        xmling.generate_test_data(case_generator),
    ):
        path = output_dir / output.relative_path

        path.parent.mkdir(exist_ok=True, parents=True)

        with path.open("wt", encoding="utf-8") as fid:
            fid.write(output.text)
            fid.write("\n")

        print(f"Written to: {path}", file=stdout)

    return 0


def main(prog: str) -> int:
    """
    Execute the main routine.

    :param prog: name of the program to be displayed in the help
    :return: exit code
    """
    parser = argparse.ArgumentParser(prog=prog, description=__doc__)
    parser.add_argument(
        "--model_path", help="path to the AAS meta-model", required=True
    )
    parser.add_argument(
        "--output_dir",
        help="path to the directory where test data is stored",
        required=True,
    )
    parser.add_argument(
        "--version", help="show the current version and exit", action="store_true"
    )

    # NOTE (mristin):
    # The module ``argparse`` is not flexible enough to understand special options such
    # as ``--version`` so we manually hard-wire.
    if "--version" in sys.argv and "--help" not in sys.argv:
        print(aas_core_testdatagen.__version__)
        return 0

    args = parser.parse_args()

    model_path = pathlib.Path(args.model_path)
    output_dir = pathlib.Path(args.output_dir)

    return execute(
        model_path=model_path,
        output_dir=output_dir,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def entry_point() -> int:
    """Provide an entry point for a console script."""
    return main(prog="aas-core-testdatagen")


if __name__ == "__main__":
    sys.exit(main(prog="aas-core-testdatagen"))
