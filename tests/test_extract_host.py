#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Last update: October 4, 2025
import pytest
from Yauti import extract_host

@pytest.mark.parametrize("token,expected", [
    ("arawírupi", {'host': 'arawira', 'suff': 'upé', 'xpos': 'N', 'multiwordtoken': 'arawírupi'}),
    ("úkupi", {'host': 'uka', 'suff': 'upé', 'xpos': 'N', 'multiwordtoken': 'úkupi'}),
    ("rúkupi", {'host': 'ruka', 'suff': 'upé', 'xpos': 'N', 'multiwordtoken': 'rúkupi'}),
    ("súkupi", {'host': 'suka', 'suff': 'upé', 'xpos': 'N', 'multiwordtoken': 'súkupi'}),
    ("pitérupi", {'host': 'pitera', 'suff': 'upé', 'xpos': 'N', 'multiwordtoken': 'pitérupi'}),
    ("maita", {'host': 'mayé', 'suff': 'taá', 'xpos': 'ADVRA', 'multiwordtoken': 'maita'}),
    ("marã", {'host': 'maã', 'suff': 'arã', 'xpos': 'IND', 'multiwordtoken': 'marã'}),
    ("paraname", {'host': 'paranã', 'suff': 'me', 'multiwordtoken': 'paraname'}),
    ("ripí-pe", {}),
    ("uikuwera", {'host': 'uikú', 'suff': 'wera', 'multiwordtoken': 'uikuwera'}),
    ("awá-ta", {}),
    ("uruyariwera", {'host': 'uruyari', 'suff': 'wera', 'multiwordtoken': 'uruyariwera'}),
    ("Amuriwera", {'host': 'Amurí', 'suff': 'wera', 'multiwordtoken': 'Amuriwera'}),
    ("umaãwera", {'host': 'umaã', 'suff': 'wera', 'multiwordtoken': 'umaãwera'}),
    ("sauruwera", {'host': 'saurú', 'suff': 'wera', 'multiwordtoken': 'sauruwera'}),
    ("usikawera", {'host': 'usika', 'suff': 'wera', 'multiwordtoken': 'usikawera'}),
    ("xibentu", {'host': 'xibé', 'suff': 'ntu', 'multiwordtoken': 'xibentu'}),
    ("Pewapikantu", {'host': 'Pewapika', 'suff': 'ntu', 'multiwordtoken': 'Pewapikantu'}),
    ("rupitá-pe", {}),
    ("ukárupi", {'host': 'ukara', 'suff': 'upé', 'xpos': 'N', 'multiwordtoken': 'ukárupi'}),
    ("gantime", {'host': 'gantĩ', 'suff': 'me', 'multiwordtoken': 'gantime'}),
    ("ramewera", {'host': 'ramé', 'suff': 'wera', 'multiwordtoken': 'ramewera'}),
    ("Sakakwerantu", {'host': 'Sakakwera', 'suff': 'ntu', 'multiwordtoken': 'Sakakwerantu'}),
    ("suaxarawara", {'host': 'suaxara', 'suff': 'wara', 'multiwordtoken': 'suaxarawara'}),
    ("paranawara", {'host': 'paraná', 'suff': 'wara', 'multiwordtoken': 'paranawara'}),
    ("aramewara", {'host': 'aramé', 'suff': 'wara', 'multiwordtoken': 'aramewara'}),
    ("tetama-etá-wara", {'host': 'tetama-etá-', 'suff': 'wara', 'multiwordtoken': 'tetama-etá-wara'}),
    ("tumasawawara", {'host': 'tumasawa', 'suff': 'wara', 'multiwordtoken': 'tumasawawara'}),
    ("sangawa/ncont", {}),
    ("apurakí-vutari/=typo:c|putari:i|t", {}),
    ("apurakí-putari", {}),
    ("Tupayúwara", {'host': 'Tupayú', 'suff': 'wara', 'multiwordtoken': 'Tupayúwara'}),
    ("Mixukúi", {'host': 'xukúi', 'prefix': 'mi', 'multiwordtoken': 'Mixukúi'}),
    ("na/=spl:w|a:c|ateíma:x|v2:b|ne", {
        'host': {'form': 'n', 'xpos': None, 'correct': 'ne'},
        'word': {'form': 'a', 'xpos': 'v2', 'correct': 'ateíma'},
        'function': 'wm'
    }),
    ("ukupé/=spl:w|upé:b|uka:x|adp", {
        'host': {'form': 'uk', 'xpos': None, 'correct': 'uka'},
        'word': {'form': 'upé', 'xpos': 'adp', 'correct': None},
        'function': 'wm'
    }),
])
def test_extract_host(token, expected):
    result = extract_host(token)
    assert result == expected
