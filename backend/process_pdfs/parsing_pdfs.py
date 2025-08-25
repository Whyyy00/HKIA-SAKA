import os

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

# args
pdf_file_name = "data/manual/decrpted_manual/EPM/08. EPM Part 4A - Fuel Spillage from Aircraft_Issue 01-24.pdf"
name_without_suff = os.path.splitext(os.path.basename(pdf_file_name))[0]

# prepare env
local_image_dir = "data/extracted/EPM/images"
local_md_dir = "data/extracted/EPM/markdown"
# local_middle_dir = "data/extracted/middle"
image_dir = str(os.path.basename(local_image_dir))  # "images"

# Make sure dir exist
os.makedirs(local_image_dir, exist_ok=True)
os.makedirs(local_md_dir, exist_ok=True)
# os.makedirs(local_middle_dir, exist_ok=True)

# create writer
image_writer = FileBasedDataWriter(local_image_dir)
md_writer = FileBasedDataWriter(local_md_dir)
# middle_writer = FileBasedDataWriter(local_middle_dir)

# read bytes
reader1 = FileBasedDataReader("")
pdf_bytes = reader1.read(pdf_file_name)  # read the pdf content

# proc
## Create Dataset Instance
ds = PymuDocDataset(pdf_bytes)

## inference
if ds.classify() == SupportedPdfParseMethod.OCR:
    infer_result = ds.apply(doc_analyze, ocr=True)

    ## pipeline
    pipe_result = infer_result.pipe_ocr_mode(image_writer)

else:
    infer_result = ds.apply(doc_analyze, ocr=False)

    ## pipeline
    pipe_result = infer_result.pipe_txt_mode(image_writer)

# ### draw model result on each page
# infer_result.draw_model(os.path.join(local_middle_dir, f"{name_without_suff}_model.pdf"))

# ### get model inference result
# model_inference_result = infer_result.get_infer_res()

# ### draw layout result on each page
# pipe_result.draw_layout(os.path.join(local_middle_dir, f"{name_without_suff}_layout.pdf"))

# ### draw spans result on each page
# pipe_result.draw_span(os.path.join(local_middle_dir, f"{name_without_suff}_spans.pdf"))

### get markdown content
md_content = pipe_result.get_markdown("../images")

### dump markdown
pipe_result.dump_md(md_writer, f"{name_without_suff}.md", "../images")

# ### get content list content
# content_list_content = pipe_result.get_content_list(image_dir)

# ### dump content list
# pipe_result.dump_content_list(middle_writer, f"{name_without_suff}_content_list.json", image_dir)

# ### get middle json
# middle_json_content = pipe_result.get_middle_json()

# ### dump middle json
# pipe_result.dump_middle_json(middle_writer, f'{name_without_suff}_middle.json')