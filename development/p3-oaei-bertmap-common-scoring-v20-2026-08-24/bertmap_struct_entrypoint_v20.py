#!/usr/bin/env python3
"""Outcome-blind structural-reasoner entrypoint for the frozen P3 V20 run."""

import json

import click

from deeponto.align.bertmap import BERTMapPipeline
from deeponto.onto import Ontology


OWL_THING = "http://www.w3.org/2002/07/owl#Thing"


def bind_matcher_surface(onto: Ontology, expected: list[str], role: str) -> None:
    expected_set = set(expected)
    raw_set = set(str(value) for value in onto.owl_classes)
    if raw_set != expected_set | {OWL_THING} or len(raw_set) != len(expected_set) + 1:
        raise RuntimeError(f"{role} raw class surface is not frozen universe plus exactly owl:Thing")
    removed = onto.owl_classes.pop(OWL_THING, None)
    if removed is None or set(str(value) for value in onto.owl_classes) != expected_set:
        raise RuntimeError(f"{role} outcome-blind built-in class filter failed")
    print(f"ORION_P3_V20_CLASS_SURFACE_BOUND={role}:37_TO_36:OWL_THING_ONLY", flush=True)


@click.command()
@click.option("-s", "--src_onto_file", type=click.Path(exists=True), required=True)
@click.option("-t", "--tgt_onto_file", type=click.Path(exists=True), required=True)
@click.option("-c", "--config_file", type=click.Path(exists=True), required=True)
@click.option("-u", "--universe_file", type=click.Path(exists=True), required=True)
def run_bertmap(src_onto_file: str, tgt_onto_file: str, config_file: str, universe_file: str) -> None:
    universe = json.loads(open(universe_file, encoding="utf-8").read())
    config = BERTMapPipeline.load_bertmap_config(config_file)
    config.global_matching.enabled = True
    config.bert.resume_training = None
    src_onto = Ontology(src_onto_file, reasoner_type="struct")
    tgt_onto = Ontology(tgt_onto_file, reasoner_type="struct")
    bind_matcher_surface(src_onto, universe["expected_source_iris"], "source")
    bind_matcher_surface(tgt_onto, universe["expected_target_iris"], "target")
    BERTMapPipeline(src_onto, tgt_onto, config)


if __name__ == "__main__":
    run_bertmap()
