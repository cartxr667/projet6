Runbook — Extinction propre de l'infrastructure


Contexte
Pour éviter la corruption des bases de données (MariaDB/PostgreSQL) et des fichiers de réplication, l'extinction doit suivre un ordre inverse au démarrage.

Prérequis
Aucun (procédure à appliquer avant toute extinction, y compris avant d'éteindre le PC hôte).

Étapes
1. Arrêter les applications Flask (sur app1 et app2)
bash
pkill -f app.py
2. Arrêter les bases de données
Sur pg1 et pg2 :

bash
sudo pg_ctlcluster 16 main stop
Sur zabbix :

bash
sudo systemctl stop mariadb
3. Arrêter les VMs proprement (sur l'hôte Windows)
Ne pas utiliser -f (force) :

powershell
vagrant halt
→ attendre la fin de l'arrêt de toutes les VMs.

