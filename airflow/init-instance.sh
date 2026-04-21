echo ""
echo "Actualizo apt"
echo ""
sudo apt update
echo ""
echo "Instalo pip"
echo ""
sudo apt install python3-pip -y
echo ""
echo "Instalo venv"
echo ""
sudo apt install python3-venv
echo ""
echo "Instalo git"
echo ""
sudo apt install git
echo ""
echo "Clono el repositorio"
echo ""
git clone https://github.com/pmdiaz/adTech.git
echo ""
echo "Done."
echo ""
cd adTech