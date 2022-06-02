sudo apt update
sudo apt --yes upgrade
sudo apt install gparted
sudo apt install vim
sudo apt install net-tools
sudo apt install openssh-server

#Install latest git
sudo add-apt-repository ppa:git-core/ppa
sudo apt update
sudo apt install git


# Install gcm
# https://github.com/GitCredentialManager/git-credential-manager/releases
sudo wget https://github.com/GitCredentialManager/git-credential-manager/releases/download/v2.0.696/gcmcore-linux_amd64.2.0.696.deb /tmp/gcmcore.deb
sudo dpkg -i /tmp/gcmcore.deb

#Configure Git cache
git config --global credential.helper manager-core
git config --global credential.credentialStore plaintext
git-credential-manager-core configure
git config --global core.editor "vim"

cp .vimrc ~/
cp -r .vim ~/
cp .bashrc ~/
cp .tmux.conf ~/
cp -r .tmux ~/
