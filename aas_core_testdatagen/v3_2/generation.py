"""Generate the test data assuming the logic based on pillars of the meta-model V3.2."""

import collections
from typing import Final, Iterator, Sequence, Callable

from aas_core_codegen import intermediate
from aas_core_codegen.common import Identifier
from typing_extensions import override

from aas_core_testdatagen import generation, verification, casing, preseria


class InstanceGenerator(generation.InstanceGenerator):
    """Generate instances specific for the meta-model V3.2."""

    # NOTE (mristin):
    # So far, we have not found any constraints which we had to
    # account for in V3.2.


class CaseGenerator(generation.CaseGenerator):
    """Generate the test cases specific for the meta-model V3.2."""

    instance_generator: Final[InstanceGenerator]

    @override
    @property
    def symbol_table(self) -> intermediate.SymbolTable:
        """Give the symbol table of the meta-model."""
        return self.instance_generator.symbol_table

    @property
    def verificator(self) -> verification.Verificator:
        """Verificator of the meta-model."""
        return self.instance_generator.verificator

    def __init__(self, instance_generator: InstanceGenerator) -> None:
        self.instance_generator = instance_generator

        min_max_case_registry = generation.build_min_max_case_registry(
            instance_generator
        )

        self._sub_generators = [
            generation.CaseGeneratorForSchemaConstraints(
                instance_generator=instance_generator,
                min_max_case_registry=min_max_case_registry,
            ),
            generation.CaseGeneratorForStableSemantics(
                instance_generator=instance_generator,
                min_max_case_registry=min_max_case_registry,
            ),
        ]

    def _generate_list_id_short_in_value(self) -> Iterator[casing.CasePositiveManual]:
        item = preseria.Instance(
            class_name=Identifier("Property"),
            properties=collections.OrderedDict(
                [
                    (Identifier("ID_short"), "something"),
                    (Identifier("value_type"), "xs:boolean"),
                ]
            ),
        )

        instance = preseria.Instance(
            class_name=Identifier("Submodel_element_list"),
            properties=collections.OrderedDict(
                [
                    (Identifier("value_type_list_element"), "xs:boolean"),
                    (Identifier("type_value_list_element"), "Property"),
                    (Identifier("ID_short"), "someList"),
                    (Identifier("value"), preseria.ListOfInstances(values=[item])),
                ]
            ),
        )

        yield casing.CasePositiveManual(
            instance=self.verificator.must(instance),
            name=generation.test_name_from_function_name(),
        )

    def generate(self) -> Iterator[casing.CaseUnion]:
        """Generate the cases."""
        for sub_generator in self._sub_generators:
            yield from sub_generator.generate()

        bound_generate_methods: Sequence[Callable[[], Iterator[casing.CaseUnion]]] = [
            self._generate_list_id_short_in_value
        ]

        for bound_generate_method in bound_generate_methods:
            try:
                yield from bound_generate_method()
            except Exception as exception:
                what = generation.human_readable_generate_phrase_from_function_name(
                    bound_generate_method.__name__
                )
                raise AssertionError(f"Failed to {what}") from exception


generation.assert_all_generate_methods_listed_in_generate_bound_generate_methods(
    cls=CaseGenerator
)
