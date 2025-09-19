#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: September 19, 2025
import pytest
from Yauti import remove_tags

@pytest.mark.parametrize("input_str,expected", [
    (
        "Sumura-etá/=typo:c|Sumuára-etá:x|ncont uikú/cop suakí, usendú aé/pron, upurandú yeperesé maã/int marandua aé/pron umaã.",
        "Sumura-etá uikú suakí, usendú aé, upurandú yeperesé maã marandua aé umaã."
    ),
    (
        "Kũi aé/pron wana resikari na/=spl:w|a:c|ateíma:x|v2:b|ne teíma/=x reté/advs.",
        "Kũi aé wana resikari na teíma reté."
    ),
    (
        "Kwá/demx kunhamukú/n awa-etá i/pron2 pixuna/@, paá, uwerá-werá katú/advs paraná waruá yawé/adp.",
        "Kwá kunhamukú awa-etá i pixuna, paá, uwerá-werá katú paraná waruá yawé."
    ),
    (
        "Pe/pron2 ruakí, yara/n Tupã/=p, nẽ/neg maã/ind@ yaikú/cop.",
        "Pe ruakí, yara Tupã, nẽ maã yaikú."
    ),
    (
        "Xayasuka-putari/=mid ne igarupá pupé.",
        "Xayasuka-putari ne igarupá pupé."
    ),
    (
        "Ixé se yuwá sasí/v3 ikú/=mf:m|uikú:x|v:h|v, intí xakwáu sa uyupuruka/=mid uikú/v.",
        "Ixé se yuwá sasí ikú, intí xakwáu sa uyupuruka uikú."
    ),
    (
        "Yepé/art maãpuxí/=spl:w|puxí:h|n:x|a uyukwáu ixéu kaá-pe/n aasuí/advt akanhemu/=typo:c|ukanhemu, intí xakwáu marupí/advrc usú.",
        "Yepé maãpuxí uyukwáu ixéu kaá-pe aasuí akanhemu, intí xakwáu marupí usú."
    ),
    (
        'Rerikú será urusakã purã ne "vizinho"/=n:o|pt suí/adp?',
        'Rerikú será urusakã purã ne "vizinho" suí?'
    ),
    (
        "― Awá/int taá umunhã upaĩ maã/n?",
        "― Awá taá umunhã upaĩ maã?"
    ),
    (
        "― Tiana/=spl:w|ana!",
        "― Tiana!"
    ),
    (
        "Tupana resé/adp, tenhẽ/negi iné se/=mf:m|ixé yuká/=mf:m|reyuká!",
        "Tupana resé, tenhẽ iné se yuká!"
    ),
])
def test_remove_tags(input_str, expected):
    assert remove_tags(input_str) == expected
