"""
License : AGPL <https://www.gnu.org/licenses/agpl-3.0-standalone.html>
"""

import os
import pathlib
import requests
import json
import argparse
import sys
import itertools
import time
import re

import fitz


gemini_pro_sys_prompt = """\
Analyze the following document text. Identify and return only the **exact** sentences or paragraphs that represent the core thesis or most critical findings and technical details like appendix. Do not paraphrase or add any introductory text. Output atleast 25 line extracts.\n\n\
"""


def get_gemini_api_key()->str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    else:
        raise RuntimeError("Could not find Gemini api key\n export GEMINI_API_KEY='0000...000'")


def gemini_api_call(sys_prompt, pdf_text_concat):
    api_key = get_gemini_api_key()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"contents": [{"parts": [{"text": f"{sys_prompt+pdf_text_concat}"}]}]}

    print("Calling Gemini to process document....")
    response = requests.post(url, headers=headers, data=json.dumps(data))

    try:
        response_json = response.json()
        extracted_text = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
        
        if extracted_text is not None:
            return extracted_text
        else:
            print("Could not extract text from response.")
            return ""
    
    except requests.exceptions.JSONDecodeError:
        print("Error: Response is not valid JSON.")
        return ""
    except IndexError:
        print("Error: List index out of range in response.")
        return ""


def resp_split(extracted_text):
    output_strings = []
    if not extracted_text:
        return output_strings
        
    response_split = re.split(r"[^\(\)\ﬁ\,\-a-zA-Z0-9\s]+", extracted_text)
    for i in response_split:
        if len(i)>15:
            output_strings.append(i)
    
    return output_strings


def process_pdf(pdf_path):
    basename = os.path.basename(pdf_path)
    filename_stem = os.path.splitext(basename)[0]
    output_file = "./highlighted_"+filename_stem+".pdf"

    doc = fitz.open(pdf_path)
    pages = [i for i in doc]
    
    print("Processing document")
    
    all_search_terms = []
    chunk_size = 5
    
    for i in range(0, len(pages), chunk_size):
        page_chunk = pages[i:i + chunk_size]
        pages_text_chunk = []
        for page in page_chunk:
            pages_text_chunk.append(page.get_text())
        
        print(f"Processing pages {i+1} to {min(i + chunk_size, len(pages))}...")
        
        api_result = gemini_api_call(gemini_pro_sys_prompt, ''.join(pages_text_chunk))
        chunk_search_terms = resp_split(api_result)
        all_search_terms.extend(chunk_search_terms)

    search_terms = list(dict.fromkeys(all_search_terms))

    for page in pages:
        for term in search_terms:
            search_results = page.search_for(term)
            for hits in search_results:
                highlight = page.add_highlight_annot(hits)
    
    print(f"Write output to {output_file}")
    doc.save(output_file)
    doc.close()


def main()->int:
    ap = argparse.ArgumentParser(description="Highlight core concepts in a paper.\nExpectes env variable GEMINI_API_KEY:\nexport GEMINI_API_KEY='0000...000'")
    ap.add_argument("pdf_doc", type=str, help="path to pdf to be processed.")
    args = ap.parse_args()

    if not args.pdf_doc.lower().endswith(".pdf"):
        ap.error(f"file '{args.pdf_doc}' must be a .pdf document.")
    
    process_pdf(args.pdf_doc)
    return 0


if __name__ == '__main__':
    main()
