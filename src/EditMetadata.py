#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Leonel Figueiredo de Alencar
# Function reorder_metadata created by means of ChatGPT
# Last update: August 13, 2024
import Metadata
from conllu.models import Token,TokenList
from collections import OrderedDict

def reorder_metadata(metadata):
    """
    Reorders the keys of a metadata dictionary according to a specified order:
    - sent_id, text, text_eng, text_por, text_source, [any other attributes], text_orig, text_annotator

    Args:
        metadata (dict): The metadata dictionary to reorder.

    Returns:
        dict: A new dictionary with keys ordered as specified.

    Example:
        metadata = {
            'text_source': 'source_example',
            'text_orig': 'orig_example',
            'text': 'example sentence',
            'sent_id': '1',
            'text_eng': 'example sentence in English',
            'text_por': 'exemplo de sentença em Português',
            'text_annotator': 'annotator_example',
            'custom_attribute': 'custom_value'
        }

        ordered_metadata = reorder_metadata(metadata)
        print(ordered_metadata)
        # Output:
        # {
        #     'sent_id': '1',
        #     'text': 'example sentence',
        #     'text_eng': 'example sentence in English',
        #     'text_eng_ggl': 'English translation by Google Translate',
        #     'text_por': 'exemplo de sentença em Português',
        #     'text_source': 'source_example',
        #     'custom_attribute': 'custom_value',
        #     'text_orig': 'orig_example',
        #     'text_annotator': 'annotator_example'
        # }
    """
    key_order = ['sent_id', 'text', 'text_eng', 'text_eng_ggl','text_por', 'text_source', 'text_orig', 'text_annotator']
    ordered_metadata = {key: metadata[key] for key in key_order if key in metadata}
    for key in metadata:
        if key not in key_order:
            ordered_metadata[key] = metadata[key]
    return ordered_metadata

def EditMetadata(sents):
	jul=Metadata.PEOPLE['jul']
	sentids=set()
	attributes=['text_adapter','text_orig_transcriber','text_por_orig_transcriber', 'text_por_transcriber']
	for sent in sents:
		sentid=sent.metadata['sent_id']
		if sentid.startswith('Casasnovas2006'):
			jlg=sent.metadata.get('text_annotator')
			if jlg == 'JLG' or jul:
				text_eng = sent.metadata.get('text_eng')
				if not text_eng:
					text_eng_ggl = sent.metadata.get('text_eng_ggl')
					if text_eng_ggl:
						#sent.metadata.pop('text_eng_ggl')
						sent.metadata['text_eng'] = 'TODO'
						sentids.add(sentid)
				text_por=sent.metadata.get('text_por')
				if not text_por:
					text_por_orig = sent.metadata.get('text_por_orig')
					if text_por_orig:
						sent.metadata['text_por']=sent.metadata.pop('text_por_orig')
						sentids.add(sentid)
				for att in attributes:
					value=sent.metadata.get(att)
					if value and value in ('JLG',jul):
						sent.metadata.pop(att)
						sentids.add(sentid)
				if sentid in sentids:
					oldlen=len(sent.metadata)
					sent.metadata=reorder_metadata(sent.metadata)
					newlen=len(sent.metadata)
					if oldlen != newlen:
						print(f"Length of {sentid}'s metadata has changed.'")
	return sentids
