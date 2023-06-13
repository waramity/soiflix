cd /etc/nginx/site-available
cd /etc/nginx/sites-available
ls
sudo rm -rf soiflix.bak
sudo cp /etc/nginx/sites-available/soiflix /etc/nginx/sites-available/soiflix.bak
sudo vi /etc/nginx/sites-available/soiflix
sudo ufw app list
sudo ufw status
sudo ufw allow 'Nginx Full'
sudo ufw delete allow 'Nginx HTTP'
sudo ufw status
sudo nginx -t
sudo systemctl restart nginx
sudo nano /etc/nginx/sites-available/soiflix
sudo vi /etc/nginx/sites-available/soiflix
sudo nginx -t
sudo systemctl restart nginx
sudo ufw delete allow 'Nginx HTTP'
systemctl restart soiflix
ls
cd soiflix
ls
vi run.py
source soiflixenv/bin/activate
python run.py
python3 run.py
vi run.py
python3 run.py
vi run.py
python3 run.py
vi run.py
python3 run.py
vi run.py
python3 run.py
vi run.py

vi run.py
python3 run.py
systemctl restart soiflix
cd ~/.ssh
ls
vim authorized_keys
cd ~/.ssh
ls
vi authorized_keys
systemctl restart soiflix
journalctl soiflix
journalctl -u soiflix
systemctl restart soiflix
