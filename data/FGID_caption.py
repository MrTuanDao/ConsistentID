'''
Official implementation of FGID data (facial caption) production script
Author: Jiehui Huang
Hugging Face Demo: https://huggingface.co/spaces/JackAILab/ConsistentID
Project: https://ssugarwh.github.io/consistentid.github.io/
'''

import os
import json
import sys
sys.path.append("./Llava1.5/LLaVA")
# cd ConsistentID/models/LLaVA1.5
# git clone https://github.com/haotian-liu/LLaVA.git

from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path
from llava.eval.run_llava import eval_model
from tqdm import tqdm

model_path = "liuhaotian/llava-v1.5-7b" 
prompt1 = "Please describe the people in the image, including their gender, \
        age, clothing, facial expressions, and any other distinguishing features." ### item["vqa_llva"]
prompt2 = "Describe this person's facial features for me, including \
        face, ears, eyes, nose, and mouth." ### item["vqa_llva_more_face_detail"]

### Prompt generated by LLVA1.5 to capture caption
image_file = "./demo_IMG.jpg"

tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path=model_path,
    model_base=None,
    model_name=get_model_name_from_path(model_path),
    load_4bit=True # Save GPU memory
) # device="cuda" default

def process_caption(image_folder=None, json_folder=None):

    total_files = sum(len(files) for _, _, files in os.walk(image_folder))

    for root, dirs, files in os.walk(image_folder):
        for image_file in tqdm(files, total=total_files, desc="Processing Files"):
            if image_file.endswith(('.jpg', '.jpeg', '.png')):

                image_path = os.path.join(root, image_file)

                args = type('Args', (), {
                    "model_path": model_path,
                    "model_base": None,
                    "model_name": get_model_name_from_path(model_path),
                    "query": prompt1,
                    "conv_mode": None,
                    "image_file": image_path,  ### Loop through different files
                    "sep": ",",
                    "temperature": 0,
                    "top_p": None,
                    "num_beams": 1,
                    "max_new_tokens": 512
                })()

                generated_text_vqa1 = eval_model(args, tokenizer, model, image_processor) 
                image_id = os.path.splitext(image_file)[0]
                relative_path = os.path.relpath(root, image_folder)

                args = type('Args', (), {
                    "model_path": model_path,
                    "model_base": None,
                    "model_name": get_model_name_from_path(model_path),
                    "query": prompt2,
                    "conv_mode": None,
                    "image_file": image_path,  ### Loop through different files
                    "sep": ",",
                    "temperature": 0,
                    "top_p": None,
                    "num_beams": 1,
                    "max_new_tokens": 512
                })()

                generated_text_vqa2 = eval_model(args, tokenizer, model,image_processor)  

                ### Build JSON data
                json_file_path = os.path.join(json_folder, relative_path, image_id + '.json')
                data1 = {"vqa_llva": generated_text_vqa1}
                data2 = {"vqa_llva_face_caption": generated_text_vqa2}

                with open(json_file_path, 'r') as f:
                    data = json.load(f)
                    if "vqa_llva" in data:
                        print("The key vqa_llva exists in the JSON file.")
                        continue
                    else:
                        print("Key vqa_llva does not exist in the JSON file.")
                
                ### To update the corresponding JSON file, you need to first run the FGID_mask.py file
                with open(json_file_path, 'r+') as json_file:
                    data1 = json.load(json_file)
                    data1['vqa_llva'] = generated_text_vqa1
                    json_file.seek(0) 
                    json.dump(data1, json_file)
                    json_file.truncate()
                with open(json_file_path, 'r+') as json_file:
                    data2 = json.load(json_file)
                    data2['vqa_llva_more_face_detail'] = generated_text_vqa2
                    json_file.seek(0) 
                    json.dump(data2, json_file)
                    json_file.truncate()

                print(f"Processed {image_file}, JSON file saved at: {json_file_path}")


if __name__ == "__main__":
    
    ### Specify folder path
    origin_img_path = "./FGID_Origin" # read_path for customized IMGs
    json_save_path = "./FGID_JSON" # save_path for fine_caption information

    process_caption(image_folder=origin_img_path, json_folder=json_save_path)



'''
Additional instructions:

(1) Specify folder path, then CUDA_VISIBLE_DEVICES=0 python ./FGID_caption.py

(2) Note: Run FGID_mask.py first, and then FGID_caption.py to ensure that the json data is created smoothly.

(3) JSON data should be constructed as follows:
{
"origin_IMG": "15/0062963.png", 
"resize_IMG": "15/0062963_resize.png", 
"parsing_color_IMG": "15/0062963_color.png", 
"parsing_mask_IMG": "15/0062963_mask.png"
"vqa_llva": "The image features a young woman with short hair, wearing a black shirt and a black jacket. 
            She has a smiling expression on her face, and her eyes are open. The woman appears to be the main subject of the photo.",
"vqa_llva_face_caption": "The person in the image has a short haircut, which gives her a modern and stylish appearance. 
            She has a small nose, which is a prominent feature of her face. Her eyes are large and wide-set, adding to her striking facial features. 
            The woman has a thin mouth and a small chin, which further accentuates her overall look. Her ears are small and subtle, blending in with her hairstyle."
}

'''
















