import torch
from transformers import pipeline, AutoModelForCausalLM

class koalpaca() :
  def __init__(self) :
    MODEL = "beomi/KoAlpaca-Polyglot-5.8B"

    self._model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    device_map="auto",
    load_in_8bit=True,
    revision="8bit",
    # max_memory=f'{int(torch.cuda.mem_get_info()[0]/1024**3)-2}GB'
    )

    self._pipe = pipeline(
    "text-generation",
    model=self._model,
    tokenizer=MODEL,
    # device=2,
    )

  def ask(self, x, context='', is_input_full=False):
      ans = self._pipe(
          f"### 질문: {x}\n\n### 맥락: {context}\n\n### 답변:" if context else f"### 질문: {x}\n\n### 답변:",
          do_sample=True,
          max_new_tokens=512,
          temperature=0.7,
          top_p=0.9,
          return_full_text=False,
          eos_token_id=2,
      )

      msg = ans[0]['generated_text']

      return msg
