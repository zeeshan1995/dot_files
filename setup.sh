sudo apt update
sudo apt --yes upgrade
sudo apt install gparted -y
sudo apt install vim -y
sudo apt install net-tools -y
sudo apt install openssh-server -y
sudo apt install cifs-utils
sudo apt install fzf
sudo apt install clangd-12 -y
sudo apt install tmux -y

#Install latest git
sudo apt purge git -y
sudo add-apt-repository ppa:git-core/ppa -y
sudo apt update
sudo apt install git -y
sudo apt-get install -y libwebkit2gtk-4.0-37

#install Latest Node
curl -sL https://deb.nodesource.com/setup_17.x | sudo -E bash -
sudo apt install nodejs -y

# Install gcm
# https://github.com/GitCredentialManager/git-credential-manager/releases
sudo wget https://github.com/GitCredentialManager/git-credential-manager/releases/download/v2.0.696/gcmcore-linux_amd64.2.0.696.deb -P /tmp/
sudo dpkg -i /tmp/gcmcore-linux_amd64.2.0.696.deb

#Configure Git cache
git config --global credential.helper manager-core
git config --global credential.credentialStore plaintext
git-credential-manager-core configure
git config --global core.editor "vim"

#Set up shared folder with host machine
sudo mount.cifs //WIN-VQHN3T6VQSS/shared/ ~/shared -o=administrator

cp .vimrc ~/
cp -r .vim ~/
cp .bashrc ~/
cp .tmux.conf ~/

mkdir -p ~/.config/
cp -r clangd ~/.config/
