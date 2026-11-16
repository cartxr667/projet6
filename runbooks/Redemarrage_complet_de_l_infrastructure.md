Runbook — Redémarrage complet de l'infrastructure


Contexte
Après une extinction planifiée (fin de journée, maintenance de la salle serveur), il faut relancer l'ensemble de l'infrastructure dans un ordre précis pour éviter les erreurs de connexion (les applications dépendent de la base, la base dépend du réseau, etc.).

Prérequis
Toutes les VMs éteintes proprement (voir procédure d'extinction : arrêt des apps, arrêt des bases, puis vagrant halt).

Étapes
1. Démarrer toutes les VMs (sur l'hôte Windows)
powershell
vagrant up
→ attendre que les 7 VMs soient Machine booted and ready!.

2. Démarrer PostgreSQL (sur pg1 et pg2)
bash
sudo pg_ctlcluster 16 main start
→ sur les deux machines.

3. Démarrer MariaDB et Zabbix (sur zabbix)
bash
sudo systemctl start mariadb
sudo systemctl restart zabbix-server apache2
4. Démarrer les applications Flask (sur app1 et app2)
bash
cd /opt/app
nohup /opt/app/venv/bin/python app.py > /opt/app/flask.log 2>&1 &
5. Vérifier Keepalived et HAProxy (sur lb1 et lb2)
bash
sudo systemctl restart haproxy
sudo systemctl restart keepalived
6. Vérification finale (depuis le client Windows)
powershell
curl.exe http://192.168.56.100/health
→ doit renvoyer {"status":"ok"}. L'infrastructure est opérationnelle.