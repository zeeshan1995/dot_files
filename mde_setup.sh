ubunutVer=$(lsb_release -d | cut -f2| cut -d' ' -f 2| cut -d'.' -f 1-2)
echo $ubunutVer
sudo apt-get install curl -y
sudo apt-get install libplist-utils -y
curl -o microsoft.list https://packages.microsoft.com/config/ubuntu/$ubunutVer/prod.list
sudo mv ./microsoft.list /etc/apt/sources.list.d/microsoft-prod.list
sudo apt-get install gpg -y
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null
sudo apt-get install apt-transport-https -y
sudo apt-get update -y
sudo apt-get install -y libwebkit2gtk-4.0-37
