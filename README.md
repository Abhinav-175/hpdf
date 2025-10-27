# hpdf
Highlight pdf documents and papers.

### Install

Install and use easily with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/Abhinav-175/hpdf.git
hpdf test.pdf
```

**hpdf** is a not so smart plumbing between Pymupdf and GEMINI api calls.
Works by extracting text from the docment and ignoring images.
So, does'nt work on rasterized pdf documents.

Bring your own keys approach.

```bash
export GEMINI_API_KEY="0000...000"
```

Notes:
- No safety checks on the size of the document, be mindful.
- The behaviour around password protected documents falls on Pymupdf's defaults.
- The "smartness" or the lack there of is inherited from GEMINI.

### License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.html)
