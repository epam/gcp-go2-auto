# T5 Model Serving

Stanza for model packaging and serving for T5 models.

```bash 
mkdir "models/t5-large"
gsutil -m rsync -r "gs://akranga-models/t5/t5-large-snapshot-1/" "rsync models/t5-large"
mkdir -p "model_store"
torch-model-archiver \
  --model-name "t5" \
  --version "1.0" \
  --handler "text_classifier" \
  --serialized-file "models/t5-large/pytorch_model.bin" \
  --extra-files 'models/t5-large/config.json,models/t5-large/tokenizer.json' \
  --export-path "model_store"
```
