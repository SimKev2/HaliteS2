# -------------------
# Constants
# -------------------
FILE=replays-20170930-sample.zip
HALITE_BINARY_ADDRESS=https://halite.io/assets/downloads/Halite2_MacOS.zip
SEED=15485863
SOURCES_FOR_TRAINING= tsmlstarterbot/common.py \
	tsmlstarterbot/neural_net.py tsmlstarterbot/parsing.py \
	tsmlstarterbot/train.py

# -------------------
# Targets
# -------------------
.PHONY: default
default: model_long_training

.PHONY: deps
deps:
	pip install -r requirements.txt


.PHONY: model_long_training 
model_long_training: models/model_long_training.ckpt.meta

models/model_long_training.ckpt.meta: data/${FILE} ${SOURCES_FOR_TRAINING}
	mkdir -p models/
	python -m tsmlstarterbot.train --model_name model_long_training --data data/${FILE} --games_limit 1000 --steps 5000 --seed ${SEED}


.PHONY: model_short_training 
model_short_training: models/model_short_training.ckpt.meta

models/model_short_training.ckpt.meta: data/${FILE} ${SOURCES_FOR_TRAINING}
	mkdir -p models/
	python -m tsmlstarterbot.train --model_name model_short_training --data data/${FILE} --games_limit 100 --steps 500 --seed ${SEED}


.PHONY: clean_model
clean_model:
	rm -rf models

.PHONY: clean_data
clean_data:
	rm -rf data

.PHONY: real_clean
real_clean: clean_model clean_data
	rm -f submission.zip
	rm -f bin/halite


.PHONY: data
data: data/${FILE}

data/${FILE}:
	mkdir -p data
	curl https://storage.googleapis.com/ml-bot-data/${FILE} -o data/${FILE}

bin/halite:
	curl $(HALITE_BINARY_ADDRESS) -o halite_binary.zip
	unzip halite_binary.zip -d bin
	rm -rf halite_binary.zip


.PHONY: compare
compare: bin/compare.sh MyBotShortTraining.py MyBot.py model_short_training model_long_training bin/halite
	bin/compare.sh MyBotShortTraining.py MyBot.py


.PHONY: submission
submission: 
	zip -r submission.zip MyBot.py LANGUAGE hlt/ tsmlstarterbot/ models/

.PHONY: submit
submit: submission
	python ./HaliteClient/hlt_client/client.py bot -b ./submission.zip

