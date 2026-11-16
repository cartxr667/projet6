Runbook — Bascule de l'IP Virtuelle (Keepalived : lb1 → lb2)


Contexte
lb1 (MASTER) détient l'IP virtuelle 192.168.56.100. En cas de panne de lb1 ou de maintenance planifiée, lb2 (BACKUP) doit prendre le relais pour maintenir la continuité de service.

Prérequis
lb1 et lb2 opérationnels.

Keepalived configuré (lb1 priorité 101, lb2 priorité 100).

HAProxy configuré à l'identique sur les deux machines.

Étapes
1. Vérifier l'état actuel (sur lb1)
bash
ip a | grep 192.168.56.100
→ l'IP doit apparaître sur enp0s8.

2. Simuler la panne de lb1 (sur lb1)
bash
sudo systemctl stop keepalived
3. Vérifier la bascule sur lb2 (sur lb2)
bash
ip a | grep 192.168.56.100
→ l'IP doit maintenant être visible sur enp0s8 de lb2.

4. Vérifier le service applicatif (depuis le client Windows)
powershell
curl.exe http://192.168.56.100/health
→ doit renvoyer {"status":"ok"}.

5. Retour à la normale (sur lb1)
bash
sudo systemctl start keepalived
→ lb1 reprend l'IP grâce à sa priorité supérieure (101).

