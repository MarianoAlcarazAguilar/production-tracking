#! /bin/bash

sudo apt-get update
sudo apt update

# Instalamos miniconda 
# Este link puede cambiar, hay que encontrar el adecuado
# https://docs.conda.io/projects/miniconda/en/latest/
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod 777 Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh

# Instalamos tmux y creamos una sesión 
sudo apt install tmux
# Esto te va a meter a la sesión
# Para salir es Control + b y luego d
tmux new-session -s StreamSession

# Para volver a meterte a la sesión es
# tmux attach -t StreamSession
