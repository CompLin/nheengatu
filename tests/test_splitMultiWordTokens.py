#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: October 4, 2025

import json
import os
import pytest
import Yauti

# Get the directory where this test file is located
HERE = os.path.dirname(__file__)

# Build the absolute path to tokenization.json
json_path = os.path.join(HERE, "tokenization.json")

# Load test data from tokenization.json
with open(json_path, encoding="utf-8") as f:
    data = json.load(f)["data"]

@pytest.mark.parametrize("entry", data, ids=[d["sent_id"] for d in data])
def test_splitMultiWordTokens(entry):
    """Test Yauti.splitMultiWordTokens using known sentences."""
    tokens = entry["tokens"]
    expected = entry["newtokens"]
    result = Yauti.splitMultiWordTokens(tokens)
    assert result == expected, (
        f"Mismatch for {entry['sent_id']}:\n"
        f"Expected: {expected}\nGot:      {result}"
    )
