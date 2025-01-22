
 

import time

import torch

from transformers import AutoTokenizer, AutoModelForTokenClassification, BertTokenizer, BertForMaskedLM

import numpy as np

import json

 

def detect_and_correct_errors(text):

    # ここに先ほどの誤り検出と補完のコードを追加します

    # 例:

    # completed_text = ...

    # errors = ...

    # return completed_text, errors

    pass

 

# リクルートの誤字脱字検出モデルのロード

typo_model_name = 'recruit-jp/japanese-typo-detector-roberta-base'

typo_tokenizer = AutoTokenizer.from_pretrained(typo_model_name)

typo_model = AutoModelForTokenClassification.from_pretrained(typo_model_name)

 

# 東北大学の日本語BERTモデルのロード

bert_tokenizer = BertTokenizer.from_pretrained('cl-tohoku/bert-base-japanese')

bert_model = BertForMaskedLM.from_pretrained('cl-tohoku/bert-base-japanese')

 

# デバイスの設定

device = "cuda:0" if torch.cuda.is_available() else "cpu"

typo_model = typo_model.to(device)

bert_model = bert_model.to(device)

 

# 入力テキスト

text = "今日はまめが降るので傘を持っていきます。"

 

# 誤り情報を保存するリスト

all_errors = []

 

start_time = time.time()  # 実行時間の測定開始

 

while True:

    # 誤字脱字の検出

    inputs = typo_tokenizer(text, return_tensors='pt').to(device)

    outputs = typo_model(**inputs)

    logits = outputs.logits

 

    # 誤り部分を処理

    tokens = typo_tokenizer.tokenize(text)

    masked_text = tokens.copy()

    errors = []

    for i, logit in enumerate(logits.squeeze().tolist()[1:-1]):

        err_type_ind = np.argmax(logit)

        if err_type_ind == 2 or err_type_ind == 3:  # insertion_a または insertion_b の場合

            errors.append({

                "position": i,

                "character": tokens[i],

                "error_type": typo_model.config.id2label[err_type_ind]

            })

            masked_text[i] = ''  # 誤りの文字を削除

        elif err_type_ind > 0:  # その他の誤りの場合

            masked_text[i] = '[MASK]'

            errors.append({

                "position": i,

                "character": tokens[i],

                "error_type": typo_model.config.id2label[err_type_ind]

            })

 

    masked_text_str = typo_tokenizer.convert_tokens_to_string(masked_text)

    print(f"Masked Text: {masked_text_str}")

 

    # 誤り情報をリストに追加

    all_errors.extend(errors)

 

    # 誤りが検出されなくなったらループを終了

    if not errors:

        break

 

    # マスクされたテキストをBERTモデルで補完

    inputs = bert_tokenizer(masked_text_str, return_tensors='pt').to(device)

    outputs = bert_model(**inputs)

    predictions = outputs.logits

 

    # 最も可能性の高いトークンを取得して補完

    masked_indices = [i for i, token in enumerate(masked_text) if token == '[MASK]']

    for i in masked_indices:

        predicted_index = predictions[0, i].argmax().item()

        predicted_token = bert_tokenizer.convert_ids_to_tokens(predicted_index)

        masked_text[i] = predicted_token

 

    text = bert_tokenizer.convert_tokens_to_string(masked_text)

    print(f"Completed Text: {text}")

 

end_time = time.time()  # 実行時間の測定終了

execution_time = end_time - start_time

print(f"Execution Time: {execution_time} seconds")

 

# 誤り情報をファイルに保存

with open('errors.json', 'w', encoding='utf-8') as f:

    json.dump(all_errors, f, ensure_ascii=False, indent=4)

 

print(f"Final Completed Text: {text}")
